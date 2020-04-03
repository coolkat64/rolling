# coding: utf-8
import enum

from sqlalchemy import JSON
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from rolling.server.extension import ServerSideDocument as Document


class AffinityJoinType(enum.Enum):
    ACCEPT_ALL = "ACCEPT_ALL"
    ONE_CHIEF_ACCEPT = "ONE_CHIEF_ACCEPT"
    HALF_STATUS_ACCEPT = "HALF_STATUS_ACCEPT"


class AffinityDirectionType(enum.Enum):
    ONE_DIRECTOR = "ONE_DIRECTOR"
    ELECTED_BY_HALF_STATUS = "ELECTED_BY_HALF_STATUS"


CHIEF_STATUS = ("CHIEF_STATUS", "Chef")
MEMBER_STATUS = ("MEMBER_STATUS", "Membre")


affinity_join_str = {
    AffinityJoinType.ACCEPT_ALL: "Accepter tout de suite",
    AffinityJoinType.ONE_CHIEF_ACCEPT: "Sur acceptation d'un des chefs",
    AffinityJoinType.HALF_STATUS_ACCEPT: "Sur acceptation d'une majorité",
}

affinity_direction_str = {
    AffinityDirectionType.ONE_DIRECTOR: "Un seul chef",
    AffinityDirectionType.ELECTED_BY_HALF_STATUS: "Sur acceptation d'une majorité",
}


class AffinityDocument(Document):
    __tablename__ = "affinity"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False, default="")
    join_type = Column(
        Enum(*[j.value for j in AffinityJoinType]), default=AffinityJoinType.ONE_CHIEF_ACCEPT.value
    )
    direction_type = Column(
        Enum(*[j.value for j in AffinityDirectionType]),
        default=AffinityDirectionType.ONE_DIRECTOR.value,
    )
    statuses = Column(
        JSON, nullable=False, default='[["CHIEF_STATUS", "Chef"], ["MEMBER_STATUS", "Membre"]]'
    )


class AffinityRelationDocument(Document):
    __tablename__ = "character_affinity"
    character_id = Column(String(255), ForeignKey("character.id"), primary_key=True)
    affinity_id = Column(Integer, ForeignKey("character.id"), primary_key=True)
    request = Column(Boolean, nullable=False, default=False)
    accepted = Column(Boolean, nullable=False, default=False)
    disallowed = Column(Boolean, nullable=False, default=False)  # disallowed by affinity
    rejected = Column(Boolean, nullable=False, default=False)  # rejected by character
    status_id = Column(String, nullable=True, default=None)
    fighter = Column(Boolean, nullable=False, default=False)
