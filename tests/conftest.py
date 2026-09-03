"""Local stand-in for a published 1C infobase."""

from __future__ import annotations

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from python_1c_odata import Infobase


class FakeOData:
    def __init__(self) -> None:
        self.requests: list[dict] = []
        self._next: tuple[int, object, str | None] = (200, {"value": []}, None)
        self._queue: list[tuple[int, object, str | None]] = []
        self.base_url = ""

    def respond(self, status: int, payload: object, *, content_type: str | None = None) -> None:
        self._queue = []
        self._next = (status, payload, content_type)

    async def handle(self, request: web.Request) -> web.StreamResponse:
        self.requests.append(
            {
                "method": request.method,
                "path": request.path,
                "query": request.query_string,
            }
        )
        status, payload, content_type = self._next
        if isinstance(payload, (bytes, str)):
            text = payload.decode() if isinstance(payload, bytes) else payload
            return web.Response(
                status=status, text=text, content_type=content_type or "application/json"
            )
        return web.json_response(payload, status=status)


_METADATA = """<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx Version="1.0" xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx">
  <edmx:DataServices xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
      m:DataServiceVersion="3.0">
    <Schema Namespace="StandardODATA" xmlns="http://schemas.microsoft.com/ado/2009/11/edm">
      <EntityType Name="Catalog_Товары">
        <Key><PropertyRef Name="Ref_Key"/></Key>
        <Property Name="Ref_Key" Type="Edm.Guid" Nullable="false"/>
        <Property Name="Description" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="StandardODATA">
        <EntitySet Name="Catalog_Товары" EntityType="StandardODATA.Catalog_Товары"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


@pytest.fixture
def metadata_xml() -> str:
    return _METADATA


@pytest.fixture
async def fake_odata():
    fake = FakeOData()
    app = web.Application()
    app.router.add_route("*", "/{path:.*}", fake.handle)
    server = TestServer(app)
    await server.start_server()
    fake.base_url = str(server.make_url("/")).rstrip("/")
    yield fake
    await server.close()


@pytest.fixture
async def infobase(fake_odata):
    ib = Infobase(fake_odata.base_url, "ut", "user", "secret")
    async with ib:
        yield ib


@pytest.fixture(autouse=True)
def _reset_connection_state(monkeypatch):
    import python_1c_mcp.connection as conn

    conn._infobase = None
    conn._config = None
    monkeypatch.delenv("ONEC_URL", raising=False)
    monkeypatch.delenv("ONEC_SERVER", raising=False)
    monkeypatch.delenv("ONEC_INFOBASE", raising=False)
    monkeypatch.delenv("ONEC_USER", raising=False)
    monkeypatch.delenv("ONEC_PASSWORD", raising=False)
    yield
    conn._infobase = None
    conn._config = None
