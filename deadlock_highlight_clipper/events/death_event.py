from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.events.event import Event


@dataclass
class DeathEvent(Event):
    killer: CMsgMatchMetaDataContents.Players
    victim: CMsgMatchMetaDataContents.Players
    killer_pos: CMsgMatchMetaDataContents.Position
    death_pos: CMsgMatchMetaDataContents.Position
    death_duration_s: int

    @classmethod
    def from_death_detail(
        cls,
        death_detail: CMsgMatchMetaDataContents.Deaths,
        killer: CMsgMatchMetaDataContents.Players,
        victim: CMsgMatchMetaDataContents.Players,
    ):
        return cls(
            name="death",
            killer=killer,
            victim=victim,
            game_time_s_start=timedelta(seconds=death_detail.game_time_s),
            game_time_s_end=timedelta(seconds=death_detail.game_time_s),
            killer_pos=death_detail.killer_pos,
            death_pos=death_detail.death_pos,
            death_duration_s=death_detail.death_duration_s,
        )

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["DeathEvent"]:
        return [
            cls.from_death_detail(
                death, utils.get_player_at_slot(death.killer_player_slot, match), victim
            )
            for victim in match.players
            if victim.account_id == steam_id
            for death in victim.death_details
        ]

    def filename(self):
        return f"{self.game_time_s_start.total_seconds()}-K{self.killer.account_id}-{self.killer.hero_id}_V{self.victim.account_id}-{self.victim.hero_id}"
