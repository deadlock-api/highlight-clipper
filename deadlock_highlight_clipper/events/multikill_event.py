from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.events.event import Event

MIN_KILLS = 3
THRESHOLD_S = 10


@dataclass
class MultiKillEvent(Event):
    killer: CMsgMatchMetaDataContents.Players
    victims: list[CMsgMatchMetaDataContents.Players]

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["MultiKillEvent"]:
        player_slot = utils.get_player_slot(steam_id, match)
        killer = next((p for p in match.players if p.account_id == steam_id), None)
        if not killer:
            raise ValueError(f"Player with Steam ID {steam_id} not found in match.")
        all_kills = [
            death
            for victim in match.players
            if victim.account_id != steam_id
            for death in victim.death_details
            if death.killer_player_slot == player_slot
        ]
        all_kills.sort(key=lambda k: k.game_time_s)
        multi_kills = []
        multi_kill = []
        for kill in all_kills:
            if not multi_kill:  # first kill
                multi_kill.append(kill)
                continue
            if (
                kill.game_time_s - multi_kill[-1].game_time_s < THRESHOLD_S
            ):  # within threshold
                multi_kill.append(kill)
                continue
            if len(multi_kill) >= MIN_KILLS:  # multi kill
                multi_kills.append(multi_kill)
            # reset multi kill
            multi_kill = [kill]
        if len(multi_kill) >= MIN_KILLS:
            multi_kills.append(multi_kill)

        return [
            cls(
                name="multikill",
                killer=killer,
                victims=[
                    utils.get_player_at_slot(k.killer_player_slot, match) for k in kd
                ],
                game_time_s_start=timedelta(seconds=min([k.game_time_s for k in kd])),
                game_time_s_end=timedelta(seconds=max([k.game_time_s for k in kd])),
            )
            for kd in multi_kills
        ]

    def filename(self) -> str:
        return f"{self.game_time_s_start.total_seconds()}-K{self.killer.hero_id}-V{len(self.victims)}"
