"""
Deadlock API client for the Deadlock Highlight Clipper.
"""

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

import pytz
from httpx import AsyncClient
from valveprotos_py.citadel_gcmessages_common_p2p import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.utils.data import RecursiveNamespace


@dataclass
class DeadlockMatchHistoryEntry:
    """
    A class representing a match history entry from the Deadlock API.
    """

    account_id: int
    match_id: int
    hero_id: int
    hero_level: int
    start_time: datetime
    game_mode: int
    match_mode: int
    player_team: int
    player_kills: int
    player_deaths: int
    player_assists: int
    denies: int
    net_worth: int
    last_hits: int
    match_duration_s: int
    match_result: int
    objectives_mask_team0: int
    objectives_mask_team1: int
    team_abandoned: int | None
    abandoned_time_s: int | None

    @classmethod
    def from_dict(cls, data):
        data["start_time"] = datetime.fromtimestamp(data["start_time"]).astimezone(
            pytz.UTC
        )
        return cls(**data)


@lru_cache
async def get_matches(
    http_client: AsyncClient, steam_id: int
) -> list[DeadlockMatchHistoryEntry]:
    """
    Get match history for a player from the Deadlock API.

    Args:
        http_client: An HTTP client
        steam_id: The Steam ID of the player

    Returns:
        A list of DeadlockMatchHistoryEntry objects
    """
    data = await http_client.get(
        f"https://api.deadlock-api.com/v1/players/{steam_id}/match-history"
    )
    data.raise_for_status()
    return [DeadlockMatchHistoryEntry.from_dict(entry) for entry in data.json()]


@lru_cache
async def get_match(
    http_client: AsyncClient, match_id: int
) -> CMsgMatchMetaDataContents.MatchInfo:
    """
    Get match data from the Deadlock API.

    Args:
        http_client: An HTTP client
        match_id: The match ID

    Returns:
        Match data as a CMsgMatchMetaDataContents.MatchInfo object
    """
    data = await http_client.get(
        f"https://api.deadlock-api.com/v1/matches/{match_id}/metadata"
    )
    data.raise_for_status()
    return RecursiveNamespace(**data.json()["match_info"])
