# Email Notifier

Sends an email notification via SMTP. Credentials are read from **environment
variables only** — never hardcoded, never passed as CLI arguments (which would leak
into shell history).

## Prerequisites
None beyond the standard library (`smtplib`, `email` are built in).

## Required environment variables
| Variable | Example |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` or `smtp.office365.com` |
| `SMTP_PORT` | `587` (STARTTLS) |
| `SMTP_USERNAME` | the account you're sending *from* |
| `SMTP_PASSWORD` | an **app password**, not your real account password |

Both Gmail and Microsoft 365 require a separate app password when 2FA is enabled —
generate one for this purpose rather than using your normal login password.

PowerShell (current session only):
```powershell
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "you@gmail.com"
$env:SMTP_PASSWORD = "your-16-char-app-password"
```

## Run it
```
python send_notification.py --to someone@example.com --subject "Job done" --body "The nightly sync finished."
python send_notification.py --to someone@example.com --subject "Report" --body-file report.txt
python send_notification.py --to a@example.com --to b@example.com --subject "Alert" --body "Multiple recipients"
```
Repeat `--to` for multiple recipients.

## Errors
- Missing any of the 4 required env vars → clear error listing exactly which are
  missing, exit code 1
- Neither `--body` nor `--body-file` given → clear error, exit code 1
- Connection/auth failures surface via `smtplib`'s exceptions, logged, exit code 1

## ⚠️ Testing limitation — please read
I do not have real SMTP credentials and cannot send an actual email to verify this
end-to-end. What I *did* verify:
- Missing-env-var detection (all 4 correctly flagged when unset)
- Missing-body detection
- Multiple `--to` values correctly parsed and joined
- With fake credentials pointed at a fake host, the script correctly proceeded all
  the way to actually calling `smtplib.SMTP()` and attempting a real connection,
  failing with a DNS resolution error — confirming the connection code path itself
  runs correctly, right up to the point where real credentials would take over.

**What's still unverified**: the actual login + send against a real mail server. Set
your real environment variables and send yourself a test email before relying on this
for anything important.

## Logging
Logs are written to `Logs/send_notification_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).
The log records the SMTP host/port/username used and recipients/subject, but never
the password or body content.

## Status
- [x] Verified: argument parsing, env var validation, multi-recipient handling,
  connection attempt against a fake host (correctly fails with DNS error)
- [ ] **Not verified: actual successful send against a real SMTP server — please
  test yourself with your real credentials**
