"""
SYNOPSIS
    Lesson 12: Regular Expressions (re module) in Python - Metacharacters,
    character sets, quantifiers, anchors, re.match vs re.search vs re.findall
    vs re.finditer, re.sub, capturing and named groups, lookarounds, flags
    (IGNORECASE, MULTILINE, DOTALL, VERBOSE), compiled regex objects (re.compile),
    common practical patterns (email, phone, IP, URL, date), and interview questions.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python regular_expressions.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import re

print("=" * 60)
print("LESSON 12: Regular Expressions (re module) in Python")
print("=" * 60)


# ============================================================
# 1. Raw Strings vs Normal Strings in Regex
# ============================================================
print("\n--- 1. Raw Strings (r'...') in Regex ---")
# Regular expressions frequently use backslashes (\d, \w, \b).
# In standard Python strings, \ is an escape character (\n, \t).
# Always use raw strings r"..." so Python passes literal backslashes to the regex engine.

pattern_raw = r"\d+\.\d+"
print(f"Raw string pattern: {pattern_raw}")


# ============================================================
# 2. Core Search Functions: match vs search vs findall vs finditer
# ============================================================
print("\n--- 2. Core Regex Search Functions ---")
text = "Contact us at support@example.com or admin@site.org for assistance."

# 1. re.search(): searches anywhere in the string, returns first Match object (or None)
match_search = re.search(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
if match_search:
    print(f"re.search() match: {match_search.group()} (span: {match_search.span()})")

# 2. re.match(): checks for match ONLY at the beginning of the string (index 0)
match_start = re.match(r"Contact", text)
print(f"re.match('Contact', text): {'Matched: ' + match_start.group() if match_start else 'No match'}")
match_fail = re.match(r"support", text)
print(f"re.match('support', text): {match_fail} (fails because 'support' is not at index 0)")

# 3. re.fullmatch(): matches if the ENTIRE string matches the pattern
pattern_year = r"\d{4}"
print(f"re.fullmatch(r'\\d{{4}}', '2026')   : {bool(re.fullmatch(pattern_year, '2026'))}")
print(f"re.fullmatch(r'\\d{{4}}', '2026-11'): {bool(re.fullmatch(pattern_year, '2026-11'))}")

# 4. re.findall(): returns a list of all matched string substrings (or tuples if groups exist)
emails = re.findall(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
print(f"re.findall() emails: {emails}")

# 5. re.finditer(): returns an iterator yielding Match objects (memory-efficient for large text)
print("re.finditer() iterations:")
for match in re.finditer(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}", text):
    print(f"  Found '{match.group()}' at index range {match.span()}")


# ============================================================
# 3. Character Classes, Metacharacters & Anchors
# ============================================================
print("\n--- 3. Character Classes & Metacharacters ---")
# \d = digit [0-9]               \D = non-digit [^0-9]
# \w = word character [a-zA-Z0-9_]  \W = non-word character
# \s = whitespace [ \t\n\r\f\v]  \S = non-whitespace
# .  = any character except newline (unless DOTALL)
# ^  = start of string / line    $  = end of string / line
# \b = word boundary             \B = non-word boundary

sample_phrase = "Item 007 costs $45.99 on 2026-11-15!"

digits = re.findall(r"\d+", sample_phrase)
print(f"Digits (\\d+): {digits}")

# Word boundaries (\b) match at start or end of a word:
words_with_bound = re.findall(r"\b\w{4}\b", sample_phrase)
print(f"4-letter words (\\b\\w{{4}}\\b): {words_with_bound}")

# Anchors ^ and $
print(f"Starts with 'Item' (^Item): {bool(re.search(r'^Item', sample_phrase))}")
print(f"Ends with '!' (!$)       : {bool(re.search(r'!$', sample_phrase))}")


# ============================================================
# 4. Quantifiers (Greedy vs Non-Greedy / Lazy)
# ============================================================
print("\n--- 4. Quantifiers: Greedy vs Non-Greedy (Lazy) ---")
# *     = 0 or more (greedy)
# +     = 1 or more (greedy)
# ?     = 0 or 1 (or makes quantifier non-greedy when appended)
# {n}   = exactly n
# {n,}  = n or more
# {n,m} = between n and m

html = "<div><p>First paragraph</p><p>Second paragraph</p></div>"

# Greedy: consumes as much as possible
greedy_match = re.findall(r"<p>.*</p>", html)
print(f"Greedy (<p>.*</p>)  : {greedy_match}")

# Non-Greedy / Lazy: consumes as little as possible using ?
lazy_match = re.findall(r"<p>.*?</p>", html)
print(f"Lazy   (<p>.*?</p>) : {lazy_match}")


# ============================================================
# 5. Grouping: Numbered Groups, Named Groups, Non-Capturing
# ============================================================
print("\n--- 5. Capturing, Named Groups & Non-Capturing Groups ---")
log_entry = "2026-11-15 09:30:15 [ERROR] [auth_service] Invalid user token for uid: 4082"

# 1. Numbered Capturing Groups: (pattern)
pattern_numbered = r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) \[(\w+)\]"
match_num = re.search(pattern_numbered, log_entry)
if match_num:
    print(f"Full match (group 0) : {match_num.group(0)}")
    print(f"Group 1 (Date)       : {match_num.group(1)}")
    print(f"Group 2 (Time)       : {match_num.group(2)}")
    print(f"Group 3 (Log Level)  : {match_num.group(3)}")
    print(f"groups() tuple       : {match_num.groups()}")

# 2. Named Capturing Groups: (?P<name>pattern)
pattern_named = (
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<level>\w+)\]\s+"
    r"\[(?P<service>\w+)\]\s+"
    r"(?P<message>.*)"
)
match_named = re.search(pattern_named, log_entry)
if match_named:
    data = match_named.groupdict()
    print(f"groupdict() dictionary:")
    for k, v in data.items():
        print(f"  {k:8s} -> {v}")

# 3. Non-Capturing Group: (?:pattern) - groups without saving capture overhead
domain_pattern = r"(?:https?://)?(?:www\.)?([\w-]+(?:\.[\w-]+)+)"
m_domain = re.search(domain_pattern, "Visit https://www.python.org today")
if m_domain:
    print(f"Non-capturing extraction (domain only): {m_domain.group(1)}")


# ============================================================
# 6. Text Manipulation: re.sub(), re.subn(), and re.split()
# ============================================================
print("\n--- 6. String Substitution & Splitting (re.sub, re.split) ---")

dirty_text = "Call 555-123-4567 or 555-987-6543 today."
# Mask phone numbers with redaction
redacted, count = re.subn(r"\d{3}-\d{3}-\d{4}", "[REDACTED]", dirty_text)
print(f"Redacted text: '{redacted}' ({count} replacements made)")

# Backreferences in re.sub (\1, \2 or \g<name>)
# Convert 'YYYY-MM-DD' to 'DD/MM/YYYY'
date_string = "Release date: 2026-11-15, Expiry: 2027-05-30"
reformatted_date = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", date_string)
print(f"Reformatted dates: {reformatted_date}")

# Using a function callback with re.sub
def to_uppercase(match):
    return match.group().upper()

text_mixed = "apple banana cherry"
upper_text = re.sub(r"\b\w+\b", to_uppercase, text_mixed)
print(f"re.sub with callback: {upper_text}")

# re.split(): split string by complex regex pattern
csv_style = "alpha, beta ; gamma   delta\tepsilon"
tokens = re.split(r"[,\s;]+", csv_style)
print(f"re.split() tokens: {tokens}")


# ============================================================
# 7. Regex Compilation: re.compile() for Performance
# ============================================================
print("\n--- 7. Performance: re.compile() ---")
# Pre-compiling a regex pattern compiles the bytecode once.
# In high-throughput loops, re.compile avoids repeated parsing.

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

user_emails = ["navneet@example.com", "invalid-email@", "dev.team@domain.co.uk", "@empty.com"]
for email in user_emails:
    is_valid = bool(EMAIL_REGEX.match(email))
    print(f"  {email:<25}: {'VALID' if is_valid else 'INVALID'}")


# ============================================================
# 8. Regex Flags
# ============================================================
print("\n--- 8. Regex Compilation Flags ---")

# re.IGNORECASE (re.I)
print("re.IGNORECASE:")
print(f"  'python' in 'PYTHON 3.12': {bool(re.search(r'python', 'PYTHON 3.12', re.I))}")

# re.MULTILINE (re.M): makes ^ and $ match start/end of each line, not just whole string
multiline_text = "First line\nSecond line\nThird line"
lines_starting_with = re.findall(r"^\w+", multiline_text, re.M)
print(f"re.MULTILINE (lines starting with word): {lines_starting_with}")

# re.DOTALL (re.S): makes . match any character INCLUDING newline \n
code_block = "```python\nx = 10\nprint(x)\n```"
code_match = re.search(r"```python(.*?)```", code_block, re.DOTALL)
if code_match:
    print(f"re.DOTALL extracted snippet:\n{code_match.group(1).strip()}")

# re.VERBOSE (re.X): allow comments and whitespace inside complex regex
phone_pattern_verbose = re.compile(
    r"""
    ^(\+\d{1,3}\s)?     # Optional international country code (+91, +1)
    \(?(\d{3})\)?       # Area code with optional parentheses
    [-.\s]?             # Delimiter (hyphen, dot, or space)
    (\d{3})             # First 3 digits
    [-.\s]?             # Delimiter
    (\d{4})$            # Last 4 digits
    """,
    re.VERBOSE,
)
print(f"Verbose phone match '+1 (555) 123-4567': {bool(phone_pattern_verbose.match('+1 (555) 123-4567'))}")


# ============================================================
# 9. Lookaround Assertions (Zero-Width)
# ============================================================
print("\n--- 9. Lookaround Assertions ---")
# Positive Lookahead:    (?=pattern)  - matches if followed by pattern
# Negative Lookahead:    (?!pattern)  - matches if NOT followed by pattern
# Positive Lookbehind:   (?<=pattern) - matches if preceded by pattern
# Negative Lookbehind:   (?<!pattern) - matches if NOT preceded by pattern

price_text = "Apple costs $15, Banana costs €12, Cherry costs $8, Date costs 50."

# Match amounts preceded by $
dollar_amounts = re.findall(r"(?<=\$)\d+", price_text)
print(f"Positive Lookbehind (?<=\\$)\\d+: {dollar_amounts}")

# Match numbers NOT preceded by $ or €
plain_amounts = re.findall(r"(?<![\$€])\b\d+\b", price_text)
print(f"Negative Lookbehind (?<![\\$€])\\b\\d+\\b: {plain_amounts}")

# Password strength validation using positive lookaheads:
# At least 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char
password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
sample_passwords = ["Pass123!", "weakpass", "NoSpecial1", "Navneet@2026"]
for pw in sample_passwords:
    print(f"  Password '{pw:<14}': {'STRONG' if password_regex.match(pw) else 'WEAK'}")


# ============================================================
# 10. Practical Real-World Patterns Summary
# ============================================================
print("\n--- 10. Practical Real-World Utility Patterns ---")
ipv4_sample = "Host 192.168.1.1 and 10.0.0.254 are online; 999.1.1.1 is invalid."
# Match valid IPv4 addresses (0-255 range per octet)
ipv4_regex = re.compile(
    r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
)
print(f"Valid IPv4 matches: {ipv4_regex.findall(ipv4_sample)}")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python regular_expressions.py
# ============================================================
#
# 1. EMAIL VALIDATOR:
#    Write a function `is_valid_email(email: str) -> bool` that checks if an
#    email follows the format: username@domain.tld (tld 2 to 6 alphabetic chars).
#
# 2. DATE EXTRACTION & REFORMATTING:
#    Given text: "Due dates are 2026/11/15, 2026/12/01, and 2027/01/10."
#    Use `re.sub()` to convert all dates to "DD-MM-YYYY" format.
#
# 3. LOG PARSER:
#    Given log string: "CRITICAL 2026-11-15 10:20:30 [service=payment_api] Connection timed out"
#    Use named groups (?P<severity>...), (?P<timestamp>...), (?P<service>...), and
#    (?P<message>...) to extract and print a dictionary of these fields.
#
# 4. WORD FREQUENCY WITH BOUNDARIES:
#    Extract all whole words (ignoring case and punctuation) from:
#    "Python is great. Regular expressions in python make python powerful!"
#    Count occurrences of the word "python" using `re.findall()`.
#
# 5. LOOKAROUND CHALLENGE:
#    Extract all numbers from "Order #101: 5 apples, 12 oranges, total $65, discount $10."
#    that represent monetary dollar amounts (i.e., preceded by '$').

# --- write your code below this line ---
