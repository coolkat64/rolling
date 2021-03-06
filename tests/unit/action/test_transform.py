# coding: utf-8
import typing

import pytest

from rolling.action.transform import QuantityModel
from rolling.action.transform import TransformResourcesIntoResourcesAction
from rolling.kernel import Kernel
from rolling.model.character import CharacterModel
from rolling.rolling_types import ActionType


@pytest.fixture
def transform_rtr_action(worldmapc_kernel: Kernel,) -> TransformResourcesIntoResourcesAction:
    return typing.cast(
        TransformResourcesIntoResourcesAction,
        worldmapc_kernel.action_factory.create_action(
            ActionType.TRANSFORM_RESOURCES_TO_RESOURCES, "MAKE_CLOTH"
        ),
    )


class TestTransformAction:
    @pytest.mark.parametrize(
        "input_quantity,expected_left_quantity,expected_produced_quantity,consumed_ap",
        [
            # According to game config fixtures
            (0.5, 4.5, 1, 2.5),
            (1.0, 4.0, 2, 5.0),
            (1.1, 4.0, 2, 5.0),
            (1.9, 3.5, 3, 7.5),
            (2.0, 3.0, 4, 10.0),
        ],
    )
    def test_unit__transform_resource_to_resource__ok__m3_to_unit(
        self,
        worldmapc_kernel: Kernel,
        worldmapc_franck_model: CharacterModel,
        transform_rtr_action: TransformResourcesIntoResourcesAction,
        input_quantity: float,
        expected_left_quantity: float,
        expected_produced_quantity: int,
        consumed_ap: float,
    ):
        kernel = worldmapc_kernel
        franck = worldmapc_franck_model
        action = transform_rtr_action

        before_ap = franck.action_points
        kernel.resource_lib.add_resource_to(
            resource_id="VEGETAL_FIBER", character_id=franck.id, quantity=5.0
        )
        assert (
            kernel.resource_lib.get_one_carried_by(
                character_id=franck.id, resource_id="VEGETAL_FIBER"
            ).quantity
            == 5.0
        )
        assert not kernel.resource_lib.have_resource(character_id=franck.id, resource_id="CLOTH")

        action.perform(
            character=franck,
            resource_id="VEGETAL_FIBER",
            input_=QuantityModel(quantity=input_quantity),
        )

        assert (
            kernel.resource_lib.get_one_carried_by(
                character_id=franck.id, resource_id="VEGETAL_FIBER"
            ).quantity
            == expected_left_quantity
        )
        assert (
            kernel.resource_lib.get_one_carried_by(
                character_id=franck.id, resource_id="CLOTH"
            ).quantity
            == expected_produced_quantity
        )
        franck_doc = kernel.character_lib.get_document(franck.id)
        assert before_ap - float(franck_doc.action_points) == consumed_ap
