"""
Base event class for the Deadlock Highlight Clipper.

This module provides the base class for all event types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents


@dataclass
class Event(ABC):
    """
    Base class for all event types.

    This class defines the interface for all event types. Each event type must
    implement the `detect` and `filename` methods.
    """

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
        """
        Detect events in a match.

        Args:
            steam_id: The Steam ID of the player
            match: The match data

        Returns:
            A list of Event objects
        """
        raise NotImplementedError

    @abstractmethod
    def filename(self) -> str:
        """
        Generate a filename for the event.

        Returns:
            A string representing the filename
        """
        raise NotImplementedError
