from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

import pytz
from httpx import AsyncClient
from valveprotos_py.citadel_gcmessages_common_p2p import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.utils import RecursiveNamespace


@dataclass
class DeadlockMatchHistoryEntry:
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
    data = await http_client.get(
        f"https://api.deadlock-api.com/v1/players/{steam_id}/match-history"
    )
    data.raise_for_status()
    return [DeadlockMatchHistoryEntry.from_dict(entry) for entry in data.json()]


@lru_cache
async def get_match(
    http_client: AsyncClient, match_id: int
) -> CMsgMatchMetaDataContents.MatchInfo:
    data = await http_client.get(
        f"https://api.deadlock-api.com/v1/matches/{match_id}/metadata"
    )
    data.raise_for_status()
    return RecursiveNamespace(**data.json()["match_info"])
