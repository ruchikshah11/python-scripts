"""
SYNOPSIS
    Generates the bs one QM bilingual (German + English) email notification
    templates - one HTML file per notification type, matching the approved
    design (right-aligned "bs one: quality" header, white card with a
    German block, a divider, then an English block, and a bilingual footer).

DESCRIPTION
    The original PnP-provisioned HTML files under bsone.deployment.qm's
    ProvisioningTemplates/EmailTemplates/Files/English and .../German folders
    ship with no body content at all (just a <title>, no markup) - only the
    email subject lines exist, in the two PnP provisioning XML manifests
    (bsone-QM-EmailTemplates-ContentEN.xml / ContentDE.xml).

    This script hard-codes, per template, the subject lines (copied from
    those XML manifests) and hand-authored DE/EN body copy (drafted from the
    template's name and subject line, since no source body copy exists), and
    renders each one through a single shared HTML shell so every output file
    is visually consistent.

    Output is written to Files/Combined/<TemplateName>.html - one combined
    bilingual file per notification type (not separate EN/DE files).

    IMPORTANT: the HTML shell (SHELL) is the approved design - do not restructure
    it (table layout, header/card/divider/footer) without explicit sign-off.
    Only the TEMPLATES data (subjects/body copy) is meant to be edited freely.

EXAMPLE
    python generate_email_templates.py
    python generate_email_templates.py --out-dir "C:/some/other/folder"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-09-07
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import logging
import re
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"generate_email_templates_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7
DEFAULT_OUT_DIR = (
    r"C:\Ruchik\BSTFS\bsone.deployment.qm\2_Packages\QM\ProvisioningTemplates"
    r"\EmailTemplates\Files\Combined"
)

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
    logger = logging.getLogger("generate_email_templates")
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

#region HTML Shell (approved design - do not restructure)
SHELL = """<html xmlns:mso="urn:schemas-microsoft-com:office:office" xmlns:msdt="uuid:C2F41010-65B3-11d1-A29F-00AA00C14882"><head>
<title>{title}</title></head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Calibri,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5;border:1px solid #000000;">
<tr>
<td style="padding:20px 24px 10px 24px;text-align:right;">
<span style="font-weight:bold;font-size:14px;color:#000000;">bs one: quality</span>
</td>
</tr>
<tr>
<td style="padding:0 24px 20px 24px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#ffffff;">
<tr>
<td style="padding:28px 30px 18px 30px;font-size:14px;color:#000000;line-height:1.7;font-family:Calibri,Arial,sans-serif;">
<p style="margin:0 0 14px 0;">Guten Tag,</p>
{de_body}
<p style="margin:16px 0 0 0;">Vielen Dank</p>
</td>
</tr>
<tr>
<td style="padding:0 30px;">
<hr style="border:none;border-top:1px solid #cccccc;margin:8px 0;" />
</td>
</tr>
<tr>
<td style="padding:18px 30px 28px 30px;font-size:14px;color:#000000;line-height:1.7;font-family:Calibri,Arial,sans-serif;">
<p style="margin:0 0 14px 0;">Good Day,</p>
{en_body}
<p style="margin:16px 0 0 0;">Thank you</p>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="padding:0 24px 4px 24px;font-size:11px;color:#888888;line-height:1.6;font-family:Calibri,Arial,sans-serif;">
<p style="margin:0;">Dies ist eine automatisch generierte E-Mail, bitte antworten Sie nicht auf sie.<br/>
This is an automatically generated email, please do not reply to it.</p>
<p style="margin:10px 0 0 0;">Diese E-Mail enth&auml;lt einen sicheren Link. Geben Sie diese E-Mail nicht an andere Personen weiter.<br/>
This email contains a secure link. Do not forward this email to others.</p>
</td>
</tr>
<tr>
<td style="padding:6px 24px 20px 24px;font-size:11px;color:#888888;font-family:Calibri,Arial,sans-serif;">
Powered by <b>bs one</b>
</td>
</tr>
</table>
</body></html>
"""

LINK_STYLE = "color:#0000CC;font-weight:bold;text-decoration:underline;"
#endregion

#region HTML Indentation (post-processing - runs once per file, right before it's written)
# Only these structural tags affect nesting depth; inline/text-level tags (p, a, b, span,
# title, hr, br) are left flat on their own line so body copy stays easy to read/edit.
BLOCK_TAGS = {"html", "head", "body", "table", "tr", "td"}
TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)([^>]*?)(/?)>")


def indent_html(html, indent_unit="  "):
    """Re-indents already-one-element-per-line HTML by tracking BLOCK_TAGS nesting
    depth - a line starting with a closing tag dedents before it's printed; any
    other line's net block-tag open/close count adjusts the depth for what follows.
    Whitespace-only - never touches the tags/attributes themselves."""
    depth = 0
    out_lines = []
    for raw_line in html.split("\n"):
        line = raw_line.strip()
        if not line:
            out_lines.append("")
            continue

        dedent_first = line.startswith("</")
        if dedent_first:
            depth = max(0, depth - 1)

        out_lines.append(indent_unit * depth + line)

        if not dedent_first:
            delta = 0
            for closing, tag, _attrs, self_close in TAG_RE.findall(line):
                if self_close or tag.lower() not in BLOCK_TAGS:
                    continue
                delta += -1 if closing else 1
            depth = max(0, depth + delta)

    return "\n".join(out_lines)
#endregion

#region Body Content Helpers


def link(text):
    return '<a href="#" style="%s">%s</a>' % (LINK_STYLE, text)


DOC_LINK = link("[DocumentName] ([DocumentNumber])")
PROC_LINK = link("[ProcessName] ([ProcessNumber])")


def p(text):
    return '<p style="margin:0 0 10px 0;">%s</p>' % text


def field(label, value):
    return '<p style="margin:0 0 4px 0;">%s: %s</p>' % (label, value)


def join(*parts):
    """Join body paragraph/field fragments with newlines so the generated
    HTML stays one element per line instead of one giant concatenated line."""
    return "\n".join(parts)


# entity forms: en (lowercase noun), de nominative/accusative/genitive w/ article
DOC = dict(link_en=DOC_LINK, link_de=DOC_LINK, en="document", en_cap="Document", de_cap="Dokument",
           de_nom="das Dokument", de_acc="das Dokument", de_gen="des Dokuments", de_bare="Dokument")
PROC = dict(link_en=PROC_LINK, link_de=PROC_LINK, en="process", en_cap="Process", de_cap="Prozess",
            de_nom="der Prozess", de_acc="den Prozess", de_gen="des Prozesses", de_bare="Prozess")


def body_task_approval(e, note_en=None, note_de=None, kind="technical"):
    verbs = {
        "technical": ("A technical review is required for the", "F&uuml;r %s ist eine fachliche Pr&uuml;fung erforderlich."),
        "qm": ("A QM check is required for the", "F&uuml;r %s ist eine QM-Pr&uuml;fung erforderlich."),
        "release": ("Approval is required for the release of the", "F&uuml;r die Freigabe von %s ist eine Genehmigung erforderlich."),
    }
    en_lead, de_lead = verbs[kind]
    en_parts = [p("%s %s %s. Please review it and take the necessary action using the secure link above." % (en_lead, e["en"], e["link_en"]))]
    de_parts = [p((de_lead % ("%s %s" % (e["de_acc"], e["link_de"]))) + " Bitte pr&uuml;fen Sie und f&uuml;hren Sie die erforderliche Aktion &uuml;ber den obigen Link aus.")]
    en_parts.append(field("Initiator", "[InitiatorName]"))
    de_parts.append(field("Initiator", "[InitiatorName]"))
    if note_en:
        en_parts.append(p(note_en))
        de_parts.append(p(note_de))
    return join(*en_parts), join(*de_parts)


def body_reminder(e, kind="pending"):
    if kind == "pending":
        en = p("This is a reminder that the review and approval of the %s %s is still pending. Please take the necessary action as soon as possible." % (e["en"], e["link_en"]))
        de = p("Dies ist eine Erinnerung, dass die Pr&uuml;fung und Genehmigung %s %s noch aussteht. Bitte f&uuml;hren Sie die erforderliche Aktion so bald wie m&ouml;glich aus." % (e["de_gen"], e["link_de"]))
    else:
        en = p("The approval for the review of the %s %s is overdue. Please take the necessary action as soon as possible." % (e["en"], e["link_en"]))
        de = p("Die Genehmigung f&uuml;r die &Uuml;berpr&uuml;fung %s %s ist &uuml;berf&auml;llig. Bitte f&uuml;hren Sie die erforderliche Aktion so bald wie m&ouml;glich aus." % (e["de_gen"], e["link_de"]))
    return en, de


def body_notify_approved(e):
    en = p("The %s %s has been approved." % (e["en"], e["link_en"]))
    de = p("%s %s wurde genehmigt." % (e["de_cap"], e["link_de"]))
    return en, de


def body_notify_corrections(e):
    en = p("Feedback has been provided on the review of the %s %s. Please review the comments and make the necessary corrections." % (e["en"], e["link_en"]))
    de = p("Es liegt eine R&uuml;ckmeldung zur Pr&uuml;fung %s %s vor. Bitte pr&uuml;fen Sie die Kommentare und nehmen Sie die erforderlichen Korrekturen vor." % (e["de_gen"], e["link_de"]))
    return en, de


def body_review_task(e):
    en_parts = [
        p("The review of the %s %s has been initiated." % (e["en"], e["link_en"])),
        field("Reviewer", "[ReviewerName]"),
        field("Review date", "[RevisionDate]"),
    ]
    de_parts = [
        p("Die &Uuml;berpr&uuml;fung %s %s wurde eingeleitet." % (e["de_gen"], e["link_de"])),
        field("Pr&uuml;fer", "[ReviewerName]"),
        field("&Uuml;berpr&uuml;fungsdatum", "[RevisionDate]"),
    ]
    return join(*en_parts), join(*de_parts)


def body_review_notify_qm(e):
    en = p("The review of the %s %s has been initiated." % (e["en"], e["link_en"]))
    de = p("Die Pr&uuml;fung %s %s wurde eingeleitet." % (e["de_gen"], e["link_de"]))
    return en, de


def body_review_notify_revision(e):
    en = p("A revision has been requested for the %s %s. Please review the feedback provided and update the %s accordingly." % (e["en"], e["link_en"], e["en"]))
    de = p("F&uuml;r %s %s wurde eine &Uuml;berarbeitung angefordert. Bitte pr&uuml;fen Sie das Feedback und aktualisieren Sie %s entsprechend." % (e["de_acc"], e["link_de"], e["de_acc"]))
    return en, de


def body_responsible_change_task(e):
    en = p("You have been assigned as Responsible for the %s %s. Please accept or decline this responsibility using the secure link above." % (e["en"], e["link_en"]))
    de = p("Sie wurden als Verantwortlicher f&uuml;r %s %s vorgesehen. Bitte nehmen Sie diese Verantwortung &uuml;ber den obigen Link an oder lehnen Sie sie ab." % (e["de_acc"], e["link_de"]))
    return en, de


def body_responsible_change_notify(e, accepted):
    if accepted:
        en = p("Responsible '[ResponsibleName]' has accepted responsibility for the %s %s." % (e["en"], e["link_en"]))
        de = p("Verantwortlicher '[ResponsibleName]' hat die Verantwortung f&uuml;r %s %s &uuml;bernommen." % (e["de_acc"], e["link_de"]))
    else:
        en = p("Responsible '[ResponsibleName]' has declined responsibility for the %s %s." % (e["en"], e["link_en"]))
        de = p("Verantwortlicher '[ResponsibleName]' hat die Verantwortung f&uuml;r %s %s abgelehnt." % (e["de_acc"], e["link_de"]))
    return en, de


def body_responsible_missing(e):
    en = p("No responsible user could be found for the %s %s. Please assign a responsible user as soon as possible." % (e["en"], e["link_en"]))
    de = p("F&uuml;r %s %s konnte kein Verantwortlicher gefunden werden. Bitte weisen Sie so schnell wie m&ouml;glich einen Verantwortlichen zu." % (e["de_acc"], e["link_de"]))
    return en, de


def body_responsible_disabled(e):
    en = p("The responsible user assigned to the %s %s is disabled. Please assign a new responsible user." % (e["en"], e["link_en"]))
    de = p("Der f&uuml;r %s %s zugewiesene Verantwortliche ist deaktiviert. Bitte weisen Sie einen neuen Verantwortlichen zu." % (e["de_acc"], e["link_de"]))
    return en, de


def body_responsible_email_missing(e):
    en = p("The responsible user assigned to the %s %s has no email address on file. Please update the user's profile or assign a new responsible user." % (e["en"], e["link_en"]))
    de = p("Der f&uuml;r %s %s zugewiesene Verantwortliche hat keine hinterlegte E-Mail-Adresse. Bitte aktualisieren Sie das Benutzerprofil oder weisen Sie einen neuen Verantwortlichen zu." % (e["de_acc"], e["link_de"]))
    return en, de


def body_verify_users(entity_pl_en, entity_pl_de):
    en = p("Please find below a summary of users who are missing, disabled, or deleted across %s. Please review and update the assignments as needed." % entity_pl_en)
    de = p("Nachfolgend finden Sie eine Zusammenfassung der fehlenden, deaktivierten oder gel&ouml;schten Benutzer in %s. Bitte pr&uuml;fen Sie die Zuordnungen und aktualisieren Sie diese bei Bedarf." % entity_pl_de)
    return en, de


def body_archival_task(e):
    en_parts = [
        p("Approval is required for the archival of the %s %s. Please review and approve using the secure link above." % (e["en"], e["link_en"])),
        field("Initiator", "[InitiatorName]"),
    ]
    de_parts = [
        p("F&uuml;r die Archivierung %s %s ist eine Genehmigung erforderlich. Bitte pr&uuml;fen und genehmigen Sie &uuml;ber den obigen Link." % (e["de_gen"], e["link_de"])),
        field("Initiator", "[InitiatorName]"),
    ]
    return join(*en_parts), join(*de_parts)


def body_archival_notify(e, approved):
    if approved:
        en = p("The archival of the %s %s has been approved." % (e["en"], e["link_en"]))
        de = p("Die Archivierung %s %s wurde genehmigt." % (e["de_gen"], e["link_de"]))
    else:
        en = p("The archival of the %s %s has been rejected." % (e["en"], e["link_en"]))
        de = p("Die Archivierung %s %s wurde abgelehnt." % (e["de_gen"], e["link_de"]))
    return en, de


def body_deletion_task(e):
    en_parts = [
        p("Approval is required for the deletion of the %s %s. Please review and approve using the secure link above." % (e["en"], e["link_en"])),
        field("Initiator", "[InitiatorName]"),
    ]
    de_parts = [
        p("F&uuml;r die L&ouml;schung %s %s ist eine Genehmigung erforderlich. Bitte pr&uuml;fen und genehmigen Sie &uuml;ber den obigen Link." % (e["de_gen"], e["link_de"])),
        field("Initiator", "[InitiatorName]"),
    ]
    return join(*en_parts), join(*de_parts)


def body_deletion_notify(e, approved):
    if approved:
        en = p("The deletion of the %s %s has been approved." % (e["en"], e["link_en"]))
        de = p("Die L&ouml;schung %s %s wurde genehmigt." % (e["de_gen"], e["link_de"]))
    else:
        en = p("The deletion of the %s %s has been rejected." % (e["en"], e["link_en"]))
        de = p("Die L&ouml;schung %s %s wurde abgelehnt." % (e["de_gen"], e["link_de"]))
    return en, de


def body_draft_notify(e):
    en = p("The %s %s has been set to Draft status." % (e["en"], e["link_en"]))
    de = p("Der Prozess %s wurde auf den Status Entwurf gesetzt." % e["link_de"])
    return en, de


def body_docs_pending(e):
    en = p("Approval is pending for one or more documents related to the process %s. Please review the pending documents using the secure link above." % e["link_en"])
    de = p("F&uuml;r ein oder mehrere Dokumente im Zusammenhang mit dem Prozess %s steht eine Genehmigung noch aus. Bitte pr&uuml;fen Sie die ausstehenden Dokumente &uuml;ber den obigen Link." % e["link_de"])
    return en, de


def body_instruction_read(e, de_noun, quiz=False, training=False):
    kind_en = "training instructions" if training else "instructions"
    kind_de = "Schulungsanweisungen" if training else "Anweisungen"
    en = p("Please read the %s described in the %s %s%s." % (kind_en, e["en"], e["link_en"], " and complete the related quiz" if quiz else ""))
    de = p("Bitte lesen Sie die im %s %s beschriebenen %s%s." % (de_noun, e["link_de"], kind_de, " und schlie&szlig;en Sie das zugeh&ouml;rige Quiz ab" if quiz else ""))
    return en, de


def body_instruction_reminder(e, de_noun, overdue=False):
    if overdue:
        en = p("The request to read the instructions described in the %s %s is overdue. Please complete this as soon as possible." % (e["en"], e["link_en"]))
        de = p("Die Anforderung, die im %s %s beschriebenen Anweisungen zu lesen, ist &uuml;berf&auml;llig. Bitte erledigen Sie dies so bald wie m&ouml;glich." % (de_noun, e["link_de"]))
    else:
        en = p("This is a reminder to read the instructions described in the %s %s." % (e["en"], e["link_en"]))
        de = p("Dies ist eine Erinnerung, die im %s %s beschriebenen Anweisungen zu lesen." % (de_noun, e["link_de"]))
    return en, de


def body_instruction_task(e):
    en = p("A reading request has been assigned to you: [TaskTitle]. Please read the instructions using the secure link above.")
    de = p("Ihnen wurde eine Leseaufforderung zugewiesen: [TaskTitle]. Bitte lesen Sie die Anweisungen &uuml;ber den obigen Link.")
    return en, de


def body_measure_reminder(kind, effectiveness=False):
    subj_en = "effectiveness test" if effectiveness else "task"
    subj_de = "Wirksamkeitspr&uuml;fung" if effectiveness else "Aufgabe"
    if kind == "upcoming":
        en = p("You have an upcoming %s: '[TaskTitle]', due on [DueDate]." % subj_en)
        de = p("Sie haben eine bevorstehende %s: '[TaskTitle]', f&auml;llig am [DueDate]." % subj_de)
    elif kind == "duetoday":
        en = p("You have a %s that is due today: '[TaskTitle]'." % subj_en)
        de = p("Sie haben eine %s, die heute f&auml;llig ist: '[TaskTitle]'." % subj_de)
    elif kind == "overdue":
        en = p("You have an overdue %s: '[TaskTitle]', which was due on [DueDate]. Please complete it as soon as possible." % subj_en)
        de = p("Sie haben eine versp&auml;tete %s: '[TaskTitle]', f&auml;llig am [DueDate]. Bitte schlie&szlig;en Sie diese so bald wie m&ouml;glich ab." % subj_de)
    elif kind == "escalation":
        en = p("The %s '[TaskTitle]' is overdue and has been escalated. Please follow up as soon as possible." % subj_en)
        de = p("Die %s '[TaskTitle]' ist &uuml;berf&auml;llig und wurde eskaliert. Bitte k&uuml;mmern Sie sich so bald wie m&ouml;glich darum." % subj_de)
    return en, de


def body_measure_completed():
    en = p("The task '[TaskTitle]' has been completed.")
    de = p("Die Aufgabe '[TaskTitle]' wurde abgeschlossen.")
    return en, de


def body_measure_duedate_change():
    en = p("The due date for the task '[TaskTitle]' has been changed to [DueDate].")
    de = p("Der Termin f&uuml;r die Aufgabe '[TaskTitle]' wurde auf [DueDate] ge&auml;ndert.")
    return en, de


def body_measure_assigned():
    en = p("A new task has been assigned to you: '[TaskTitle]'.")
    de = p("Ihnen wurde eine neue Aufgabe zugewiesen: '[TaskTitle]'.")
    return en, de
#endregion

#region Template Data (81 entries - subjects copied from the PnP XML manifests)
TEMPLATES = {}

TEMPLATES["bsoneQMDocumentApprovalTaskResponsible"] = dict(
    subject_en="Technical review required for document - [DocumentName] ([DocumentNumber])",
    subject_de="Fachliche Pr\u00fcfung f\u00fcr das Dokument erforderlich -  [DocumentName] ([DocumentNumber])",
    body=body_task_approval(DOC, kind="technical"))

TEMPLATES["bsoneQMDocumentApprovalReminderResponsible"] = dict(
    subject_en="Reminder for pending document review and approval - [DocumentName] ([DocumentNumber])",
    subject_de="Erinnerung f\u00fcr ausstehende Pr\u00fcfung und Genehmigung des Dokuments - [DocumentName] ([DocumentNumber])",
    body=body_reminder(DOC, "pending"))

TEMPLATES["bsoneQMDocumentApprovalNotifyCorrections"] = dict(
    subject_en="Feedback on [DocumentName] ([DocumentNumber]) Review",
    subject_de="R\u00fcckmeldung zu [DocumentName] ([DocumentNumber]) Bewertung",
    body=body_notify_corrections(DOC))

TEMPLATES["bsoneQMDocumentApprovalTaskApprovers"] = dict(
    subject_en="QM check required for the document - [DocumentName] ([DocumentNumber])",
    subject_de="QM Pr\u00fcfung f\u00fcr den Dokument erforderlich - [DocumentName] ([DocumentNumber])",
    body=body_task_approval(DOC, kind="qm"))

TEMPLATES["bsoneQMDocumentApprovalTaskGL"] = dict(
    subject_en="Approval required for document release - [DocumentName] ([DocumentNumber])",
    subject_de="Erforderliche Genehmigung f\u00fcr die Freigabe des Dokuments - [DocumentName] ([DocumentNumber])",
    body=body_task_approval(DOC, kind="release"))

TEMPLATES["bsoneQMDocumentApprovalReminderApprovers"] = dict(
    subject_en="Document Pending Review and Approval Reminder - [DocumentName] ([DocumentNumber])",
    subject_de="Erinnerung an die ausstehende Pr\u00fcfung und Genehmigung des Dokuments - [DocumentName] ([DocumentNumber])",
    body=body_reminder(DOC, "pending"))

TEMPLATES["bsoneQMDocumentApprovalNotifyApproved"] = dict(
    subject_en="Document [DocumentName] ([DocumentNumber]) is Approved",
    subject_de="Dokument [DocumentName] ([DocumentNumber]) ist genehmigt",
    body=body_notify_approved(DOC))

TEMPLATES["bsoneQMProcessApprovalTaskResponsible"] = dict(
    subject_en="Approval required for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erforderliche fachliche Pr\u00fcfung f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_task_approval(PROC, kind="technical"))

TEMPLATES["bsoneQMProcessApprovalTaskApprovers"] = dict(
    subject_en="QM check required for process - [ProcessName] ([ProcessNumber])",
    subject_de="QM Pr\u00fcfung f\u00fcr den Prozess erforderlich - [ProcessName] ([ProcessNumber])",
    body=body_task_approval(PROC, kind="qm",
                             note_en="Please make sure that all documents related to the current process are approved.",
                             note_de="Bitte stellen Sie sicher, dass alle Dokumente im Zusammenhang mit dem aktuellen Prozess genehmigt sind."))

TEMPLATES["bsoneQMProcessApprovalReminderApprovers"] = dict(
    subject_en="Reminder for the pending Approval of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung zur ausstehenden Genehmigung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_reminder(PROC, "pending"))

TEMPLATES["bsoneQMProcessApprovalReminderResponsible"] = dict(
    subject_en="Reminder for the pending Approval of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung zur ausstehenden Genehmigung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_reminder(PROC, "pending"))

TEMPLATES["bsoneQMProcessApprovalTaskGL"] = dict(
    subject_en="Approval required for the release of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Genehmigung erforderlich f\u00fcr die Freigabe des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_task_approval(PROC, kind="release"))

TEMPLATES["bsoneQMProcessApprovalReminderGL"] = dict(
    subject_en="Reminder for the pending Approval of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung zur ausstehenden Genehmigung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_reminder(PROC, "pending"))

TEMPLATES["bsoneQMProcessApprovalNotifyApproved"] = dict(
    subject_en="Process [ProcessName] ([ProcessNumber]) is Approved",
    subject_de="Prozess [ProcessName] ([ProcessNumber]) ist genehmigt",
    body=body_notify_approved(PROC))

TEMPLATES["bsoneQMProcessReviewTask"] = dict(
    subject_en="Review required for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="F\u00fcr den Prozess erforderliche \u00dcberpr\u00fcfung - [ProcessName] ([ProcessNumber])",
    body=body_review_task(PROC))

TEMPLATES["bsoneQMDocumentReviewReminderOwner"] = dict(
    subject_en="Reminder for the pending Review of the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Erinnerung zur ausstehenden \u00dcberpr\u00fcfung des Dokuments - [DocumentName] ([DocumentNumber])",
    body=body_reminder(DOC, "pending"))

TEMPLATES["bsoneQMDocumentReviewReminderApprovers"] = dict(
    subject_en="Approval for the review of the Document - [DocumentName] ([DocumentNumber]) is overdue",
    subject_de="Genehmigung f\u00fcr die \u00dcberpr\u00fcfung des Dokuments - [DocumentName] ([DocumentNumber]) ist \u00fcberf\u00e4llig",
    body=body_reminder(DOC, "overdue"))

TEMPLATES["bsoneQMProcessReviewReminderOwner"] = dict(
    subject_en="Reminder for the pending Review of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung zur ausstehenden \u00dcberpr\u00fcfung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_reminder(PROC, "pending"))

TEMPLATES["bsoneQMProcessReviewReminderApprovers"] = dict(
    subject_en="Approval for the review of the Process [ProcessName] ([ProcessNumber]) is overdue",
    subject_de="Genehmigung f\u00fcr die \u00dcberpr\u00fcfung des Prozesses [ProcessName] ([ProcessNumber]) ist \u00fcberf\u00e4llig",
    body=body_reminder(PROC, "overdue"))

TEMPLATES["bsoneQMDocumentReviewTask"] = dict(
    subject_en="Review required for the Document - [DocumentName] ([DocumentNumber])",
    subject_de="\u00dcberpr\u00fcfung f\u00fcr das Dokument erforderlich - [DocumentName] ([DocumentNumber])",
    body=body_review_task(DOC))

TEMPLATES["bsoneQMDocumentVerifyUsers"] = dict(
    subject_en="[Action Required] Summary of Missing or Disabled/Deleted Users in Process Documents",
    subject_de="[Erforderliche Ma\u00dfnahme]  Zusammenfassung der fehlenden oder deaktivierten/gel\u00f6schten Benutzer in Prozessdokumenten.",
    body=body_verify_users("process documents", "Prozessdokumenten"))

TEMPLATES["bsoneQMDocumentResponsibleExist"] = dict(
    subject_en="Responsible does not exist for the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr das Dokument - [DocumentName] ([DocumentNumber])",
    body=body_responsible_missing(DOC))

TEMPLATES["bsoneQMProcessVerifyUsers"] = dict(
    subject_en="[Action Required] Summary of Missing or Disabled/Deleted Users in Processes",
    subject_de="[Erforderliche Ma\u00dfnahme] Zusammenfassung der fehlenden oder deativierten/gel\u00f6schten Benutzer in Prozessen.",
    body=body_verify_users("processes", "Prozessen"))

TEMPLATES["bsoneQMProcessResponsibleExist"] = dict(
    subject_en="Responsible does not exist for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_responsible_missing(PROC))

TEMPLATES["bsoneQMDocumentResponsibleMissing"] = dict(
    subject_en="Responsible does not exist for the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr das Dokument  - [DocumentName] ([DocumentNumber])",
    body=body_responsible_missing(DOC))

TEMPLATES["bsoneQMDocumentResponsibleChangeTask"] = dict(
    subject_en="You have been assigned as Responsible of the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Sie wurden als Verantwortlicher f\u00fcr das Dokument - [DocumentName] ([DocumentNumber])",
    body=body_responsible_change_task(DOC))

TEMPLATES["bsoneQMDocumentResponsibleChangeNotifyRejected"] = dict(
    subject_en="Responsible '[ResponsibleName]' has declined responsibilities of the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Verantwortlicher '[ResponsibleName]' hat die Verantwortung f\u00fcr das Dokument abgelehnt - [DocumentName] ([DocumentNumber])",
    body=body_responsible_change_notify(DOC, accepted=False))

TEMPLATES["bsoneQMDocumentResponsibleChangeNotifyApproved"] = dict(
    subject_en="Responsible '[ResponsibleName]' has accepted responsibilities of the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Verantwortlicher '[ResponsibleName]' hat die Verantwortung f\u00fcr das Dokument \u00fcbernommen - [DocumentName] ([DocumentNumber])",
    body=body_responsible_change_notify(DOC, accepted=True))

TEMPLATES["bsoneQMProcessResponsibleMissing"] = dict(
    subject_en="Responsible does not exist for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_responsible_missing(PROC))

TEMPLATES["bsoneQMProcessApprovalNotifyCorrectionsAuthors"] = dict(
    subject_en="Feedback on [ProcessName] ([ProcessNumber]) Review",
    subject_de="R\u00fcckmeldung zu [ProcessName] ([ProcessNumber]) Bewertung",
    body=body_notify_corrections(PROC))

TEMPLATES["bsoneQMProcessApprovalNotifyCorrectionsApprovers"] = dict(
    subject_en="Feedback on [ProcessName] ([ProcessNumber]) Review",
    subject_de="R\u00fcckmeldung zu [ProcessName] ([ProcessNumber]) Bewertung",
    body=body_notify_corrections(PROC))

TEMPLATES["bsoneQMProcessResponsibleChangeTask"] = dict(
    subject_en="You have been assigned as Responsible of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Sie wurden als Verantwortlicher f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_responsible_change_task(PROC))

TEMPLATES["bsoneQMProcessResponsibleChangeNotifyRejected"] = dict(
    subject_en="Responsible '[ResponsibleName]' has declined responsibilities of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Verantwortlicher '[ResponsibleName]' hat die Verantwortung f\u00fcr den Prozess abgelehnt - [ProcessName] ([ProcessNumber])",
    body=body_responsible_change_notify(PROC, accepted=False))

TEMPLATES["bsoneQMProcessResponsibleChangeNotifyApproved"] = dict(
    subject_en="Responsible '[ResponsibleName]' has accepted responsibilities of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Verantwortlicher '[ResponsibleName]' hat die Verantwortung f\u00fcr den Prozess \u00fcbernommen - [ProcessName] ([ProcessNumber])",
    body=body_responsible_change_notify(PROC, accepted=True))

TEMPLATES["bsoneQMDocumentResponsibleDisabled"] = dict(
    subject_en="Responsible does not exist for the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr das Dokument - [DocumentName] ([DocumentNumber])",
    body=body_responsible_disabled(DOC))

TEMPLATES["bsoneQMDocumentResponsibleEmailMissing"] = dict(
    subject_en="Responsible Email does not exist for the Document - [DocumentName] ([DocumentNumber])",
    subject_de="Zust\u00e4ndige E-Mail existiert nicht f\u00fcr das Dokument - [DocumentName] ([DocumentNumber])",
    body=body_responsible_email_missing(DOC))

TEMPLATES["bsoneQMProcessResponsibleDisabled"] = dict(
    subject_en="Responsible does not exist for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Verantwortlicher existiert nicht f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_responsible_disabled(PROC))

TEMPLATES["bsoneQMProcessResponsibleEmailMissing"] = dict(
    subject_en="Responsible Email does not exist for the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Zust\u00e4ndige E-Mail existiert nicht f\u00fcr den Prozess - [ProcessName] ([ProcessNumber])",
    body=body_responsible_email_missing(PROC))

TEMPLATES["bsoneQMProcessArchivalApprovalTask"] = dict(
    subject_en="Approval required for the archival of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erforderliche Genehmigung f\u00fcr die Archivierung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_archival_task(PROC))

TEMPLATES["bsoneQMProcessArchivalNotifyApproved"] = dict(
    subject_en="Archival of the Process [ProcessName] ([ProcessNumber]) is approved",
    subject_de="Die Archivierung des Prozesses [ProcessName] ([ProcessNumber]) ist genehmigt",
    body=body_archival_notify(PROC, approved=True))

TEMPLATES["bsoneQMProcessArchivalNotifyRejected"] = dict(
    subject_en="Archival of the Process [ProcessName] ([ProcessNumber]) is rejected",
    subject_de="Archivierung des Prozesses [ProcessName] ([ProcessNumber]) wird abgelehnt",
    body=body_archival_notify(PROC, approved=False))

TEMPLATES["bsoneQMProcessDeletionApprovalTask"] = dict(
    subject_en="Approval required for the Deletion of the Process - [ProcessName] ([ProcessNumber])",
    subject_de="Erforderliche Genehmigung f\u00fcr die L\u00f6schung des Prozesses - [ProcessName] ([ProcessNumber])",
    body=body_deletion_task(PROC))

TEMPLATES["bsoneQMProcessDeletionNotifyApproved"] = dict(
    subject_en="Deletion of the Process [ProcessName] ([ProcessNumber]) is approved",
    subject_de="Die L\u00f6schung des Prozesses [ProcessName] ([ProcessNumber]) wird genehmigt",
    body=body_deletion_notify(PROC, approved=True))

TEMPLATES["bsoneQMProcessDeletionNotifyRejected"] = dict(
    subject_en="Deletion of the Process [ProcessName] ([ProcessNumber]) is rejected",
    subject_de="Die L\u00f6schung des Prozesses [ProcessName] ([ProcessNumber]) wird abgelehnt",
    body=body_deletion_notify(PROC, approved=False))

TEMPLATES["bsoneQMProcessDraftNotifyOwner"] = dict(
    subject_en="The Process [ProcessName] ([ProcessNumber]) is set to Draft",
    subject_de="Der Prozess [ProcessName] ([ProcessNumber]) ist auf Entwurf eingestellt",
    body=body_draft_notify(PROC))

TEMPLATES["bsoneQMProcessDocumentsApprovalPendingNotifyQAApprovers"] = dict(
    subject_en="Approval is pending for the Documents of the Process [ProcessName] ([ProcessNumber])",
    subject_de="Die Genehmigung f\u00fcr die Dokumente des Prozesses [ProcessName] ([ProcessNumber])",
    body=body_docs_pending(PROC))

TEMPLATES["bsoneQMProcessInstructionReadNotify"] = dict(
    subject_en="Read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Lesen Sie die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber])",
    body=body_instruction_read(PROC, "Prozess"))

TEMPLATES["bsoneQMProcessInstructionReadQuizNotify"] = dict(
    subject_en="Read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Lesen Sie die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber])",
    body=body_instruction_read(PROC, "Prozess", quiz=True))

TEMPLATES["bsoneQMProcessTrainingInstructionReadNotify"] = dict(
    subject_en="Read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Lesen Sie die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber])",
    body=body_instruction_read(PROC, "Prozess", training=True))

TEMPLATES["bsoneQMProcessTrainingInstructionReadQuizNotify"] = dict(
    subject_en="Read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Lesen Sie die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber])",
    body=body_instruction_read(PROC, "Prozess", quiz=True, training=True))

TEMPLATES["bsoneQMProcessInstructionReadReminderResponsible"] = dict(
    subject_en="Reminder to read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung, die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber]) zu lesen",
    body=body_instruction_reminder(PROC, "Prozess"))

TEMPLATES["bsoneQMProcessInstructionReadReminderApprovers"] = dict(
    subject_en="Request to read the instructions for the Process [ProcessName] ([ProcessNumber]) is overdue",
    subject_de="Die Anfrage zum Lesen der Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber]) ist \u00fcberf\u00e4llig",
    body=body_instruction_reminder(PROC, "Prozess", overdue=True))

TEMPLATES["bsoneQMProcessInstructionReadQuizReminderResponsible"] = dict(
    subject_en="Reminder to read the instructions for the Process [ProcessName] ([ProcessNumber])",
    subject_de="Erinnerung, die Anweisungen f\u00fcr den Prozess [ProcessName] ([ProcessNumber]) zu lesen",
    body=body_instruction_reminder(PROC, "Prozess"))

TEMPLATES["bsoneQMDocumentInstructionReadNotify"] = dict(
    subject_en="Read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Lies die im Dokument beschriebenen Anweisungen {Document Name} ({Document Number})",
    body=body_instruction_read(DOC, "Dokument"))

TEMPLATES["bsoneQMDocumentTrainingInstructionReadNotify"] = dict(
    subject_en="Read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Lies die im Dokument beschriebenen Anweisungen {Document Name} ({Document Number})",
    body=body_instruction_read(DOC, "Dokument", training=True))

TEMPLATES["bsoneQMDocumentProcessInstructionReadNotify"] = dict(
    subject_en="Read the instructions described in the Document [DocumentName] ([DocumentNumber])",
    subject_de="Lies die im Dokument beschriebenen Anweisungen [DocumentName] ([DocumentNumber])",
    body=body_instruction_read(DOC, "Dokument"))

TEMPLATES["bsoneQMDocumentInstructionReadQuizNotify"] = dict(
    subject_en="Read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Lies die im Dokument beschriebenen Anweisungen {Document Name} ({Document Number})",
    body=body_instruction_read(DOC, "Dokument", quiz=True))

TEMPLATES["bsoneQMDocumentTrainingInstructionReadQuizNotify"] = dict(
    subject_en="Read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Lies die im Dokument beschriebenen Anweisungen {Document Name} ({Document Number})",
    body=body_instruction_read(DOC, "Dokument", quiz=True, training=True))

TEMPLATES["bsoneQMDocumentInstructionReadReminderResponsible"] = dict(
    subject_en="Reminder to read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Erinnerung, die im Dokument beschriebenen Anweisungen zu lesen {Document Name} ({Document Number})",
    body=body_instruction_reminder(DOC, "Dokument"))

TEMPLATES["bsoneQMDocumentInstructionReadQuizReminderResponsible"] = dict(
    subject_en="Reminder to read the instructions described in the Document {Document Name} ({Document Number})",
    subject_de="Erinnerung, die im Dokument beschriebenen Anweisungen zu lesen {Document Name} ({Document Number})",
    body=body_instruction_reminder(DOC, "Dokument"))

TEMPLATES["bsoneQMDocumentInstructionReadReminderApprovers"] = dict(
    subject_en="Request to read the instructions described in the Document {Document Name} ({Document Number}) is overdue",
    subject_de="Anforderung, die im Dokument beschriebenen Anweisungen zu lesen {Document Name} ({Document Number}) ist \u00fcberf\u00e4llig",
    body=body_instruction_reminder(DOC, "Dokument", overdue=True))

TEMPLATES["bsoneQMMeasureUpcomingDueReminder"] = dict(
    subject_en="You have an upcoming Task",
    subject_de="Sie haben eine bevorstehende Aufgabe",
    body=body_measure_reminder("upcoming"))

TEMPLATES["bsoneQMMeasureDueTodayReminder"] = dict(
    subject_en="You have an Task that is due today",
    subject_de="Sie haben eine Aufgabe, die heute f\u00e4llig ist",
    body=body_measure_reminder("duetoday"))

TEMPLATES["bsoneQMMeasureOverdueReminder"] = dict(
    subject_en="You have a late task",
    subject_de="Sie haben eine versp\u00e4tete Aufgabes",
    body=body_measure_reminder("overdue"))

TEMPLATES["bsoneQMMeasureEscalationReminder"] = dict(
    subject_en="A Task is Overdue",
    subject_de="Eine Aufgabe ist \u00fcberf\u00e4llig",
    body=body_measure_reminder("escalation"))

TEMPLATES["bsoneQMMeasureEffectivenessTestUpcomingDueReminder"] = dict(
    subject_en="You have an upcoming Measure effectiveness test",
    subject_de="Sie haben eine bevorstehende Wirksamkeitspr\u00fcfung f\u00fcr die Ma\u00dfnahme",
    body=body_measure_reminder("upcoming", effectiveness=True))

TEMPLATES["bsoneQMMeasureEffectivenessTestDueTodayReminder"] = dict(
    subject_en="You have a Measure effectiveness test due today",
    subject_de="Sie haben eine Wirksamkeitspr\u00fcfung f\u00fcr die Ma\u00dfnahme, die heute f\u00e4llig ist",
    body=body_measure_reminder("duetoday", effectiveness=True))

TEMPLATES["bsoneQMMeasureEffectivenessTestOverdueReminder"] = dict(
    subject_en="You have a late Measure effectiveness test",
    subject_de="Eine Wirksamkeitspr\u00fcfung ist versp\u00e4tet",
    body=body_measure_reminder("overdue", effectiveness=True))

TEMPLATES["bsoneQMMeasureEffectivenessTestEscalationReminder"] = dict(
    subject_en="A Measure effectiveness test is Overdue",
    subject_de="Eine Wirksamkeitspr\u00fcfung ist \u00fcberf\u00e4llig",
    body=body_measure_reminder("escalation", effectiveness=True))

TEMPLATES["bsoneQMMeasureCompletedNotify"] = dict(
    subject_en="Task '[TaskTitle]' has been completed",
    subject_de="Aufgabe '[TaskTitle]' wurde erledigt",
    body=body_measure_completed())

TEMPLATES["bsoneQMMeasureDueDateChangeNotify"] = dict(
    subject_en="Due Date Changed for the Task '[TaskTitle]'",
    subject_de="Der Termin f\u00fcr die Aufgabe wurde ge\u00e4ndert '[TaskTitle]'",
    body=body_measure_duedate_change())

TEMPLATES["bsoneQMMeasureNotifyAssignedTo"] = dict(
    subject_en="New Task Assigned: [TaskTitle]",
    subject_de="Neue Aufgabe zugewiesen: [TaskTitle]",
    body=body_measure_assigned())

TEMPLATES["bsoneQMDocumentInstructionReadTask"] = dict(
    subject_en="\"Reading Request for Document\" [TaskTitle]",
    subject_de="\"Leseaufforderung f\u00fcr Dokument\" [TaskTitle]",
    body=body_instruction_task(DOC))

TEMPLATES["bsoneQMProcessInstructionReadTask"] = dict(
    subject_en="\"[TaskTitle]\" Reading Request",
    subject_de="\"[TaskTitle]\" Leseaufforderung",
    body=body_instruction_task(PROC))

TEMPLATES["bsoneQMDocumentReviewNotifyRevisionAuthors"] = dict(
    subject_en="Request for Revision of the Document: [DocumentName] ([DocumentNumber])",
    subject_de="Antrag auf \u00dcberarbeitung des Dokuments: [DocumentName] ([DocumentNumber])",
    body=body_review_notify_revision(DOC))

TEMPLATES["bsoneQMProcessReviewNotifyRevisionAuthors"] = dict(
    subject_en="Request for Revision of the Process: [ProcessName] ([ProcessNumber])",
    subject_de="Antrag auf Revision des Prozesses: [ProcessName] ([ProcessNumber])",
    body=body_review_notify_revision(PROC))

TEMPLATES["bsoneQMDocumentDeletionApprovalTask"] = dict(
    subject_en="Approval required for the Deletion of the Document [DocumentName] [DocumentNumber]",
    subject_de="F\u00fcr die L\u00f6schung des Dokuments [DocumentName] [DocumentNumber] ist eine Genehmigung erforderlich.",
    body=body_deletion_task(DOC))

TEMPLATES["bsoneQMDocumentDeletionNotifyApproved"] = dict(
    subject_en="Deletion of the Document [DocumentName] [DocumentNumber] is approved",
    subject_de="Die L\u00f6schung des Dokuments [DocumentName] [DocumentNumber] wird genehmigt.",
    body=body_deletion_notify(DOC, approved=True))

TEMPLATES["bsoneQMDocumentDeletionNotifyRejected"] = dict(
    subject_en="Deletion of the Document [DocumentName] [DocumentNumber] is rejected",
    subject_de="Die L\u00f6schung des Dokuments [DocumentName] [DocumentNumber] wurde abgelehnt.",
    body=body_deletion_notify(DOC, approved=False))

TEMPLATES["bsoneQMProcessReviewNotifyQMApprovers"] = dict(
    subject_en="Process review initiated - [ProcessName] ([ProcessNumber])",
    subject_de="Prozesspr\u00fcfung eingeleitet - [ProcessName] ([ProcessNumber])",
    body=body_review_notify_qm(PROC))

TEMPLATES["bsoneQMDocumentReviewNotifyQMApprovers"] = dict(
    subject_en="Document review initiated - [DocumentName] ([DocumentNumber])",
    subject_de="Dokumentenpr\u00fcfung eingeleitet  - [DocumentName] ([DocumentNumber])",
    body=body_review_notify_qm(DOC))
#endregion


def parse_args():
    parser = argparse.ArgumentParser(description="Generate the bs one QM bilingual email templates.")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                         help="Folder to write the generated .html files into (default: %(default)s)")
    return parser.parse_args()


def main_process(args, logger):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Writing %d templates to %s", len(TEMPLATES), out_dir)

    for key, data in TEMPLATES.items():
        en_body, de_body = data["body"]
        html = SHELL.format(title=key, de_body=de_body, en_body=en_body)
        html = indent_html(html)
        out_path = out_dir / (key + ".html")
        out_path.write_text(html, encoding="utf-8")
        logger.info("Wrote %s", out_path.name)

    logger.info("Done - %d templates written", len(TEMPLATES))


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
