# coding: utf-8
import typing

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.elements import and_

from rolling.exception import NoCarriedResource
from rolling.exception import NotEnoughResource
from rolling.model.character import CharacterModel
from rolling.model.effect import CharacterEffectDescriptionModel
from rolling.model.measure import Unit
from rolling.model.resource import CarriedResourceDescriptionModel
from rolling.model.resource import ResourceDescriptionModel
from rolling.server.action import ActionFactory
from rolling.server.document.resource import ResourceDocument
from rolling.server.link import CharacterActionLink

if typing.TYPE_CHECKING:
    from rolling.kernel import Kernel


class ResourceLib:
    def __init__(self, kernel: "Kernel") -> None:
        self._kernel = kernel
        self._action_factory = ActionFactory(kernel)

    def add_resource_to_character(
        self, character_id: str, resource_id: str, quantity: float, commit: bool = True
    ) -> CarriedResourceDescriptionModel:
        resource_description: ResourceDescriptionModel = self._kernel.game.config.resources[
            resource_id
        ]
        try:
            resource = (
                self._kernel.server_db_session.query(ResourceDocument)
                .filter(
                    and_(
                        ResourceDocument.carried_by_id == character_id,
                        ResourceDocument.resource_id == resource_id,
                    )
                )
                .one()
            )
        except NoResultFound:
            resource = ResourceDocument(
                resource_id=resource_id,
                carried_by_id=character_id,
                quantity=0.0,
                unit=resource_description.unit.value,
            )

        resource.quantity = float(resource.quantity) + quantity
        self._kernel.server_db_session.add(resource)

        if commit:
            self._kernel.server_db_session.commit()

        return self._carried_resource_model_from_doc(resource)

    def add_resource_to_build(
        self, build_id: int, resource_id: str, quantity: float, commit: bool = True
    ) -> CarriedResourceDescriptionModel:
        resource_description: ResourceDescriptionModel = self._kernel.game.config.resources[
            resource_id
        ]
        try:
            resource = (
                self._kernel.server_db_session.query(ResourceDocument)
                .filter(
                    and_(
                        ResourceDocument.in_built_id == build_id,
                        ResourceDocument.resource_id == resource_id,
                    )
                )
                .one()
            )
        except NoResultFound:
            resource = ResourceDocument(
                resource_id=resource_id,
                in_built_id=build_id,
                quantity=0.0,
                unit=resource_description.unit.value,
            )

        resource.quantity = float(resource.quantity) + quantity
        self._kernel.server_db_session.add(resource)

        if commit:
            self._kernel.server_db_session.commit()

        return self._carried_resource_model_from_doc(resource)

    def get_carried_by(self, character_id: str) -> typing.List[CarriedResourceDescriptionModel]:
        carried = (
            self._kernel.server_db_session.query(ResourceDocument)
            .filter(ResourceDocument.carried_by_id == character_id)
            .all()
        )
        return [self._carried_resource_model_from_doc(doc) for doc in carried]

    def get_one_carried_by(
        self, character_id: str, resource_id: str
    ) -> CarriedResourceDescriptionModel:
        doc = (
            self._kernel.server_db_session.query(ResourceDocument)
            .filter(
                and_(
                    ResourceDocument.carried_by_id == character_id,
                    ResourceDocument.resource_id == resource_id,
                )
            )
            .one()
        )
        return self._carried_resource_model_from_doc(doc)

    def _carried_resource_model_from_doc(
        self, doc: ResourceDocument
    ) -> CarriedResourceDescriptionModel:
        resource_description = self._kernel.game.config.resources[doc.resource_id]
        clutter = float(doc.quantity) * resource_description.clutter

        if resource_description.unit in (Unit.UNIT, Unit.CUBIC, Unit.LITTER):
            weight = float(doc.quantity) * resource_description.weight
        elif resource_description.unit in (Unit.GRAM,):
            weight = float(doc.quantity)
        else:
            raise NotImplementedError()

        return CarriedResourceDescriptionModel(
            id=doc.resource_id,
            name=resource_description.name,
            weight=weight,
            material_type=resource_description.material_type,
            unit=resource_description.unit,
            clutter=clutter,
            quantity=float(doc.quantity),
            descriptions=resource_description.descriptions,
        )

    def have_resource(
        self, character_id: str, resource_id: str, quantity: typing.Optional[float] = None
    ) -> bool:
        try:
            resource_doc = (
                self._kernel.server_db_session.query(ResourceDocument)
                .filter(
                    and_(
                        ResourceDocument.carried_by_id == character_id,
                        ResourceDocument.resource_id == resource_id,
                    )
                )
                .one()
            )
        except NoResultFound:
            return False

        if quantity is not None:
            return float(resource_doc.quantity) >= quantity

        return True

    def reduce_carried_by(
        self, character_id: str, resource_id: str, quantity: float, commit: bool = True
    ) -> None:
        filter_ = and_(
            ResourceDocument.carried_by_id == character_id,
            ResourceDocument.resource_id == resource_id,
        )
        self._reduce(filter_, quantity=quantity, commit=commit)

    def reduce_stored_in(
        self, build_id: int, resource_id: str, quantity: float, commit: bool = True
    ) -> None:
        filter_ = and_(
            ResourceDocument.in_built_id == build_id, ResourceDocument.resource_id == resource_id
        )
        self._reduce(filter_, quantity=quantity, commit=commit)

    def _reduce(self, filter_, quantity: float, commit: bool = True) -> None:
        try:
            resource_doc = (
                self._kernel.server_db_session.query(ResourceDocument).filter(filter_).one()
            )
        except NoResultFound:
            raise NoCarriedResource()

        if float(resource_doc.quantity) < quantity:
            raise NotEnoughResource()

        resource_doc.quantity = float(resource_doc.quantity) - quantity

        if float(resource_doc.quantity) <= 0:
            self._kernel.server_db_session.delete(resource_doc)
        else:
            self._kernel.server_db_session.add(resource_doc)

        if commit:
            self._kernel.server_db_session.commit()

    def drop(
        self,
        character_id: str,
        resource_id: str,
        quantity: float,
        world_row_i: int,
        world_col_i: int,
        zone_row_i: int,
        zone_col_i: int,
        commit: bool = True,
    ) -> None:
        self.reduce_carried_by(character_id, resource_id, quantity, commit=commit)
        # TODO BS 2019-09-09: add resource on the ground

    def get_carrying_actions(
        self, character: CharacterModel, resource_id: str
    ) -> typing.List[CharacterActionLink]:
        actions: typing.List[CharacterActionLink] = []
        resource_description = self._kernel.game.config.resources[resource_id]

        for description in resource_description.descriptions:
            action = self._action_factory.get_with_resource_action(description)
            actions.extend(action.get_character_actions(character, resource_id))

        return actions

    def get_stored_in_build(self, build_id: int) -> typing.List[CarriedResourceDescriptionModel]:
        carried = (
            self._kernel.server_db_session.query(ResourceDocument)
            .filter(ResourceDocument.in_built_id == build_id)
            .all()
        )
        return [self._carried_resource_model_from_doc(doc) for doc in carried]