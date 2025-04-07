from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.events.event import Event


@dataclass
class KillEvent(Event):
    killer: CMsgMatchMetaDataContents.Players
    victim: CMsgMatchMetaDataContents.Players

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["KillEvent"]:
        player_slot = utils.get_player_slot(steam_id, match)
        killer = next((p for p in match.players if p.account_id == steam_id), None)
        if not killer:
            raise ValueError(f"Player with Steam ID {steam_id} not found in match.")
        return [
            cls(
                name="kill",
                killer=killer,
                victim=victim,
                game_time_s_start=timedelta(seconds=death.game_time_s),
                game_time_s_end=timedelta(seconds=death.game_time_s),
            )
            for victim in match.players
            if victim.account_id != steam_id
            for death in victim.death_details
            if death.killer_player_slot == player_slot
        ]

    def filename(self) -> str:
        return f"{int(self.game_time_s_start.total_seconds())}-K{self.killer.hero_id}-V{self.victim.account_id}-{self.victim.hero_id}"
