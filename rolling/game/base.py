# coding: utf-8
from os import path
import typing

import toml

from rolling.game.stuff import StuffManager
from rolling.game.world import WorldManager
from rolling.map.type.world import WorldMapTileType
from rolling.model.action import ActionProperties
from rolling.model.stuff import StuffProperties
from rolling.model.stuff import ZoneGenerationStuff
from rolling.model.types import MaterialType
from rolling.model.world import World
from rolling.model.zone import GenerationInfo
from rolling.model.zone import ZoneProperties
from rolling.types import ActionType

if typing.TYPE_CHECKING:
    from rolling.kernel import Kernel


class GameConfig:
    def __init__(self, config_dict: dict) -> None:
        self.action_points_per_turn: int = config_dict["action_points_per_turn"]
        self.create_character_messages: typing.List[str] = config_dict[
            "create_character_messages"
        ]


class Game:
    def __init__(self, kernel: "Kernel", config_folder: str) -> None:
        self._kernel = kernel
        self._stuff = self._create_stuff_manager(path.join(config_folder, "stuff.toml"))
        self._world = self._create_world_manager(path.join(config_folder, "world.toml"))
        self._config = GameConfig(toml.load(path.join(config_folder, "game.toml")))

    @property
    def config(self) -> GameConfig:
        return self._config

    @property
    def stuff_manager(self) -> StuffManager:
        return self._stuff

    @property
    def world_manager(self) -> WorldManager:
        return self._world

    def _create_stuff_manager(self, stuff_file_path: str) -> StuffManager:
        items: typing.List[StuffProperties] = []
        raw_stuffs = toml.load(stuff_file_path)

        for stuff_id, stuff_info in raw_stuffs.items():
            full_info = dict(stuff_info)
            full_info.update({"id": stuff_id})
            full_info["material_type"] = full_info.get("material_type", None)

            full_info["action_properties"] = [
                ActionProperties(
                    type_=ActionType(a["type"]),
                    acceptable_material_types=[
                        MaterialType(t) for t in a.get("acceptable_material_types", [])
                    ],
                )
                for a in full_info.get("action_properties", [])
            ]

            items.append(StuffProperties(**full_info))

        return StuffManager(self._kernel, items)

    def _create_world_manager(self, world_file_path: str) -> WorldManager:
        raw_world = toml.load(world_file_path)
        zones_properties: typing.List[ZoneProperties] = []

        for zone_type_str, zone_data in raw_world.get("ZONE_PROPERTIES", {}).items():

            # Stuff generation part
            generation_data = zone_data["GENERATION"]
            count: int = generation_data["count"]

            stuffs: typing.List[ZoneGenerationStuff] = []
            for stuff_id, stuff_generation_info in generation_data.get(
                "STUFF", {}
            ).items():
                probability = stuff_generation_info["probability"]
                meta = dict(
                    [
                        item
                        for item in stuff_generation_info.items()
                        if item[0] not in ["probability"]
                    ]
                )
                stuff = self._stuff.get_stuff_properties_by_id(stuff_id)
                stuffs.append(
                    ZoneGenerationStuff(stuff=stuff, probability=probability, meta=meta)
                )

            generation_info = GenerationInfo(count=count, stuffs=stuffs)
            zones_properties.append(
                ZoneProperties(
                    WorldMapTileType.get_for_id(zone_type_str), generation_info
                )
            )

        return WorldManager(self._kernel, World(zones_properties=zones_properties))
