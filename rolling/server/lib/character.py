# coding: utf-8
import typing
import uuid

from rolling.model.character import CharacterModel
from rolling.model.character import CreateCharacterModel
from rolling.model.stuff import CharacterInventoryModel
from rolling.server.controller.url import TAKE_STUFF_URL
from rolling.server.document.character import CharacterDocument
from rolling.server.lib.action import CharacterAction
from rolling.server.lib.stuff import StuffLib

if typing.TYPE_CHECKING:
    from rolling.kernel import Kernel


class CharacterLib:
    def __init__(
        self, kernel: "Kernel", stuff_lib: typing.Optional[StuffLib] = None
    ) -> None:
        self._kernel = kernel
        self._stuff_lib: StuffLib = stuff_lib or StuffLib(kernel)

    def create(self, create_character_model: CreateCharacterModel) -> str:
        character = CharacterDocument()
        character.id = uuid.uuid4().hex
        character.name = create_character_model.name
        character.background_story = create_character_model.background_story
        character.hunting_and_collecting_comp = (
            create_character_model.hunting_and_collecting_comp
        )
        character.find_water_comp = create_character_model.find_water_comp
        character.max_life_comp = create_character_model.max_life_comp

        # Place on zone
        world_row_i, world_col_i = self._kernel.get_start_world_coordinates()
        zone_row_i, zone_col_i = self._kernel.get_start_zone_coordinates(
            world_row_i, world_col_i
        )

        character.world_row_i = world_row_i
        character.world_col_i = world_col_i
        character.zone_row_i = zone_row_i
        character.zone_col_i = zone_col_i

        self._kernel.server_db_session.add(character)
        self._kernel.server_db_session.commit()
        return character.id

    def get_document(self, id_: str) -> CharacterDocument:
        return (
            self._kernel.server_db_session.query(CharacterDocument)
            .filter(CharacterDocument.id == id_)
            .one()
        )

    def _document_to_model(
        self, character_document: CharacterDocument
    ) -> CharacterModel:
        return CharacterModel(
            id=character_document.id,
            name=character_document.name,
            world_col_i=character_document.world_col_i,
            world_row_i=character_document.world_row_i,
            zone_col_i=character_document.zone_col_i,
            zone_row_i=character_document.zone_row_i,
            background_story=character_document.background_story,
            max_life_comp=float(character_document.max_life_comp),
            hunting_and_collecting_comp=float(
                character_document.hunting_and_collecting_comp
            ),
            find_water_comp=float(character_document.find_water_comp),
        )

    def get(self, id_: str) -> CharacterModel:
        character_document = self.get_document(id_)
        return self._document_to_model(character_document)

    def move_on_zone(
        self, character: CharacterModel, to_row_i: int, to_col_i: int
    ) -> None:
        character_document = self.get_document(character.id)
        character_document.zone_row_i = to_row_i
        character_document.zone_col_i = to_col_i
        self._kernel.server_db_session.add(character_document)
        self._kernel.server_db_session.commit()

    def get_zone_players(self, row_i: int, col_i: int) -> typing.List[CharacterModel]:
        character_documents = (
            self._kernel.server_db_session.query(CharacterDocument)
            .filter(CharacterDocument.world_row_i == row_i)
            .filter(CharacterDocument.world_col_i == col_i)
            .all()
        )

        return [
            self._document_to_model(character_document)
            for character_document in character_documents
        ]

    def move(
        self, character: CharacterModel, to_world_row: int, to_world_col: int
    ) -> None:
        # TODO BS 2019-06-04: Check if move is possible
        # TODO BS 2019-06-04: Compute how many action point and consume
        character_document = self.get_document(character.id)
        character_document.world_row_i = to_world_row
        character_document.world_col_i = to_world_col
        self.update(character_document)

    def update(
        self, character_document: CharacterDocument, commit: bool = True
    ) -> None:
        self._kernel.server_db_session.add(character_document)
        if commit:
            self._kernel.server_db_session.commit()

    def get_all_character_count(self) -> int:
        return self._kernel.server_db_session.query(CharacterDocument.id).count()

    def get_all_character_ids(self) -> typing.Iterable[str]:
        return (
            row[0]
            for row in self._kernel.server_db_session.query(CharacterDocument.id).all()
        )

    def get_inventory(self, character_id: str) -> CharacterInventoryModel:
        carried_stuff = self._stuff_lib.get_carried_by(character_id)
        total_weight = sum([stuff.weight for stuff in carried_stuff])
        total_clutter = sum([stuff.clutter for stuff in carried_stuff])
        return CharacterInventoryModel(
            stuff=carried_stuff, weight=total_weight, clutter=total_clutter
        )

    def get_on_place_actions(self, character_id: str) -> typing.List[CharacterAction]:
        character_doc = self.get_document(character_id)
        character_actions: typing.List[CharacterAction] = []

        # First, search action with near items
        on_same_position_items = self._stuff_lib.get_zone_stuffs(
            world_row_i=character_doc.world_row_i,
            world_col_i=character_doc.world_col_i,
            zone_row_i=character_doc.zone_row_i,
            zone_col_i=character_doc.zone_col_i,
        )
        for item in on_same_position_items:
            character_actions.append(
                CharacterAction(
                    name=f"Take {item.get_name_and_light_description()}",
                    link=TAKE_STUFF_URL.format(
                        character_id=character_id, stuff_id=item.id
                    ),
                )
            )

        return character_actions

    def take_stuff(self, character_id: str, stuff_id: int) -> None:
        self._stuff_lib.set_carried_by(stuff_id=stuff_id, character_id=character_id)
