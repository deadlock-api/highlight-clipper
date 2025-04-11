"""
Event detection for the Deadlock Highlight Clipper.

This package provides functionality for detecting events in Deadlock matches.
"""

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.events.death_event import DeathEvent
from deadlock_highlight_clipper.events.event import Event
from deadlock_highlight_clipper.events.kill_event import KillEvent
from deadlock_highlight_clipper.events.multikill_event import MultiKillEvent
from deadlock_highlight_clipper.events.team_fight_event import TeamFightEvent


def detect_events(
    steam_id: int, match: CMsgMatchMetaDataContents.MatchInfo
) -> list[Event]:
    """
    Detect events in a match.

    This function detects all supported event types in a match.

    Args:
        steam_id: The Steam ID of the player
        match: The match data

    Returns:
        A list of Event objects
    """
    return [
        # *KillEvent.detect(steam_id, match),
        # *DeathEvent.detect(steam_id, match),
        *MultiKillEvent.detect(steam_id, match),
        *TeamFightEvent.detect(steam_id, match),
    ]
