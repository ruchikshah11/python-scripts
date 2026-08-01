# common

Shared logging helper reused by every script under `SharePoint/`. Not meant to be run
directly. (The SharePoint-specific auth/list functions live in the separate
[sharepoint](../sharepoint/README.md) library, not here.)

## Files
- **`sp_logging.py`** — `build_logger(script_folder, script_name)` returns `(logger, correlation_id)`:
  sets up a logger writing to `<script_folder>/Logs/<script_name>_<date>.log` with
  7-day retention, and a per-run CorrelationID.

## How scripts import this
Since each script lives in its own sibling folder (not a proper installed package),
every script adds `common/` to `sys.path` at the top before importing:

```python
SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER.parent / "common"))

import sp_logging
```

Note: IDEs (Pylance/VS Code) may show "Import could not be resolved" for `sp_logging`
since they can't see the runtime `sys.path` change - this is a false warning, not a real error.

## Used by
- [ConnectToSite](../ConnectToSite/README.md)
- [GetList](../GetList/README.md)
- [GetListItems](../GetListItems/README.md)
- [GetConnection](../GetConnection/README.md)
