# Changelog

## 3.2.4

- Consolidated the maintained release line onto the default branch.
- Added reliable interactive-session detection for standard Python, IPython,
  Jupyter, and redirected streams.
- Updated supported runtime, documentation, and development dependencies while
  retaining Python 3.10 compatibility.
- Refreshed project metadata and development instructions.

## 3.2.2

- Prevented file handlers and file creation when `no_file_logging=True`.
- Preserved positional formatting arguments and caller stack levels in
  `Logger.error()`.
- Restored `Loggable.method_logger` as a working descriptor that creates
  method-specific children.
- Made `isEnabledFor(level)` a callable method.
- Kept the wrapped standard-library logger at the lowest enabled handler level.
- Made handler setup idempotent and extracted handler and hierarchy management
  from `Logger`.
- Stopped replacing the process-wide `LogRecordFactory` during import.
- Deferred CLI argument parsing and public-suffix loading until those features
  are used.
- Added contract tests for logger identity, hierarchy, handlers, levels, caller
  attribution, `Loggable`, and `warn_once()`.
- Updated the README for Python 3.10+ and the v3 API.
- Removed unused direct dependencies on `appdirs`, `pypattyrn`, and `urllib3`,
  and declared the previously missing `public-suffix-list` dependency.
