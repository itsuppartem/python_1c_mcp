"""Read-only MCP tool implementations."""

from __future__ import annotations

from typing import Any

from python_1c_odata.metadata import EntityTypeInfo

from python_1c_mcp.connection import get_infobase
from python_1c_mcp.entity_set import NamedEntitySet

_LIST_TRUNCATE_AT = 500
_METADATA_XML_LIMIT = 8000
_DEFAULT_TOP = 20
_MAX_TOP = 100


def entity_type_to_dict(info: EntityTypeInfo) -> dict[str, Any]:
    return {
        "name": info.name,
        "keys": list(info.keys),
        "properties": [
            {"name": prop.name, "type": prop.type, "nullable": prop.nullable}
            for prop in info.properties
        ],
        "navigation_properties": list(info.navigation_properties),
    }


async def list_entity_sets() -> dict[str, Any]:
    ib = await get_infobase()
    names = await ib.entity_sets()
    total = len(names)
    truncated = total > _LIST_TRUNCATE_AT
    if truncated:
        names = names[:_LIST_TRUNCATE_AT]
    result: dict[str, Any] = {
        "total": total,
        "entity_sets": names,
        "truncated": truncated,
    }
    if truncated:
        result["message"] = (
            f"Listing truncated to first {_LIST_TRUNCATE_AT} of {total} entity sets."
        )
    return result


async def describe_entity_set(entity_set: str) -> dict[str, Any]:
    ib = await get_infobase()
    info = await ib.entity_type_for_set(entity_set)
    return entity_type_to_dict(info)


async def odata_query(
    entity_set: str,
    *,
    odata_filter: str | None = None,
    select: str | None = None,
    top: int = _DEFAULT_TOP,
    skip: int | None = None,
    orderby: str | None = None,
    inlinecount: bool = False,
) -> dict[str, Any]:
    if top < 1:
        raise ValueError("top must be at least 1")
    if top > _MAX_TOP:
        raise ValueError(f"top cannot exceed {_MAX_TOP}")
    if skip is not None and skip < 0:
        raise ValueError("skip must be non-negative")

    ib = await get_infobase()
    es = NamedEntitySet(ib, entity_set)
    page = await es.query(
        top=top,
        skip=skip,
        select=select.split(",") if select else None,
        odata_filter=odata_filter,
        orderby=orderby,
        inlinecount=inlinecount,
    )
    payload: dict[str, Any] = {
        "entity_set": entity_set,
        "value": page.value,
        "count": len(page.value),
    }
    if inlinecount and page.count is not None:
        payload["inlinecount"] = page.count
    return payload


async def get_entity(
    entity_set: str,
    ref_key: str,
    *,
    select: str | None = None,
) -> dict[str, Any]:
    ib = await get_infobase()
    es = NamedEntitySet(ib, entity_set)
    record = await es.get(
        ref_key,
        select=select.split(",") if select else None,
    )
    return {"entity_set": entity_set, "ref_key": ref_key, "record": record}


async def get_metadata(*, raw_xml: bool = False) -> dict[str, Any]:
    ib = await get_infobase()
    if raw_xml:
        xml = await ib.metadata()
        truncated = len(xml) > _METADATA_XML_LIMIT
        return {
            "raw_xml": xml[:_METADATA_XML_LIMIT],
            "length": len(xml),
            "truncated": truncated,
        }

    names = await ib.entity_sets()
    sample = names[:10]
    return {
        "entity_set_count": len(names),
        "sample_entity_sets": sample,
        "odata_root": ib.root,
    }


async def resource_entity_sets() -> str:
    ib = await get_infobase()
    names = await ib.entity_sets()
    lines = [f"{index + 1}. {name}" for index, name in enumerate(names)]
    return "1C OData entity sets:\n" + "\n".join(lines)


async def resource_metadata() -> str:
    ib = await get_infobase()
    xml = await ib.metadata()
    if len(xml) > _METADATA_XML_LIMIT:
        return xml[:_METADATA_XML_LIMIT] + f"\n\n... truncated ({len(xml)} bytes total)"
    return xml
