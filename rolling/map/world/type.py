# coding: utf-8
import typing


class WorldMapTileType(object):
    _list_cache: typing.Dict[str, typing.Type["WorldMapTileType"]] = None

    id = NotImplemented
    foreground_color = "white"
    background_color = ""
    mono = ""
    foreground_high_color = ""
    background_high_color = "#000"

    @classmethod
    def get_all(cls) -> typing.Dict[str, typing.Type["WorldMapTileType"]]:
        if cls._list_cache is None:
            cls._list_cache = {
                Sea.id: Sea,
                Mountain.id: Mountain,
                Jungle.id: Jungle,
                Hill.id: Hill,
                Beach.id: Beach,
                Plain.id: Plain,
            }

        return cls._list_cache

    @classmethod
    def get_for_id(cls, id_: str) -> typing.Type["WorldMapTileType"]:
        return cls.get_all()[id_]

    @classmethod
    def get_full_id(cls) -> str:
        return "WORLD_TILE__{}".format(cls.id)


class Sea(WorldMapTileType):
    id = "SEA"
    foreground_high_color = "#06f"
    background_high_color = "#006"


class Mountain(WorldMapTileType):
    id = "MOUNTAIN"
    foreground_color = ""
    background_color = ""
    mono = ""
    foreground_high_color = "#860"


class Jungle(WorldMapTileType):
    id = "JUNGLE"
    foreground_high_color = "#060"


class Hill(WorldMapTileType):
    id = "HILL"
    foreground_high_color = "#660"


class Beach(WorldMapTileType):
    id = "BEACH"
    foreground_high_color = "#fa0"


class Plain(WorldMapTileType):
    id = "PLAIN"
    foreground_high_color = "#fda"