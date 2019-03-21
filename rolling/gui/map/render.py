# coding: utf-8
import typing

from rolling.exception import NoDefaultTileType
from rolling.exception import TileTypeNotFound
from rolling.gui.map.object import DisplayObject
from rolling.gui.map.object import DisplayObjectManager
from rolling.map.source import MapSource
from rolling.map.type.zone import Nothing

WORLD_VOID_STR = " "


class MapRenderEngine(object):
    def __init__(
        self, world_map_source: MapSource, display_objects_manager: DisplayObjectManager
    ) -> None:
        self._world_map_source = world_map_source
        self._rows: typing.List[str] = None
        self._attributes: typing.List[
            typing.List[typing.Tuple[typing.Optional[str], int]]
        ] = None
        self._display_objects_manager = display_objects_manager

    @property
    def rows(self) -> typing.List[str]:
        return self._rows

    @property
    def attributes(self):
        return self._attributes

    @property
    def display_objects_manager(self) -> DisplayObjectManager:
        return self._display_objects_manager

    @property
    def display_objects(self) -> typing.List[DisplayObject]:
        return self._display_objects_manager.display_objects

    @display_objects.setter
    def display_objects(self, display_objects: typing.List[DisplayObject]) -> None:
        self._display_objects_manager.display_objects = display_objects

    def render(
        self,
        width: int,
        height: int,
        offset_horizontal: int = 0,
        offset_vertical: int = 0,
    ) -> None:
        map_width = self._world_map_source.geography.width
        map_height = self._world_map_source.geography.height
        map_rows = self._world_map_source.geography.rows
        map_legend = self._world_map_source.legend

        # Build map tile coordinates
        matrix: typing.List[typing.List[typing.Tuple[int, int]]] = [
            [(None, None) for i in range(width)] for ii in range(height)
        ]
        for screen_row_i in range(height):
            for screen_col_i in range(width):
                map_row_i = screen_row_i - offset_vertical
                map_col_i = screen_col_i - offset_horizontal

                matrix[screen_row_i][screen_col_i] = map_row_i, map_col_i

        # Build maps chars
        screen_chars: typing.List[str] = ["" for i in range(height)]
        for screen_row_i, row in enumerate(matrix):
            for map_row_i, map_col_i in row:
                # If it is outside map, use empty tile
                if map_row_i < 0 or map_row_i > (map_height - 1) or map_col_i < 0 or map_col_i > (map_width - 1):
                    tile_type = Nothing
                else:
                    tile_type = map_rows[map_row_i][map_col_i]

                tile_chars = map_legend.get_str_with_type(tile_type)
                screen_chars[screen_row_i] += tile_chars

        # Build attributes
        self._attributes = [None] * height
        for screen_row_i, row in enumerate(screen_chars):
            last_seen_char = None
            self._attributes[screen_row_i] = []

            for screen_col_i, char in enumerate(row):
                if last_seen_char != char:
                    try:
                        tile_type = map_legend.get_type_with_str(char)
                        self._attributes[screen_row_i].append(
                            (tile_type.get_full_id(), len(char.encode()))
                        )
                    except TileTypeNotFound:
                        self._attributes[screen_row_i].append((None, len(char.encode())))
                else:
                    self._attributes[screen_row_i][-1] = (
                        self._attributes[screen_row_i][-1][0],
                        self._attributes[screen_row_i][-1][1] + len(char.encode()),
                    )
                last_seen_char = char

        # Encore each rows
        self._rows = [None] * height
        for screen_row_i, row in enumerate(screen_chars):
            self._rows[screen_row_i] = row.encode()

        return



        map_width = self._world_map_source.geography.width
        map_height = self._world_map_source.geography.height

        try:
            default_type = self._world_map_source.legend.get_default_type()
            default_str = self._world_map_source.legend.get_str_with_type(default_type)
        except NoDefaultTileType:
            default_str = WORLD_VOID_STR

        # compute static void left and right
        width_difference = width - map_width
        if width_difference > 1:
            left_void = width_difference // 2
            right_void = left_void + 1 if width_difference % 2 else left_void
            left_void = left_void + offset_horizontal
            right_void = right_void - offset_horizontal
        elif width_difference == 1:
            left_void = 1 + offset_horizontal
            right_void = 0 - offset_horizontal
        else:
            left_void = 0 + offset_horizontal
            right_void = 0 - offset_horizontal

        # Prevent left void superior of width
        if left_void > width:
            left_void = width

        # compute static void top and bottom
        height_difference = height - map_height
        if height_difference > 1:
            top_void = height_difference // 2
            bottom_void = top_void + 1 if height_difference % 2 else top_void
            top_void = top_void + offset_vertical
            bottom_void = bottom_void - offset_vertical
        elif height_difference == 1:
            top_void = 1 + offset_vertical
            bottom_void = 0 - offset_vertical
        elif height_difference < 0:
            top_void = offset_vertical
            bottom_void = 0
        else:
            top_void = 0 + offset_vertical
            bottom_void = 0 - offset_vertical

        if bottom_void > height:
            bottom_void = height

        if top_void > height:
            top_void = height

        # prepare void values
        self._rows = [default_str * width] * top_void
        map_display_height = map_height
        if map_display_height > height:
            map_display_height = height

        self._rows.extend([default_str * left_void] * map_display_height)
        self._rows.extend([default_str * width] * bottom_void)
        self._attributes: typing.List[
            typing.List[typing.Tuple[typing.Optional[str], int]]
        ] = []

        # fill rows and attributes line per line
        for row_i, row in enumerate(self._world_map_source.geography.rows):
            row_left_void = left_void
            row_right_void = right_void

            if (row_i + top_void) < 0:
                continue

            # do not fill outside screen
            if row_i + top_void + 1 > height:
                break

            for col_i, col in enumerate(row):

                # do not fill outside screen
                if col_i == width:
                    break

                # Avoid char if left void need to suppress it
                if row_left_void < 0:
                    row_left_void += 1
                    continue

                # Avoid chars if right void need to suppress them
                if row_right_void < 0:
                    if col_i == len(row) + row_right_void:
                        break

                # line already completely filled
                if len(self._rows[row_i + top_void]) >= width:
                    break

                tile_str = self._world_map_source.legend.get_str_with_type(col)
                final_str = self._display_objects_manager.get_final_str(
                    row_i, col_i, tile_str
                )
                self._rows[row_i + top_void] += final_str
                # self._rows[row_i+top_void] += u'a'

        # fill right
        fill_top_void = top_void
        if top_void < 0:
            fill_top_void = 0
        for row_i, row in enumerate(
            self._rows[fill_top_void : len(self._rows) - bottom_void],
            start=fill_top_void,
        ):
            self._rows[row_i] += default_str * (width - len(self._rows[row_i]))

        # cut if more height
        self._rows = self._rows[0:height]

        # compute attributes
        for row_i, row in enumerate(self._rows):
            last_seen_char = None
            self._attributes.append([])

            for col_i, char in enumerate(row):
                if last_seen_char != char:
                    # First try with objects
                    try:
                        # FIXME BS 2018-12-27: Must select currently displayed object
                        obj = self._display_objects_manager.objects_by_position[
                            (row_i, col_i - left_void)
                        ][0]
                        self._attributes[row_i].append(
                            (obj.palette_id, len(obj.char.encode()))
                        )
                        continue
                    except KeyError:
                        pass

                    try:
                        # FIXME BS 2018-12-23: it can be display object
                        tile_type = self._world_map_source.legend.get_type_with_str(
                            char
                        )
                        self._attributes[row_i].append(
                            (tile_type.get_full_id(), len(char.encode()))
                        )
                    except TileTypeNotFound:
                        self._attributes[row_i].append((None, len(char.encode())))
                else:
                    self._attributes[row_i][-1] = (
                        self._attributes[row_i][-1][0],
                        self._attributes[row_i][-1][1] + len(char.encode()),
                    )
                last_seen_char = char

        # encode
        for row_i, row in enumerate(self._rows):
            self._rows[row_i] = row.encode()


class WorldMapRenderEngine(MapRenderEngine):
    pass


class TileMapRenderEngine(MapRenderEngine):
    pass
