from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.config import Config
from deadlock_highlight_clipper.events.event import Event
from deadlock_highlight_clipper.utils import data


@dataclass
class TeamFightEvent(Event):
    kills: list[CMsgMatchMetaDataContents.Deaths]

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["TeamFightEvent"]:
        slot = data.get_player_slot(steam_id, match)
        all_deaths = sorted(
            [
                (v, d)
                for v in match.players
                if v.account_id != steam_id
                for d in v.death_details
                if abs(d.death_pos.y) < 7000
            ],
            key=lambda d: d[1].game_time_s,
        )

        multi_kills = []
        multi_kill = []
        for p, death in all_deaths:
            if not multi_kill:
                multi_kill.append((p, death))
                continue
            if (
                death.game_time_s - multi_kill[-1][1].game_time_s
                < Config.team_fights_threshold_seconds
            ):
                multi_kill.append((p, death))
                continue
            if len(multi_kill) >= Config.team_fights_min_kills:
                multi_kills.append(multi_kill)
            multi_kill = [(p, death)]
        if len(multi_kill) >= Config.team_fights_min_kills:
            multi_kills.append(multi_kill)

        # Player made at least two kills
        multi_kills = filter(
            lambda m: sum(d.killer_player_slot == slot for _, d in m) > 2, multi_kills
        )
        # Player did not die
        multi_kills = filter(
            lambda m: not any(p.account_id == steam_id for p, _ in multi_kill),
            multi_kills,
        )

        return [
            cls(
                name="team_fight",
                kills=[d for _, d in kd],
                game_time_s_start=timedelta(seconds=min(k.game_time_s for _, k in kd)),
                game_time_s_end=timedelta(seconds=max(k.game_time_s for _, k in kd)),
            )
            for kd in multi_kills
        ]

    def filename(self) -> str:
        return f"{int(self.game_time_s_start.total_seconds())}-K{len(self.kills)}"
