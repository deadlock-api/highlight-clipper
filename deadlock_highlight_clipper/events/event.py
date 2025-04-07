from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents


@dataclass
class Event(ABC):
    name: str
    game_time_s_start: timedelta
    game_time_s_end: timedelta

    @classmethod
    @abstractmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["Event"]:
        raise NotImplementedError

    @abstractmethod
    def filename_postfix(self) -> str:
        raise NotImplementedError
