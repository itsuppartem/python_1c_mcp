# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-03

First release. Bilingual docs (English `README.md`, Russian `README.ru.md`, stacked `README.pypi.md`).

### Added

- Read-only MCP server for 1C:Enterprise standard OData (`standard.odata`, platform 8.3.5+).
- Tools: `list_entity_sets`, `describe_entity_set`, `odata_query`, `get_entity`, `get_metadata`.
- Resources: `1c://entity-sets`, `1c://metadata`.
- Connection via `ONEC_SERVER` / `ONEC_INFOBASE` / credentials or `ONEC_URL`.
- Built on [python-1c-odata](https://github.com/itsuppartem/python_1c_odata) 0.6.0.
