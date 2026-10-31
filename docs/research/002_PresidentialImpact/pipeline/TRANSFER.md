# Transfer guide

The `pipeline/` directory is intentionally self-contained. To move it:

1. Copy the entire directory, including `pyproject.toml`, `config/`, `src/`,
   `tests/`, and these Markdown source decisions.
2. Install with `python -m pip install -e .`. The core package only uses the
   Python standard library. Add `.[shiller]` only when parsing the legacy Excel
   download.
3. Keep runtime output outside the package or in the ignored `.local/` directory.
   Move raw archives only when their source terms permit it; preserve their
   manifest beside them.
4. Change `config/sources.toml` or provide another config file to substitute a
   licensed market vendor. Keep the role and return-basis fields truthful.
5. Point the final `build-annual --output` path at the receiving application's
   import location. The produced JSON uses the documented PRES data contract and
   does not import QuantMeridian Python or TypeScript code.

There are no hard-coded absolute paths, credentials, database dependencies or
application imports. Network access occurs only in the explicit `fetch` command.
