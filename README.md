# python-1c-mcp

Read-only [Model Context Protocol](https://modelcontextprotocol.io/) server for **1C:Enterprise standard OData** (`standard.odata`, platform **8.3.5+**).

Built on [python-1c-odata](https://github.com/itsuppartem/python_1c_odata). Exposes schema discovery and OData queries to LLM agents in Claude Desktop, Cursor, and other MCP hosts.

## Read-only scope

This server provides **read-only** access only:

- List and describe entity sets from `$metadata`
- Query entity sets (`$filter`, `$select`, `$top`, `$skip`, `$orderby`, `$inlinecount`)
- Fetch a single record by `Ref_Key`

There are **no** create, update, delete, post, or unpost tools.

**Honest limits:** standard OData 3.0 publication only. No 8.2, 7.7, SOAP, COM, or proprietary APIs.

## Install

```bash
pip install python-1c-mcp
```

Or from source:

```bash
git clone https://github.com/itsuppartem/python_1c_mcp.git
cd python_1c_mcp
pip install -e ".[dev]"
```

## Connection (environment variables)

| Variable | Required | Description |
|----------|----------|-------------|
| `ONEC_SERVER` | Yes* | Server base URL, e.g. `http://1c.example` |
| `ONEC_INFOBASE` | Yes* | Publication name, e.g. `trade` |
| `ONEC_USER` | Yes* | OData user |
| `ONEC_PASSWORD` | Yes* | OData password |
| `ONEC_URL` | Alt. | Single URL: `http://user:pass@host/publication` (overrides the four vars above) |
| `ONEC_FORMAT` | No | Response format: `json` (default), `atom`, or `auto` |
| `ONEC_DEBUG` | No | If `true`, log HTTP requests to stderr |

\* Either set `ONEC_URL` **or** all four of `ONEC_SERVER`, `ONEC_INFOBASE`, `ONEC_USER`, `ONEC_PASSWORD`.

The server validates configuration at startup and exits with a clear stderr message if settings are missing.

## MCP configuration

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python",
      "args": ["-m", "python_1c_mcp.server"],
      "env": {
        "ONEC_SERVER": "http://1c.example",
        "ONEC_INFOBASE": "trade",
        "ONEC_USER": "odata_user",
        "ONEC_PASSWORD": "secret"
      }
    }
  }
}
```

Alternatively, use the console script:

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python-1c-mcp",
      "env": {
        "ONEC_URL": "http://odata_user:secret@1c.example/trade"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `list_entity_sets` | All entity set names from `$metadata` |
| `describe_entity_set` | Keys, properties, navigation for one set |
| `odata_query` | Read-only collection query |
| `get_entity` | Single record by `Ref_Key` GUID |
| `get_metadata` | Metadata summary or truncated raw XML |

## Resources

| URI | Description |
|-----|-------------|
| `1c://entity-sets` | Plain-text list of entity set names |
| `1c://metadata` | `$metadata` XML (truncated if large) |

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

## License

MIT — Artem Gulyaev
