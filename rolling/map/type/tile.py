# coding: utf-8
import typing

from rolling.map.type.base import MapTileType


class TileMapTileType(MapTileType):
    _list_cache: typing.Dict[str, typing.Type["TileMapTileType"]] = None
    _full_id_pattern = "TILE__{}"

    @classmethod
    def get_all(cls) -> typing.Dict[str, typing.Type["TileMapTileType"]]:
        if cls._list_cache is None:
            cls._list_cache = {
                Nothing.id: Nothing,
                Sand.id: Sand,
                DryBush.id: DryBush,
                Rock.id: Rock,
                SeaWater.id: SeaWater,
            }

        return cls._list_cache


class Nothing(TileMapTileType):
    id = "NOTHING"


class Sand(TileMapTileType):
    id = "SAND"
    foreground_high_color = "#fa0"


class DryBush(TileMapTileType):
    id = "DRY BUSH"
    foreground_high_color = "#860"


class Rock(TileMapTileType):
    id = "ROCK"
    foreground_high_color = "g35"


class SeaWater(TileMapTileType):
    id = "SEA WATER"
    foreground_high_color = "#06f"
    background_high_color = "#006"