# coding: utf-8
import dataclasses
import enum
import typing

from guilang.description import Description
from guilang.description import Part
from rolling.map.type.zone import ZoneMapTileType
from rolling.model.measure import Unit
from rolling.rolling_types import ActionType
from rolling.server.link import CharacterActionLink

if typing.TYPE_CHECKING:
    from rolling.kernel import Kernel
    from rolling.model.stuff import StuffModel
    from rolling.model.character import CharacterModel
    from rolling.map.source import ZoneMapSource


@dataclasses.dataclass
class EmptyModel:
    pass


def get_on_and_around_coordinates(x: int, y: int) -> typing.List[typing.Tuple[int, int]]:
    return [
        (x, y),
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        (x - 1, y),
        (x + 1, y),
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    ]


def is_there_resource_id_in_zone(
    kernel: "Kernel", resource_id: str, zone_source: "ZoneMapSource"
) -> bool:
    for row in zone_source.geography.rows:
        for zone_tile_type in row:
            zone_tile_type = typing.cast(typing.Type[ZoneMapTileType], zone_tile_type)

            try:
                for tile_resource_id in list(
                    # FIXME BS 2019-09-14: Only for zero cost !
                    kernel.game.config.extractions[zone_tile_type.id].resources.keys()
                ):
                    if tile_resource_id == resource_id:
                        return True
            except KeyError:
                pass

    return False


def get_stuffs_filled_with_resource_id(
    kernel: "Kernel", character_id: str, resource_id: str
) -> typing.Iterator["StuffModel"]:
    from rolling.server.lib.stuff import StuffLib

    stuff_lib = StuffLib(kernel=kernel)
    character_stuffs = stuff_lib.get_carried_by(character_id)
    for stuff in character_stuffs:
        # FIXME BS 2019-07-10: case where not 100% ?
        if stuff.filled_with_resource == resource_id:
            yield stuff


def get_stuffs_eatable(kernel: "Kernel", character_id: str) -> typing.Iterator["StuffModel"]:
    for stuff in kernel.stuff_lib.get_carried_by(character_id):
        stuff_properties = kernel.game.stuff_manager.get_stuff_properties_by_id(stuff.stuff_id)
        for description in stuff_properties.descriptions:
            if description.action_type == ActionType.EAT_STUFF:
                yield stuff


class CornerEnum(enum.Enum):
    TOP = "TOP"
    TOP_RIGHT = "TOP_RIGHT"
    RIGHT = "RIGHT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    BOTTOM = "BOTTOM"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    LEFT = "LEFT"
    TOP_LEFT = "TOP_LEFT"


def get_opposite_zone_place(from_: CornerEnum, zone_width: int, zone_height: int) -> (int, int):
    width_part_len = zone_width // 3
    half_width_part_len = width_part_len // 2
    height_part_len = zone_height // 3
    half_height_part_len = height_part_len // 2

    if from_ == CornerEnum.TOP:
        return 0, zone_width // 2

    if from_ == CornerEnum.TOP_RIGHT:
        return (height_part_len * 2) + half_height_part_len, half_width_part_len + 1

    if from_ == CornerEnum.RIGHT:
        return zone_height // 2, zone_width - 1

    if from_ == CornerEnum.BOTTOM_RIGHT:
        return (
            (height_part_len * 2) + half_height_part_len,
            (width_part_len * 2) + half_width_part_len - 1,
        )

    if from_ == CornerEnum.BOTTOM:
        return zone_height - 1, zone_width // 2

    if from_ == CornerEnum.BOTTOM_LEFT:
        return half_height_part_len, ((width_part_len * 2) + half_width_part_len - 1)

    if from_ == CornerEnum.LEFT:
        return zone_height // 2, 0

    if from_ == CornerEnum.TOP_LEFT:
        return half_height_part_len, half_width_part_len + 1

    raise Exception("It is not possible !")


def get_coming_from(
    before_row_i: int, before_col_i: int, after_row_i: int, after_col_i: int
) -> CornerEnum:
    if after_row_i == before_row_i - 1 and after_col_i == before_col_i:
        return CornerEnum.BOTTOM

    if after_row_i == before_row_i - 1 and after_col_i == before_col_i + 1:
        return CornerEnum.TOP_RIGHT

    if after_row_i == before_row_i and after_col_i == before_col_i + 1:
        return CornerEnum.LEFT

    if after_row_i == before_row_i + 1 and after_col_i == before_col_i + 1:
        return CornerEnum.TOP_LEFT

    if after_row_i == before_row_i + 1 and after_col_i == before_col_i:
        return CornerEnum.TOP

    if after_row_i == before_row_i - 1 and after_col_i == before_col_i - 1:
        return CornerEnum.BOTTOM_RIGHT

    if after_row_i == before_row_i and after_col_i == before_col_i - 1:
        return CornerEnum.RIGHT

    if after_row_i == before_row_i + 1 and after_col_i == before_col_i - 1:
        return CornerEnum.BOTTOM_LEFT

    raise Exception("It is not possible !")


def get_corner(
    width: int, height: int, new_row_i: int, new_col_i: int
) -> typing.Optional[CornerEnum]:
    left_col_i_end = width // 3
    right_col_i_start = (width // 3) * 2
    top_row_i_end = height // 3
    bottom_row_i_start = (height // 3) * 2

    more = new_row_i if new_row_i >= 0 else 0

    if new_row_i < top_row_i_end:
        right_col_i = right_col_i_start + more
        left_col_i = left_col_i_end - more
    elif new_row_i >= bottom_row_i_start:
        more = (height // 3) - (new_row_i - bottom_row_i_start + 1)
        more = more if more >= 0 else 0
        right_col_i = right_col_i_start + more
        left_col_i = left_col_i_end - more
    else:
        left_col_i = left_col_i_end
        right_col_i = right_col_i_start

    if new_col_i < left_col_i and new_row_i < top_row_i_end:
        return CornerEnum.TOP_LEFT

    if new_row_i < 0 and left_col_i <= new_col_i < right_col_i:
        return CornerEnum.TOP

    if new_col_i >= right_col_i and new_row_i < top_row_i_end:
        return CornerEnum.TOP_RIGHT

    if new_col_i > (width - 1) and top_row_i_end <= new_row_i < bottom_row_i_start:
        return CornerEnum.RIGHT

    if new_col_i >= right_col_i and new_row_i >= bottom_row_i_start:
        return CornerEnum.BOTTOM_RIGHT

    if new_row_i > (height - 1) and left_col_i_end <= new_col_i < right_col_i_start:
        return CornerEnum.BOTTOM

    if new_col_i < left_col_i and new_row_i >= bottom_row_i_start:
        return CornerEnum.BOTTOM_LEFT

    if new_col_i < 0 and top_row_i_end <= new_row_i < bottom_row_i_start:
        return CornerEnum.LEFT


def filter_action_links(
    links: typing.List[CharacterActionLink]
) -> typing.List[CharacterActionLink]:
    new_links: typing.List[CharacterActionLink] = []
    found_merge_type: typing.List[typing.Any] = []

    for link in links:
        if link.merge_by is None:
            new_links.append(link)
        else:
            if link.merge_by not in found_merge_type:
                new_links.append(link)
                found_merge_type.append(link.merge_by)

    return new_links


def display_g_or_kg(grams: float) -> str:
    if grams < 1000:
        return f"{grams} g"
    return f"{round(grams/1000, 3)} kg"


def quantity_to_str(quantity: float, unit: Unit, kernel: "Kernel") -> str:
    if unit == Unit.GRAM:
        return display_g_or_kg(quantity)
    unit_str = kernel.translation.get(unit)
    quantity = int(quantity) if unit == Unit.UNIT else float(quantity)
    return f"{str(quantity)} {unit_str}"


def get_description_for_not_enough_ap(
    character: "CharacterModel", cost: float, can_be_back_url: bool = False
) -> Description:
    return Description(
        title="Action impossible",
        items=[
            Part(
                text=f"{character.name} ne possède plus assez de points d'actions "
                f"({character.action_points} restant et {cost} nécessaires)"
            ),
            Part(is_link=True, go_back_zone=True, label="Retourner à l'écran de déplacements"),
        ],
        can_be_back_url=can_be_back_url,
    )


# FIXME BS: replace by iterator on eatable object (to manage all case like invent friends)
def character_can_drink_in_its_zone(kernel: "Kernel", character: "CharacterModel") -> bool:
    # TODO: consider path finding
    zone_source = kernel.tile_maps_by_position[
        (character.world_row_i, character.world_col_i)
    ].source
    return is_there_resource_id_in_zone(
        kernel, kernel.game.config.fresh_water_resource_id, zone_source
    )


def get_character_stuff_filled_with_water(
    kernel: "Kernel", character_id: str
) -> typing.Optional["StuffModel"]:
    try:
        return next(
            get_stuffs_filled_with_resource_id(
                kernel, character_id, kernel.game.config.fresh_water_resource_id
            )
        )
    except StopIteration:
        pass


clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
