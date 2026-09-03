"""Read-only MCP server for 1C:Enterprise standard OData."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.mcpserver import MCPServer

from python_1c_mcp.connection import ConfigError, close_infobase, validate_config
from python_1c_mcp.tools import handlers

_LOG = logging.getLogger("python_1c_mcp")

INSTRUCTIONS = """\
Read-only MCP server for 1C:Enterprise standard OData (platform 8.3.5+, standard.odata publication).

Available read operations only — no create, update, delete, or post/unpost.
Use list_entity_sets and describe_entity_set to discover schema, then odata_query or get_entity.
"""


@asynccontextmanager
async def _lifespan(_server: MCPServer) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await close_infobase()


mcp = MCPServer(
    "python-1c-mcp",
    title="1C OData (read-only)",
    instructions=INSTRUCTIONS,
    lifespan=_lifespan,
)


@mcp.tool(
    name="list_entity_sets",
    description=(
        "List all OData entity set names published by the connected 1C infobase "
        "(Catalog_*, Document_*, register names, etc.). Read-only."
    ),
)
async def list_entity_sets() -> dict:
    return await handlers.list_entity_sets()


@mcp.tool(
    name="describe_entity_set",
    description=(
        "Describe keys, scalar properties, and navigation properties for one entity set. "
        "Pass the full set name, e.g. Catalog_Товары. Read-only."
    ),
)
async def describe_entity_set(entity_set: str) -> dict:
    return await handlers.describe_entity_set(entity_set)


@mcp.tool(
    name="odata_query",
    description=(
        "Run a read-only OData query against an entity set. Supports $filter, $select, "
        "$top (default 20, max 100), $skip, $orderby, and $inlinecount. Read-only."
    ),
)
async def odata_query(
    entity_set: str,
    odata_filter: str | None = None,
    select: str | None = None,
    top: int = 20,
    skip: int | None = None,
    orderby: str | None = None,
    inlinecount: bool = False,
) -> dict:
    return await handlers.odata_query(
        entity_set,
        odata_filter=odata_filter,
        select=select,
        top=top,
        skip=skip,
        orderby=orderby,
        inlinecount=inlinecount,
    )


@mcp.tool(
    name="get_entity",
    description=(
        "Fetch a single entity record by Ref_Key GUID from an entity set. Read-only."
    ),
)
async def get_entity(
    entity_set: str,
    ref_key: str,
    select: str | None = None,
) -> dict:
    return await handlers.get_entity(entity_set, ref_key, select=select)


@mcp.tool(
    name="get_metadata",
    description=(
        "Return OData $metadata summary (entity set count and sample names). "
        "Set raw_xml=true for truncated XML. Read-only."
    ),
)
async def get_metadata(raw_xml: bool = False) -> dict:
    return await handlers.get_metadata(raw_xml=raw_xml)


@mcp.resource(
    "1c://entity-sets",
    name="entity-sets",
    description="Cached list of all OData entity set names from $metadata.",
    mime_type="text/plain",
)
async def entity_sets_resource() -> str:
    return await handlers.resource_entity_sets()


@mcp.resource(
    "1c://metadata",
    name="metadata",
    description="Raw or truncated $metadata XML from the connected infobase.",
    mime_type="application/xml",
)
async def metadata_resource() -> str:
    return await handlers.resource_metadata()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    try:
        validate_config()
    except ConfigError as exc:
        print(f"python-1c-mcp: {exc}", file=sys.stderr)
        sys.exit(1)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
