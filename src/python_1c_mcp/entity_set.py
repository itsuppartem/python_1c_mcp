"""Generic entity-set access by full OData name (Catalog_*, Document_*, ...)."""

from __future__ import annotations

from python_1c_odata.client import Infobase
from python_1c_odata.entity import EntitySet


class NamedEntitySet(EntitySet):
    """Query any published entity set using its full name (e.g. ``Catalog_Товары``)."""

    kind = ""

    def __init__(self, infobase: Infobase, full_name: str) -> None:
        super().__init__(infobase, full_name)

    @property
    def entity(self) -> str:
        return self.name
