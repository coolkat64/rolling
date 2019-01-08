# coding: utf-8
import typing

import dataclasses
from rolling.model.meta import TransportType


@dataclasses.dataclass
class TileTypeModel(object):
    id: str
    foreground_color: str
    background_color: str
    mono: str
    foreground_high_color: str
    background_high_color: str


@dataclasses.dataclass
class WorldMapTileTypeModel(TileTypeModel):
    pass


@dataclasses.dataclass
class ZoneTileModel(object):
    id: str
    char: str
    traversable: typing.Optional[typing.Dict[TransportType, bool]]
