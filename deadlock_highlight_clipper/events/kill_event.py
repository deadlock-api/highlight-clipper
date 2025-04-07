from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.events.event import Event


@dataclass
class KillEvent(Event):
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
            name="kill",
            killer=killer,
            victim=victim,
            game_time_s_start=timedelta(seconds=death_detail.game_time_s),
            game_time_s_end=timedelta(seconds=death_detail.game_time_s + death_detail.death_duration_s),
            killer_pos=death_detail.killer_pos,
            death_pos=death_detail.death_pos,
            death_duration_s=death_detail.death_duration_s,
        )

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["KillEvent"]:
        player_slot = utils.get_player_slot(steam_id, match)
        killer = next(
            (p for p in match.players if p.account_id == steam_id), None
        )
        if not killer:
            raise ValueError(f"Player with Steam ID {steam_id} not found in match.")
        return [
            KillEvent.from_death_detail(death, killer, victim)
            for victim in match.players
            if victim.account_id != steam_id
            for death in victim.death_details
            if death.killer_player_slot == player_slot
        ]

    def filename_postfix(self):
        return f"K{self.killer.account_id}-{self.killer.hero_id}_V{self.victim.account_id}-{self.victim.hero_id}"
