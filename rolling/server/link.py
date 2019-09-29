# coding: utf-8
import dataclasses
import typing

from rolling.types import ActionType


@dataclasses.dataclass
class CharacterActionLink:
    name: str
    link: str
    cost: typing.Optional[float] = None
    merge_by: typing.Optional[typing.Any] = None

    def get_as_str(self) -> str:
        if not self.cost:
            return self.name
        return f"{self.name} ({self.cost} points d'actions)"
