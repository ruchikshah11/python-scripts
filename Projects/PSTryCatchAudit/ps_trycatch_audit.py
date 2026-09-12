"""
SYNOPSIS
    Finds PowerShell functions whose entire body got wrapped in a new
    try/catch block, by comparing a working-tree file against its git HEAD
    version.

DESCRIPTION
    Built to clean up an AI-assisted change to a PowerShell deployment
    script (Invoke-bsoneDeployment.ps1) where nearly every function had been
    wrapped in a swallow-and-log try/catch. That silently let critical steps
    (e.g. Set-ExecutionPolicy failing, a config file missing) fail without
    stopping the script. This script flags every function where the *whole
    body* is a new top-level try/catch, so those wraps can be reviewed and
    removed by hand, restoring normal exception propagation.

    Uses a hand-rolled brace matcher (tracks single/double-quoted strings
    and #/<# #> comments) rather than a real PowerShell parser, so it can
    fail to find the matching closing brace for very large or unusually
    quoted functions (here-strings in particular aren't handled). Treat its
    output as a starting point, not a guarantee of completeness -- cross-check
    anything it misses against `git diff` directly.

EXAMPLE
    python ps_trycatch_audit.py path\\to\\Current.ps1 path\\to\\Original.ps1

    (Get the "Original" file with e.g. `git show HEAD:path/to/File.ps1 > Original.ps1`)

NOTES
    One-off analysis script, not a general PowerShell parser. No third-party
    dependencies -- stdlib only.
"""
import re
import sys


def read(path):
    with open(path, encoding='utf-8-sig') as f:
        return f.read()


def find_functions(text):
    """Return list of (name, start_idx, open_brace_idx, close_brace_idx).

    start_idx      = index of the 'Function'/'function' keyword
    open_brace_idx = index of the function's opening '{'
    close_brace_idx = index of the matching closing '}' (inclusive)
    """
    funcs = []
    pattern = re.compile(r'(?im)^\s*(?:function)\s+([A-Za-z0-9_\-]+)')
    for m in pattern.finditer(text):
        name = m.group(1)
        open_idx = text.find('{', m.end())
        if open_idx == -1:
            continue
        end_idx = match_brace(text, open_idx)
        if end_idx is None:
            continue
        funcs.append((name, m.start(), open_idx, end_idx))
    return funcs


def match_brace(text, open_idx):
    """Find the index of the '}' matching text[open_idx] == '{'.

    Tracks single/double-quoted strings and #/<# #> comments so braces
    inside them aren't counted. Does NOT handle here-strings (@"..."@,
    @'...'@) -- functions containing those can return None even though
    they're syntactically fine.
    """
    assert text[open_idx] == '{'
    depth = 0
    i = open_idx
    n = len(text)
    in_squote = in_dquote = in_line_comment = in_block_comment = False
    while i < n:
        c = text[i]
        nc = text[i + 1] if i + 1 < n else ''
        if in_line_comment:
            if c == '\n':
                in_line_comment = False
            i += 1
            continue
        if in_block_comment:
            if c == '#' and text[i - 1] == '>':
                in_block_comment = False
            i += 1
            continue
        if in_squote:
            if c == "'" and nc == "'":
                i += 2
                continue
            if c == "'":
                in_squote = False
            i += 1
            continue
        if in_dquote:
            if c == '`':
                i += 2
                continue
            if c == '"':
                in_dquote = False
            i += 1
            continue
        if c == '#':
            in_line_comment = True
            i += 1
            continue
        if c == '<' and nc == '#':
            in_block_comment = True
            i += 2
            continue
        if c == "'":
            in_squote = True
            i += 1
            continue
        if c == '"':
            in_dquote = True
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def body_starts_with_try(text, open_brace_idx, close_brace_idx):
    body = text[open_brace_idx + 1:close_brace_idx]
    stripped = body.lstrip()
    return stripped.startswith('try') and stripped[3:].lstrip().startswith('{')


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <current.ps1> <original.ps1>")
        sys.exit(1)

    new_text = read(sys.argv[1])
    old_text = read(sys.argv[2])

    new_funcs = find_functions(new_text)
    old_funcs = find_functions(old_text)
    old_by_name = {}
    for f in old_funcs:
        old_by_name.setdefault(f[0].lower(), []).append(f)

    print(f"Total functions parsed -- current: {len(new_funcs)}, original: {len(old_funcs)}")
    print()

    candidates = []
    for (name, start, open_idx, close_idx) in new_funcs:
        if not body_starts_with_try(new_text, open_idx, close_idx):
            continue
        old_list = old_by_name.get(name.lower())
        if not old_list:
            candidates.append((name, start, "NEW_FUNCTION"))
            continue
        already_wrapped = any(
            body_starts_with_try(old_text, ohstart, ohend)
            for (_, _, ohstart, ohend) in old_list
        )
        if not already_wrapped:
            candidates.append((name, start, "ADDED_WRAP"))

    print(f"Functions whose ENTIRE body is a try/catch in 'current' but wasn't in 'original': {len(candidates)}")
    for name, start, kind in candidates:
        line_no = new_text.count('\n', 0, start) + 1
        print(f"  [{kind}] {name}  (line ~{line_no})")

    print()
    print("Note: functions using advanced syntax (Param()/Process{} blocks) or")
    print("containing here-strings can be missed or reported as parse failures --")
    print("verify anything suspicious by reading the actual git diff for that function.")


if __name__ == '__main__':
    main()
