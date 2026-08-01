"""
SYNOPSIS
    Reference and demo of Python's built-in string operations - creation,
    indexing/slicing, case conversion, searching, trimming, splitting/joining,
    replacing, formatting, padding, type checks, encoding, and translation.

DESCRIPTION
    Run this file top-to-bottom to see every operation's output, then use it
    as a reference later. Strings in Python are immutable - every method
    below that "changes" a string actually returns a brand new string.

EXAMPLE
    python string_operations.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.1.0
"""

print("=" * 60)
print("LESSON 8: String Operations")
print("=" * 60)

print("\n--- Creating strings ---")
single = 'single quotes'
double = "double quotes"
triple = """triple quotes -
can span multiple lines"""
raw = r"raw string - \n is not a newline here"
fstring_name = "Ruchik"
fstring = f"f-string - hello {fstring_name}, 2 + 2 = {2 + 2}"
byte_string = b"byte string - not the same type as str"

print(single, double, sep=" | ")
print(triple)
print(raw)
print(fstring)
print(byte_string, type(byte_string).__name__)


print("\n--- Length, indexing, slicing ---")
text = "Hello, World!"
print(f"len(text) = {len(text)}")
print(f"text[0] = {text[0]}")          # H
print(f"text[-1] = {text[-1]}")        # !  (negative index = from the end)
print(f"text[0:5] = {text[0:5]}")      # Hello  (slice, end excluded)
print(f"text[7:] = {text[7:]}")        # World!
print(f"text[:5] = {text[:5]}")        # Hello
print(f"text[::-1] = {text[::-1]}")    # !dlroW ,olleH  (step -1 = reversed)


print("\n--- Concatenation & repetition ---")
first = "Py"
second = "thon"
print(f"first + second = {first + second}")
print(f"first * 3 = {first * 3}")


print("\n--- Case conversion ---")
mixed = "Hello World"
print(f"'{mixed}'.upper() = {mixed.upper()}")
print(f"'{mixed}'.lower() = {mixed.lower()}")
print(f"'{mixed}'.title() = {mixed.title()}")
print(f"'{mixed}'.capitalize() = {mixed.capitalize()}")
print(f"'{mixed}'.swapcase() = {mixed.swapcase()}")
print(f"'{mixed}'.casefold() = {mixed.casefold()}")  # like .lower(), but more aggressive for non-ASCII


print("\n--- Searching & checking ---")
sentence = "the quick brown fox jumps over the lazy dog"
print(f"'{sentence}'.find('fox') = {sentence.find('fox')}")     # index, or -1 if not found
print(f"'{sentence}'.find('cat') = {sentence.find('cat')}")
print(f"'{sentence}'.index('fox') = {sentence.index('fox')}")     # like find(), but raises ValueError if missing
print(f"'{sentence}'.rfind('the') = {sentence.rfind('the')}")     # search from the right
print(f"'{sentence}'.rindex('the') = {sentence.rindex('the')}")   # like rfind(), but raises ValueError if missing
print(f"'{sentence}'.count('the') = {sentence.count('the')}")
print(f"'{sentence}'.startswith('the') = {sentence.startswith('the')}")
print(f"'{sentence}'.endswith('dog') = {sentence.endswith('dog')}")
print(f"'fox' in sentence = {'fox' in sentence}")   # the "in" operator - most common existence check


print("\n--- Trimming whitespace ---")
padded = "   padded text   "
print(f"'{padded}'.strip() = '{padded.strip()}'")
print(f"'{padded}'.lstrip() = '{padded.lstrip()}'")
print(f"'{padded}'.rstrip() = '{padded.rstrip()}'")
print("'xxhelloxx'.strip('x') =", "xxhelloxx".strip("x"))  # strip a specific character, not just whitespace


print("\n--- Splitting & joining ---")
csv_line = "apple,banana,cherry"
parts = csv_line.split(",")
print(f"'{csv_line}'.split(',') = {parts}")
print(f"'a b  c'.split() = {'a b  c'.split()}")            # no args = split on any whitespace, collapsing repeats
print(f"'a.b.c'.rsplit('.', 1) = {'a.b.c'.rsplit('.', 1)}")  # split from the right, maxsplit=1
multiline_text = "line1\nline2\nline3"
print(f"'line1\\nline2\\nline3'.splitlines() = {multiline_text.splitlines()}")
print(f"'-'.join(parts) = {'-'.join(parts)}")               # join is a STRING method, called on the separator

# partition() splits on the FIRST occurrence only, always returning exactly 3 pieces:
# (before, separator, after) - the separator itself is included, unlike split()
print(f"'{csv_line}'.partition(',') = {csv_line.partition(',')}")
print(f"'{csv_line}'.rpartition(',') = {csv_line.rpartition(',')}")  # same idea, from the right


print("\n--- Replacing ---")
noisy = "aaa bbb aaa ccc aaa"
print(f"'{noisy}'.replace('aaa', 'X') = {noisy.replace('aaa', 'X')}")
print(f"'{noisy}'.replace('aaa', 'X', 1) = {noisy.replace('aaa', 'X', 1)}")  # count limit

# removeprefix/removesuffix (3.9+) - safer than manual slicing, no-op if the prefix/suffix isn't there
filename = "report_final.txt"
print(f"'{filename}'.removesuffix('.txt') = {filename.removesuffix('.txt')}")
print(f"'{filename}'.removeprefix('report_') = {filename.removeprefix('report_')}")
print(f"'{filename}'.removeprefix('xyz_') = {filename.removeprefix('xyz_')}")  # no match -> unchanged


print("\n--- Formatting ---")
name, age = "Ruchik", 27
print(f"f-string: {name} is {age}")
print("str.format(): {} is {}".format(name, age))
print("positional: {1} is {0}".format(age, name))
print("percent-style (legacy): %s is %d" % (name, age))
print(f"number formatting: pi is {3.14159:.2f}")     # 2 decimal places
print(f"padding numbers: {5:04d}")                    # zero-padded to 4 digits

# format_map() - like .format(**dict), but takes the dict directly without unpacking
profile = {"name": "Ruchik", "age": 27}
print(f"'{{name}} is {{age}}'.format_map(profile) = {'{name} is {age}'.format_map(profile)}")


print("\n--- Padding & alignment ---")
word = "hi"
print(f"'{word}'.ljust(10, '.') = '{word.ljust(10, '.')}'")
print(f"'{word}'.rjust(10, '.') = '{word.rjust(10, '.')}'")
print(f"'{word}'.center(10, '.') = '{word.center(10, '.')}'")
print(f"'{'7'}'.zfill(5) = '{'7'.zfill(5)}'")  # zero-pad on the left, handles a leading - sign correctly
print(f"'a\\tb\\tc'.expandtabs(4) = '{'a\tb\tc'.expandtabs(4)}'")  # replaces tabs with spaces up to the given width


print("\n--- Type checks (all return True/False) ---")
print(f"'abc'.isalpha() = {'abc'.isalpha()}")
print(f"'123'.isdigit() = {'123'.isdigit()}")
print(f"'123'.isdecimal() = {'123'.isdecimal()}")   # stricter than isdigit() - no superscripts/fractions
print(f"'123'.isnumeric() = {'123'.isnumeric()}")    # broadest - also accepts things like '½' or '一'
print(f"'abc123'.isalnum() = {'abc123'.isalnum()}")
print(f"'   '.isspace() = {'   '.isspace()}")
print(f"'ABC'.isupper() = {'ABC'.isupper()}")
print(f"'abc'.islower() = {'abc'.islower()}")
print(f"'Title Case'.istitle() = {'Title Case'.istitle()}")
print(f"'my_var'.isidentifier() = {'my_var'.isidentifier()}")  # valid as a Python variable name?
print(f"'hello'.isascii() = {'hello'.isascii()}")
print(f"'café'.isascii() = {'café'.isascii()}")      # False - é is not ASCII
print(f"'hello'.isprintable() = {'hello'.isprintable()}")
print(f"'hello\\n'.isprintable() = {('hello' + chr(10)).isprintable()}")  # False - newline isn't printable


print("\n--- Encoding / decoding ---")
text_with_unicode = "café"
encoded = text_with_unicode.encode("utf-8")
print(f"'{text_with_unicode}'.encode('utf-8') = {encoded}")
print(f"decoded back: {encoded.decode('utf-8')}")


print("\n--- Translation (bulk character replacement) ---")
table = str.maketrans("abc", "xyz")
print(f"'abcdef'.translate(maketrans('abc','xyz')) = {'abcdef'.translate(table)}")


print("\n--- Membership & comparison ---")
print(f"'Py' in 'Python' = {'Py' in 'Python'}")
print(f"'apple' < 'banana' = {'apple' < 'banana'}")  # lexicographic (alphabetical) comparison


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python string_operations.py
# ============================================================
#
# 1. Take the string `raw = "  Hello, PYTHON World!  "` and, using only
#    string methods (no manual loops), produce `"hello, python world!"`
#    (trimmed and lowercased).
# 2. Given `sentence = "the rain in spain falls mainly on the plain"`,
#    count how many times the substring "ain" appears.
# 3. Given `csv_row = "Ruchik,27,Zurich"`, split it into a list, then
#    rebuild it as `"Ruchik | 27 | Zurich"` using join().
# 4. Given `code = "user_id_42"`, check whether it `.isidentifier()`,
#    and print the result.

# --- write your code below this line ---
