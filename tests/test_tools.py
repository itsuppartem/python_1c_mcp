"""Tests for read-only MCP tool handlers."""

import pytest

from python_1c_mcp.connection import close_infobase, get_infobase
from python_1c_mcp.tools import handlers


@pytest.fixture
async def wired_infobase(fake_odata, metadata_xml, monkeypatch):
    monkeypatch.setenv("ONEC_SERVER", fake_odata.base_url)
    monkeypatch.setenv("ONEC_INFOBASE", "ut")
    monkeypatch.setenv("ONEC_USER", "user")
    monkeypatch.setenv("ONEC_PASSWORD", "secret")
    fake_odata.respond(200, metadata_xml, content_type="application/xml")
    yield fake_odata
    await close_infobase()


async def test_list_entity_sets_returns_names(wired_infobase):
    result = await handlers.list_entity_sets()
    assert result["total"] == 1
    assert result["entity_sets"] == ["Catalog_Товары"]
    assert result["truncated"] is False


async def test_describe_entity_set_returns_schema(wired_infobase):
    result = await handlers.describe_entity_set("Catalog_Товары")
    assert result["name"] == "Catalog_Товары"
    assert result["keys"] == ["Ref_Key"]
    assert [prop["name"] for prop in result["properties"]] == ["Ref_Key", "Description"]


async def test_odata_query_returns_value(wired_infobase):
    wired_infobase.respond(200, {"value": [{"Ref_Key": "abc", "Description": "Item"}]})
    result = await handlers.odata_query("Catalog_Товары", top=5)
    assert result["count"] == 1
    assert result["value"][0]["Description"] == "Item"
    last = wired_infobase.requests[-1]
    assert "/odata/standard.odata/Catalog_Товары" in last["path"]
    assert "$top=5" in last["query"]


async def test_odata_query_rejects_top_over_max(wired_infobase):
    with pytest.raises(ValueError, match="100"):
        await handlers.odata_query("Catalog_Товары", top=200)


async def test_get_entity_returns_record(wired_infobase):
    guid = "550e8400-e29b-41d4-a716-446655440000"
    wired_infobase.respond(200, {"Ref_Key": guid, "Description": "One"})
    result = await handlers.get_entity("Catalog_Товары", guid)
    assert result["record"]["Description"] == "One"
    assert guid in wired_infobase.requests[-1]["path"]


async def test_get_metadata_summary(wired_infobase):
    result = await handlers.get_metadata(raw_xml=False)
    assert result["entity_set_count"] == 1
    assert result["sample_entity_sets"] == ["Catalog_Товары"]
    assert result["odata_root"].endswith("/odata/standard.odata")


async def test_get_metadata_raw_xml_truncates(wired_infobase, metadata_xml):
    big = metadata_xml + ("x" * 9000)
    wired_infobase.respond(200, big, content_type="application/xml")
    result = await handlers.get_metadata(raw_xml=True)
    assert result["truncated"] is True
    assert result["length"] > len(result["raw_xml"])


async def test_shared_infobase_reused(wired_infobase):
    ib1 = await get_infobase()
    ib2 = await get_infobase()
    assert ib1 is ib2
    await handlers.list_entity_sets()
    metadata_hits = [r for r in wired_infobase.requests if r["path"].endswith("/$metadata")]
    assert len(metadata_hits) == 1


async def test_resource_entity_sets(wired_infobase):
    text = await handlers.resource_entity_sets()
    assert "Catalog_Товары" in text
