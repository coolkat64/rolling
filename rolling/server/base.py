# coding: utf-8
import asyncio
import typing

from rolling.kernel import Kernel
from rolling.log import server_logger


def get_kernel(
    world_map_source_path: typing.Optional[str] = None,
    tile_maps_folder_path: typing.Optional[str] = None,
    game_config_folder: typing.Optional[str] = None,
    server_db_path: str = "server.db",
) -> Kernel:
    world_map_source_raw = None

    if world_map_source_path:
        server_logger.info('Read world map source file "{}"'.format(world_map_source_path))
        with open(world_map_source_path, "r") as f:
            world_map_source_raw = f.read()

    if tile_maps_folder_path:
        server_logger.info('Start kernel with tile maps folder "{}"'.format(tile_maps_folder_path))

    loop = asyncio.get_event_loop()
    kernel = Kernel(
        world_map_source_raw,
        loop=loop,
        tile_maps_folder=tile_maps_folder_path,
        game_config_folder=game_config_folder,
        server_db_path=server_db_path,
    )

    kernel.init_server_db_session()
    return kernel
