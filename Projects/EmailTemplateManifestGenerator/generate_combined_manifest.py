"""
SYNOPSIS
    Generates the PnP provisioning XML manifest for the bs one QM combined
    (bilingual, DE / EN) email templates - one <pnp:File> entry per template,
    pointing at Files/Combined/<TemplateName>.html.

DESCRIPTION
    The two original manifests (bsone-QM-EmailTemplates-ContentEN.xml and
    ContentDE.xml) each list one <pnp:File> entry per language per template,
    with a single-language bsoneSubject and a bsoneLanguage taxonomy field.
    Now that every notification type is a single combined bilingual HTML file
    (see the EmailTemplateGenerator project), those two manifests no longer
    describe reality on their own, so this script produces a third manifest
    for the combined set - by PARSING THOSE TWO FILES DIRECTLY at runtime:
        - Src                       -> .\\Files\\Combined\\<Title>.html
        - Title                      -> unchanged, matched between the two
                                         source manifests
        - bsoneSubject               -> "<German subject> / <English subject>"
                                         (German first, matching the body's
                                         DE-then-EN order)
        - bsoneLanguage              -> dropped entirely - the item is no
                                         longer single-language
        - bsonePowerAutomateDetails  -> kept where either source manifest had
                                         it; combined "DE / EN" when the two
                                         languages' text actually differs,
                                         left as a single value when identical
                                         (e.g. the {Initiator} placeholder)

    Deliberately does NOT hard-code or duplicate any subject text anywhere in
    this script. Every subject/PowerAutomateDetails value is read straight
    from ContentEN.xml / ContentDE.xml each time this runs, so when someone
    adds or edits a template in those two manifests (the normal, existing
    workflow), re-running this script alone picks it up - no script changes
    ever needed for new or changed subjects. A Title present in only one of
    the two source files is skipped with a warning (both languages needed
    for a combined bilingual entry).

    The old ContentEN.xml / ContentDE.xml are left untouched - this writes a
    separate, additional file.

EXAMPLE
    python generate_combined_manifest.py
    python generate_combined_manifest.py --xml-path "C:/some/other/manifest.xml"
    python generate_combined_manifest.py --en-path "C:/.../ContentEN.xml" --de-path "C:/.../ContentDE.xml"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-09-07
    Modified by :
    Modified on :
    Version     : 2.0.0
"""

import argparse
import logging
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"generate_combined_manifest_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

EMAIL_TEMPLATES_ROOT = (
    r"C:\Ruchik\BSTFS\bsone.deployment.qm\2_Packages\QM\ProvisioningTemplates\EmailTemplates"
)
DEFAULT_EN_PATH = EMAIL_TEMPLATES_ROOT + r"\bsone-QM-EmailTemplates-ContentEN.xml"
DEFAULT_DE_PATH = EMAIL_TEMPLATES_ROOT + r"\bsone-QM-EmailTemplates-ContentDE.xml"
DEFAULT_XML_PATH = EMAIL_TEMPLATES_ROOT + r"\bsone-QM-EmailTemplates-ContentCombined.xml"

PNP_NS = "http://schemas.dev.office.com/PnP/2020/02/ProvisioningSchema"

CORRELATION_ID = str(uuid.uuid4())[:11]
#endregion

#region Logging Setup
def check_log_directory():
    LOGS_DIRECTORY.mkdir(parents=True, exist_ok=True)


def delete_old_logs(logger):
    if PURGE_LOG_DAYS <= 0:
        return
    try:
        logger.info("Deleting log files older than %s days", PURGE_LOG_DAYS)
        cutoff = datetime.now() - timedelta(days=PURGE_LOG_DAYS)
        for log_file in LOGS_DIRECTORY.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
        logger.info("Log files deleted")
    except Exception as ex:
        logger.error("Error deleting log files. Details: %s", ex)


def get_logger():
    logger = logging.getLogger("generate_combined_manifest")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
#endregion

XML_HEADER = """<?xml version="1.0"?>
<pnp:Provisioning xmlns:pnp="http://schemas.dev.office.com/PnP/2020/02/ProvisioningSchema">
    <pnp:Preferences Generator="OfficeDevPnP.Core, Version=3.18.2002.0, Culture=neutral, PublicKeyToken=5e633289e95c321a" />
    <pnp:Templates ID="CONTAINER-TEMPLATE-BSONE">
        <pnp:ProvisioningTemplate ID="TEMPLATE-BSONE-QM-EMAILTEMPLATES" Version="1.0">
            <pnp:Files>

                <!-- bsone QM EMAIL Template - combined bilingual (DE / EN) -->
"""
XML_FOOTER = """
            </pnp:Files>
        </pnp:ProvisioningTemplate>
    </pnp:Templates>
</pnp:Provisioning>"""


def xml_escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def parse_manifest(path, logger):
    """Reads a PnP provisioning XML manifest and returns an ordered dict:
    Title -> {"subject": str, "power_automate_details": str | None}."""
    path = Path(path)
    if not path.exists():
        logger.error("Manifest not found: %s", path)
        sys.exit(1)

    tree = ET.parse(path)
    result = {}
    for file_el in tree.getroot().iter(f"{{{PNP_NS}}}File"):
        props = {
            prop.get("Key"): prop.get("Value")
            for prop in file_el.iter(f"{{{PNP_NS}}}Property")
        }
        title = props.get("Title")
        if not title:
            continue
        result[title] = {
            "subject": props.get("bsoneSubject", ""),
            "power_automate_details": props.get("bsonePowerAutomateDetails"),
        }
    logger.info("Parsed %d entries from %s", len(result), path.name)
    return result


def combine(en_entries, de_entries, logger):
    """Merges the two per-language dicts into one Title-ordered dict of
    {"subject": "<DE> / <EN>", "power_automate_details": ...}, preserving the
    EN manifest's ordering. Skips (with a warning) any Title missing from
    either side."""
    combined = {}
    for title, en_data in en_entries.items():
        de_data = de_entries.get(title)
        if de_data is None:
            logger.warning("'%s' is in the EN manifest but not the DE manifest - skipping", title)
            continue

        subject = f'{de_data["subject"]} / {en_data["subject"]}'

        pad_en = en_data["power_automate_details"]
        pad_de = de_data["power_automate_details"]
        if pad_en and pad_de:
            details = pad_en if pad_en == pad_de else f"{pad_de} / {pad_en}"
        else:
            details = pad_en or pad_de

        combined[title] = {"subject": subject, "power_automate_details": details}

    for title in de_entries:
        if title not in en_entries:
            logger.warning("'%s' is in the DE manifest but not the EN manifest - skipping", title)

    return combined


def generate_xml(combined):
    entries = []
    for title, data in combined.items():
        lines = [
            f'                <pnp:File Src=".\\Files\\Combined\\{title}.html" Folder="bsoneEmailTemplates" Overwrite="true" Level="Published">',
            '                    <pnp:Properties>',
            f'                        <pnp:Property Key="Title" Value="{xml_escape(title)}" />',
            f'                        <pnp:Property Key="bsoneSubject" Value="{xml_escape(data["subject"])}" />',
        ]
        if data["power_automate_details"]:
            lines.append(f'                        <pnp:Property Key="bsonePowerAutomateDetails" Value="{xml_escape(data["power_automate_details"])}" />')
        lines.append('                    </pnp:Properties>')
        lines.append('                </pnp:File>')
        entries.append("\n".join(lines))

    return XML_HEADER + "\n\n".join(entries) + XML_FOOTER + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate the combined bs one QM email template PnP manifest.")
    parser.add_argument("--en-path", default=DEFAULT_EN_PATH, help="Path to the source ContentEN.xml (default: %(default)s)")
    parser.add_argument("--de-path", default=DEFAULT_DE_PATH, help="Path to the source ContentDE.xml (default: %(default)s)")
    parser.add_argument("--xml-path", default=DEFAULT_XML_PATH,
                         help="Path to write the combined PnP provisioning XML manifest to (default: %(default)s)")
    return parser.parse_args()


def main_process(args, logger):
    en_entries = parse_manifest(args.en_path, logger)
    de_entries = parse_manifest(args.de_path, logger)
    combined = combine(en_entries, de_entries, logger)

    with_details = sum(1 for data in combined.values() if data["power_automate_details"])

    xml_path = Path(args.xml_path)
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    xml_path.write_text(generate_xml(combined), encoding="utf-8")

    logger.info("Wrote combined XML manifest (%d entries, %d with PowerAutomateDetails) to %s",
                len(combined), with_details, xml_path)


def main():
    args = parse_args()
    check_log_directory()
    logger = get_logger()

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        delete_old_logs(logger)
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, CORRELATION_ID)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, CORRELATION_ID)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, CORRELATION_ID, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
