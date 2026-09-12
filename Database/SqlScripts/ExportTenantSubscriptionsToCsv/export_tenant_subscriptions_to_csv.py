"""
SYNOPSIS
    Exports Common.Tenant.Subscription rows from every tenant database into one
    CSV. Uses the sql_common library (Database/SqlScripts/common) for the SQL
    Server calls, and the shared db_logging helper (Database/SqlScripts/common) for
    logging.

DESCRIPTION
    Runs the mapping query (--mapping-query-path) against bsone_core to get every
    tenant's TenantID, CompanyName, and ConfiguredDatabaseName (the Name column
    from Server.Instance.Database, resolved via Tenant.Credential.DatabaseID).

    Multiple Tenant rows can resolve to the same physical database (several
    companies provisioned into one shared database), so this script queries each
    distinct database only once - not once per tenant row, which would read the
    same data twice under two different company labels. For each row
    Common.Tenant.Subscription returns, CompanyName is looked up from that row's
    own TenantID (via a TenantID -> CompanyName map built from the mapping query),
    not from whichever tenant happened to be current when the database was picked
    - that's what actually identifies the owner when a database is shared.

    Read-only throughout (no CREATE/INSERT/UPDATE/DELETE); both queries can use
    WITH (NOLOCK) in their .sql files so this reporting run can't block, or get
    blocked by, live production traffic.

    Tenants with no configured database, or whose database can't be reached or
    doesn't have the table, are skipped with a warning rather than aborting the
    whole export.

    Python port of Export-TenantSubscriptionsToCsv.ps1.

EXAMPLE
    python export_tenant_subscriptions_to_csv.py
    python export_tenant_subscriptions_to_csv.py --config-path SqlTenantSubscriptionExportConfig.json --mapping-query-path tenant_database_mapping.sql --subscription-query-path subscription_query.sql

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-04
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import csv
import importlib
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER.parent / "common"))

#region Module Dependency Check
REQUIRED_MODULES = ["pyodbc"]  # csv is standard library

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

import db_logging
import sql_common

SUBSCRIPTION_COLUMNS = [
    "CompanyName", "SourceDatabase", "TenantID", "SubscriptionIdentifier", "ClientState",
    "SiteUrl", "NotificationUrl", "Resource", "ExpiresOn", "ChangeToken", "IsDeleted",
    "ChangeType", "ContactID", "DBModifiedOn", "UpdateSource",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlTenantSubscriptionExportConfig.json"))
    parser.add_argument("--mapping-query-path", default=str(SCRIPT_FOLDER / "tenant_database_mapping.sql"))
    parser.add_argument("--subscription-query-path", default=str(SCRIPT_FOLDER / "subscription_query.sql"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    core_connection_string = sql_common.build_connection_string(config["Database"])
    tenant_connection_template = sql_common.build_connection_string("{0}")
    mapping_query = Path(args.mapping_query_path).read_text(encoding="utf-8")
    subscription_query = Path(args.subscription_query_path).read_text(encoding="utf-8")

    try:
        _, mapping_rows = sql_common.invoke_sql_query(core_connection_string, mapping_query)
    except Exception as ex:
        raise RuntimeError(f"Could not read the tenant/database mapping from bsone_core: {ex}") from ex

    company_name_by_tenant_id = {str(row["TenantID"]): row["CompanyName"] for row in mapping_rows}

    # Distinct configured databases, first tenant row seen per database - mirrors
    # the PowerShell version's Group-Object + take-first-of-each-group.
    database_row_by_name = {}
    for row in mapping_rows:
        database_name = row.get("ConfiguredDatabaseName")
        if not database_name or not str(database_name).strip():
            logger.warning("Tenant %s (%s) has no configured database; skipping.",
                            row["TenantID"], row["CompanyName"])
            continue
        database_row_by_name.setdefault(database_name, row)
    database_rows = list(database_row_by_name.values())

    results = []
    total_databases = len(database_rows)

    for index, row in enumerate(database_rows, start=1):
        database_name = row["ConfiguredDatabaseName"]
        logger.info("(%s of %s) Exporting %s", index, total_databases, database_name)

        tenant_connection_string = tenant_connection_template.format(database_name)

        try:
            _, subscription_rows = sql_common.invoke_sql_query(tenant_connection_string, subscription_query)
        except Exception as ex:
            logger.warning("Skipping %s (%s)", database_name, ex)
            continue

        for sub_row in subscription_rows:
            owner_tenant_id = str(sub_row["TenantID"])
            company_name = company_name_by_tenant_id.get(owner_tenant_id)
            if not company_name:
                logger.warning(
                    "Database %s has a subscription row for TenantID %s, which isn't in the bsone_core mapping.",
                    database_name, owner_tenant_id,
                )
                company_name = f"(unknown tenant {owner_tenant_id})"

            results.append({
                "CompanyName": company_name,
                "SourceDatabase": database_name,
                "TenantID": sub_row["TenantID"],
                "SubscriptionIdentifier": sub_row["SubscriptionIdentifier"],
                "ClientState": sub_row["ClientState"],
                "SiteUrl": sub_row["SiteUrl"],
                "NotificationUrl": sub_row["NotificationUrl"],
                "Resource": sub_row["Resource"],
                "ExpiresOn": sub_row["ExpiresOn"],
                "ChangeToken": sub_row["ChangeToken"],
                "IsDeleted": sub_row["IsDeleted"],
                "ChangeType": sub_row["ChangeType"],
                "ContactID": sub_row["ContactID"],
                "DBModifiedOn": sub_row["DBModifiedOn"],
                "UpdateSource": sub_row["UpdateSource"],
            })

    output_path = Path(config["OutputPath"])
    if not output_path.is_absolute():
        output_path = SCRIPT_FOLDER / output_path

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUBSCRIPTION_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    logger.info("Exported %s subscription row(s) across %s database(s) to %s",
                len(results), len(database_rows), output_path)


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "export_tenant_subscriptions_to_csv")

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, correlation_id)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, correlation_id)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, correlation_id, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
