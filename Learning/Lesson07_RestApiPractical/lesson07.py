"""
SYNOPSIS
    Lesson 7: Practical - Calling a REST API with `requests` - GET/POST,
    query params, JSON bodies, custom headers, and raise_for_status().

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom. Needs internet access - it calls free public
    test APIs (GitHub, httpbin).

EXAMPLE
    python lesson07.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
    Requires    : pip install requests
"""

import requests

print("=" * 60)
print("LESSON 7: Practical - REST API with requests")
print("=" * 60)

print("\n--- GET request ---")
response = requests.get("https://api.github.com/users/octocat")
print(response.status_code)   # 200 = success
data = response.json()        # .json() parses the response body as JSON
print(data["login"], data["public_repos"])

print("\n--- Raise an error for bad status codes (404, 500, etc.) ---")
# requests does NOT throw automatically - you opt in with raise_for_status()
try:
    bad_response = requests.get("https://api.github.com/users/this-user-should-not-exist-12345")
    bad_response.raise_for_status()
except requests.exceptions.HTTPError as ex:
    print(f"Request failed: {ex}")

print("\n--- GET with query parameters ---")
# pass a `params` dict, requests builds the query string for you
response = requests.get("https://httpbin.org/get", params={"name": "Ruchik", "role": "Consultant"})
print(response.json()["args"])

print("\n--- POST with a JSON body ---")
# pass a `json` dict directly - requests serializes it and sets the content-type header for you
response = requests.post("https://httpbin.org/post", json={"name": "Ruchik", "age": 27})
print(response.json()["json"])

print("\n--- Custom headers (e.g. auth tokens) ---")
headers = {"Authorization": "Bearer FAKE_TOKEN_FOR_DEMO"}
response = requests.get("https://httpbin.org/headers", headers=headers)
print(response.json()["headers"]["Authorization"])


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson07.py
# ============================================================
#
# 1. GET https://api.github.com/repos/python/cpython and print:
#    - the repo's "stargazers_count"
#    - the repo's "description"
# 2. Write a function `get_user(username)` that GETs
#    https://api.github.com/users/<username>, and:
#    - returns the parsed JSON dict if status_code == 200
#    - returns None if the user isn't found (status_code == 404)
# 3. Call get_user("octocat") and get_user("a-user-that-does-not-exist-xyz"),
#    printing the result of each

# --- write your code below this line ---
