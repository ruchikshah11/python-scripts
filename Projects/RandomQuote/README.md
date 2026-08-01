# Random Quote / Joke Generator

Gets a random inspirational quote, general joke, or Chuck Norris joke — **no API key
required**. Three free, keyless APIs, one per `--type`.

## Prerequisites
```
pip install requests
```

## Run it
```
python random_quote.py                        # quote (default)
python random_quote.py --type joke
python random_quote.py --type chuck --count 3
```

## Sources
| `--type` | API | Format |
|---|---|---|
| `quote` (default) | [ZenQuotes](https://zenquotes.io) | `"text" - author` |
| `joke` | [Official Joke API](https://official-joke-api.appspot.com) | `setup ... punchline` |
| `chuck` | [api.chucknorris.io](https://api.chucknorris.io) | single-line joke |

`--count` fetches that many (one request per item — there's no bulk endpoint used here).

## Logging
Logs are written to `Logs/random_quote_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (tested live: quote, joke, and 2x chuck jokes)
