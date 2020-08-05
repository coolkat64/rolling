# coding: utf-8

# This file defines a GlobalTranslation object which maps hard-wired 
# concepts of the game to translations. 

import typing

from rolling.model.measure import Unit


class GlobalTranslation:
    def __init__(self) -> None:
        self._translation: typing.Dict[typing.Any, str] = {
            Unit.LITTER: "litres",
            Unit.CUBIC: "mètre cubes",
            Unit.GRAM: "grammes",
            Unit.UNIT: "unités",
        }

    def get(self, key: typing.Any) -> str:
        return self._translation[key]
