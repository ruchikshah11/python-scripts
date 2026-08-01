# Lesson 7: Practical — REST API with `requests`

## Prerequisite
```
pip install requests
```
This lesson calls free public APIs (GitHub, httpbin) — internet access required.

## Topics
- `requests.get(url)` (vs `Invoke-RestMethod -Uri $url -Method Get`)
- `response.json()` — parses the body like `Invoke-RestMethod` does automatically
- `response.raise_for_status()` — requests does NOT throw on 4xx/5xx by default, unlike `Invoke-RestMethod`
- Query params via the `params` dict
- POST with a JSON body via the `json` dict (auto-serializes + sets content-type)
- Custom headers (e.g. `Authorization: Bearer <token>`)

## Run it
```
python lesson07.py
```

## Exercise
At the bottom of `lesson07.py`:
1. GET the PowerShell repo, print `stargazers_count` and `description`
2. `get_user(username)` — returns parsed JSON dict on 200, `None` on 404
3. Call it for `"octocat"` and a made-up username, print both results

## Status
- [ ] Exercise completed
