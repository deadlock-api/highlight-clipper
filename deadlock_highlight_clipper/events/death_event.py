from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.events.event import Event


@dataclass
class DeathEvent(Event):
    killer: CMsgMatchMetaDataContents.Players
    victim: CMsgMatchMetaDataContents.Players

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["DeathEvent"]:
        return [
            cls(
                name="death",
                killer=utils.get_player_at_slot(death.killer_player_slot, match),
                victim=victim,
                game_time_s_start=timedelta(seconds=death.game_time_s),
                game_time_s_end=timedelta(seconds=death.game_time_s),
            )
            for victim in match.players
            if victim.account_id == steam_id
            for death in victim.death_details
        ]

    def filename(self) -> str:
        return f"{self.game_time_s_start.total_seconds()}-K{self.killer.hero_id}-V{self.victim.account_id}-{self.victim.hero_id}"
