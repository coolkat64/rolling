# coding: utf-8
import typing
import uuid

from rolling.model.character import CharacterModel
from rolling.model.character import CreateCharacterModel
from rolling.model.resource import ResourceType
from rolling.model.stuff import CharacterInventoryModel
from rolling.server.controller.url import DESCRIBE_LOOT_AT_STUFF_URL
from rolling.server.controller.url import TAKE_STUFF_URL
from rolling.server.document.character import CharacterDocument
from rolling.server.lib.action import ActionFactory
from rolling.server.lib.stuff import StuffLib
from rolling.server.link import CharacterActionLink

if typing.TYPE_CHECKING:
    from rolling.kernel import Kernel


class CharacterLib:
    def __init__(
        self, kernel: "Kernel", stuff_lib: typing.Optional[StuffLib] = None
    ) -> None:
        self._kernel = kernel
        self._stuff_lib: StuffLib = stuff_lib or StuffLib(kernel)
        self._action_factory = ActionFactory(kernel)

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

    def get_document_by_name(self, name: str) -> CharacterDocument:
        return (
            self._kernel.server_db_session.query(CharacterDocument)
            .filter(CharacterDocument.name == name)
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
            feel_thirsty=character_document.feel_thirsty,
            dehydrated=character_document.dehydrated,
        )

    def get(self, id_: str) -> CharacterModel:
        character_document = self.get_document(id_)
        return self._document_to_model(character_document)

    def get_by_name(self, name: str) -> CharacterModel:
        character_document = self.get_document_by_name(name)
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
        total_weight = sum([stuff.weight for stuff in carried_stuff if stuff.weight])
        total_clutter = sum([stuff.clutter for stuff in carried_stuff])
        return CharacterInventoryModel(
            stuff=carried_stuff, weight=total_weight, clutter=total_clutter
        )

    def get_on_place_actions(
        self, character_id: str
    ) -> typing.List[CharacterActionLink]:
        character = self.get(character_id)
        character_actions_: typing.List[CharacterActionLink] = []

        # Actions with near items
        on_same_position_items = self._stuff_lib.get_zone_stuffs(
            world_row_i=character.world_row_i,
            world_col_i=character.world_col_i,
            zone_row_i=character.zone_row_i,
            zone_col_i=character.zone_col_i,
        )
        for item in on_same_position_items:
            character_actions_.append(
                CharacterActionLink(
                    name=f"Take a look on {item.name}",
                    link=DESCRIBE_LOOT_AT_STUFF_URL.format(
                        character_id=character_id, stuff_id=item.id
                    ),
                )
            )

        # Actions with available character actions
        for action in self._action_factory.get_all_character_actions():
            character_actions_.extend(action.get_character_actions(character))

        return character_actions_

    def get_on_stuff_actions(
        self, character_id: str, stuff_id: int
    ) -> typing.List[CharacterActionLink]:
        stuff = self._stuff_lib.get_stuff(stuff_id)
        character = self.get(character_id)
        character_actions: typing.List[CharacterActionLink] = []

        if stuff.carried_by is None:
            character_actions.append(
                CharacterActionLink(
                    name=f"Take {stuff.get_name_and_light_description()}",
                    link=TAKE_STUFF_URL.format(
                        character_id=character_id, stuff_id=stuff.id
                    ),
                )
            )
        elif stuff.carried_by == character_id:
            character_actions.extend(
                self._stuff_lib.get_carrying_actions(character, stuff)
            )

        return character_actions

    def take_stuff(self, character_id: str, stuff_id: int) -> None:
        self._stuff_lib.set_carried_by(stuff_id=stuff_id, character_id=character_id)

    def drink_material(self, character_id: str, resource_type: ResourceType) -> str:
        character_doc = self.get_document(character_id)

        if not character_doc.feel_thirsty:
            return "You are not thirsty"

        if resource_type == ResourceType.FRESH_WATER:
            character_doc.dehydrated = False
            character_doc.feel_thirsty = False
            self._kernel.server_db_session.add(character_doc)
            self._kernel.server_db_session.commit()
            return "You're no longer thirsty"
        elif resource_type == ResourceType.SALTED_WATER:
            return "It's unbearable"

        # TODO BS 2019-07-06: Move logic otherwise to be able to describe effect in game config ?
        return "It's not a good idea"

    def drink_stuff(self, character_id: str, stuff_id: int) -> str:
        character_doc = self.get_document(character_id)
        stuff_doc = self._stuff_lib.get_stuff_doc(stuff_id)
        stuff_properties = self._kernel.game.stuff_manager.get_stuff_properties_by_id(
            stuff_doc.stuff_id
        )

        if not character_doc.feel_thirsty:
            return "You are not thirsty"

        # TODO BS 2019-07-09: manage case where not 100% filled
        if stuff_doc.filled_at == 100.0:
            stuff_doc.empty(stuff_properties)
            self._kernel.server_db_session.add(stuff_doc)

            character_doc.feel_thirsty = False
            character_doc.dehydrated = False

            self._kernel.server_db_session.commit()
            return "You're no longer thirsty"

        return "Woops, it is not yest implemented"
