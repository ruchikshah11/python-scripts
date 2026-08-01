# Hello World

The very first script in this workspace — confirms Python is installed and
runnable before anything else was built.

```python
print("Hello, World!")
```

Deliberately has no docstring/SYNOPSIS like every other script here — it predates
the logging/argparse conventions adopted from [ScriptTemplate.py](../Utilities/Templates/ScriptTemplate/ScriptTemplate.py)
and is left as-is on purpose, as the one intentionally bare "just run it" example.
([Index Generator](../Projects/IndexGenerator/README.md) correctly flags it as the
one file with no SYNOPSIS, rather than guessing one.)

## Run it
```
python hello_world.py
```
Note: on Windows, `.\hello_world.py` alone won't run it — PowerShell doesn't
associate `.py` files with the Python interpreter by default. Always run it via
`python hello_world.py`.

## Output
```
Hello, World!
```

## Status
- [x] Verified working
