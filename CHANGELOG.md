# Changelog

## 0.1.0 — 2026-09-03

Initial release.

- Read-only MCP server for 1C:Enterprise standard OData (`standard.odata`, platform 8.3.5+).
- Tools: `list_entity_sets`, `describe_entity_set`, `odata_query`, `get_entity`, `get_metadata`.
- Resources: `1c://entity-sets`, `1c://metadata`.
- Connection via `ONEC_SERVER` / `ONEC_INFOBASE` / credentials or `ONEC_URL`.
- Built on [python-1c-odata](https://github.com/itsuppartem/python_1c_odata) 0.6.0.
