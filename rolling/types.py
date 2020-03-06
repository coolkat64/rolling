# coding: utf-8
import enum


class ActionType(enum.Enum):
    FILL_STUFF = "FILL_STUFF"
    EMPTY_STUFF = "EMPTY_STUFF"
    ATTACK_CHARACTER_WITH = "ATTACK_CHARACTER_WITH"
    DRINK_RESOURCE = "DRINK_RESOURCE"
    DRINK_STUFF = "DRINK_STUFF"
    COLLECT_RESOURCE = "COLLECT_RESOURCE"
    USE_AS_BAG = "USE_AS_BAG"
    NOT_USE_AS_BAG = "NOT_USE_AS_BAG"
    DROP_STUFF = "DROP_STUFF"
    DROP_RESOURCE = "DROP_RESOURCE"
    MIX_RESOURCES = "MIX_RESOURCES"
    EAT_RESOURCE = "EAT_RESOURCE"
    EAT_STUFF = "EAT_STUFF"
    SEARCH_FOOD = "SEARCH_FOOD"
    BEGIN_BUILD = "BEGIN_BUILD"
    BRING_RESOURCE_ON_BUILD = "BRING_RESOURCE_ON_BUILD"
    CONSTRUCT_BUILD = "CONSTRUCT_BUILD"
    TRANSFORM_STUFF_TO_RESOURCES = "TRANSFORM_STUFF_TO_RESOURCES"
    TRANSFORM_RESOURCES_TO_RESOURCES = "TRANSFORM_RESOURCES_TO_RESOURCES"
    CRAFT_STUFF_WITH_STUFF = "CRAFT_STUFF_WITH_STUFF"
    CRAFT_STUFF_WITH_RESOURCE = "CRAFT_STUFF_WITH_RESOURCE"
    BEGIN_STUFF_CONSTRUCTION = "BEGIN_STUFF_CONSTRUCTION"
    CONTINUE_STUFF_CONSTRUCTION = "CONTINUE_STUFF_CONSTRUCTION"


class TurnMode(enum.Enum):
    DAY = "DAY"
    HOUR = "HOUR"
