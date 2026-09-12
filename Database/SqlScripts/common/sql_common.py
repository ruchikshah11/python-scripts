"""
Shared SQL Server helpers used by every script under Database/SqlScripts/. Wraps
the connect/open/close boilerplate (via pyodbc) so fixes and improvements only
need to happen in one place. Python port of SqlScripts.Common.psm1.

The Server/User Id/Password/TrustServerCertificate that every script connects
with live in one place - common/SqlServerConfig.json - instead of being
repeated in every script's own config file. build_connection_string(database)
below builds the ADO.NET-style connection string
(Server=...;Database=...;User Id=...;Password=...;TrustServerCertificate=True;)
from it; _to_pyodbc_connection_string() then translates that to the ODBC keys
pyodbc expects (Uid/Pwd, Yes/No, plus a Driver=... prefix).
"""

import json
import struct
from pathlib import Path

import pyodbc

DEFAULT_DRIVER = "ODBC Driver 17 for SQL Server"
_KEY_ALIASES = {"user id": "Uid", "password": "Pwd"}
# ADO.NET writes these as True/False; the SQL Server ODBC driver only accepts Yes/No.
_YES_NO_KEYS = {"trustservercertificate", "encrypt", "multipleactiveresultsets"}

# pyodbc has no built-in decoder for SQL Server's datetimeoffset type (ODBC SQL
# type -155) - without this, any column of that type raises "ODBC SQL type -155
# is not yet supported" instead of returning a value.
# https://github.com/mkleehammer/pyodbc/issues/134
SQL_SS_TIMESTAMPOFFSET = -155

_COMMON_FOLDER = Path(__file__).resolve().parent
SHARED_SERVER_CONFIG_PATH = _COMMON_FOLDER / "SqlServerConfig.json"


def get_sql_script_config(config_path):
    """Reads a JSON config file and returns it as a dict."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_connection_string(database):
    """Builds an ADO.NET-style connection string for `database`, using the
    Server/UserId/Password/TrustServerCertificate shared by every script under
    Database/SqlScripts/ (common/SqlServerConfig.json). `database` can also be
    "{0}" as a literal placeholder for a per-tenant connection string template
    (see ExportTenantSubscriptionsToCsv)."""
    shared = get_sql_script_config(SHARED_SERVER_CONFIG_PATH)
    return (
        f"Server={shared['Server']};Database={database};"
        f"User Id={shared['UserId']};Password={shared['Password']};"
        f"TrustServerCertificate={shared['TrustServerCertificate']};"
    )


def _decode_datetimeoffset(raw_value):
    """Unpacks a datetimeoffset's raw byte value into a
    'YYYY-MM-DD HH:MM:SS.fffffff+HH:MM'-style string."""
    year, month, day, hour, minute, second, fraction, tz_hour, tz_minute = struct.unpack(
        "<6hI2h", raw_value
    )
    return (
        f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        f".{fraction:07d} {tz_hour:+03d}:{tz_minute:02d}"
    )


def _connect(connection_string):
    conn = pyodbc.connect(_to_pyodbc_connection_string(connection_string))
    conn.add_output_converter(SQL_SS_TIMESTAMPOFFSET, _decode_datetimeoffset)
    return conn


def _to_pyodbc_connection_string(connection_string, driver=DEFAULT_DRIVER):
    has_driver = False
    parts = []
    for pair in connection_string.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        key, _, value = pair.partition("=")
        key = key.strip()
        value = value.strip()
        key_lower = key.lower()
        if key_lower == "driver":
            has_driver = True
        if key_lower in _YES_NO_KEYS and value.lower() in ("true", "false"):
            value = "yes" if value.lower() == "true" else "no"
        parts.append(f"{_KEY_ALIASES.get(key_lower, key)}={value}")
    if not has_driver:
        parts.insert(0, f"Driver={{{driver}}}")
    return ";".join(parts) + ";"


def invoke_sql_non_query(connection_string, query, command_timeout=30):
    """Runs a non-query (INSERT/UPDATE/DELETE/DDL) and returns rows affected."""
    conn = _connect(connection_string)
    conn.timeout = command_timeout
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows_affected = cursor.rowcount
        conn.commit()
        return rows_affected
    finally:
        conn.close()


def invoke_sql_query(connection_string, query, command_timeout=30):
    """Runs a query and returns (columns, rows) - columns is the list of column
    names in order, rows is a list of {column_name: value} dicts."""
    conn = _connect(connection_string)
    conn.timeout = command_timeout
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return columns, rows
    finally:
        conn.close()


def bulk_insert(connection_string, table_name, rows):
    """Inserts a list of dicts (all sharing the same keys) into table_name via a
    parameterized, fast_executemany INSERT - the Python equivalent of SqlBulkCopy."""
    if not rows:
        return 0
    columns = list(rows[0].keys())
    column_list = ", ".join(f"[{c}]" for c in columns)
    placeholders = ", ".join("?" for _ in columns)
    insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
    values = [[row[c] for c in columns] for row in rows]

    conn = _connect(connection_string)
    try:
        cursor = conn.cursor()
        cursor.fast_executemany = True
        cursor.executemany(insert_sql, values)
        conn.commit()
        return len(rows)
    finally:
        conn.close()


def print_table(columns, rows):
    """Prints rows as a simple auto-sized table, similar in spirit to PowerShell's
    Format-Table -AutoSize."""
    if not rows:
        print("(no rows)")
        return
    widths = [max(len(str(col)), max(len(str(row[col])) for row in rows)) for col in columns]
    print("  ".join(str(col).ljust(width) for col, width in zip(columns, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(str(row[col]).ljust(width) for col, width in zip(columns, widths)))
