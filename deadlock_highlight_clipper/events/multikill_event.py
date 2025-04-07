"""
Multi-kill event detection for the Deadlock Highlight Clipper.

This module provides functionality for detecting multi-kill events in Deadlock matches.
"""

from dataclasses import dataclass
from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.config import Config
from deadlock_highlight_clipper.utils.data import get_player_slot, get_player_at_slot
from deadlock_highlight_clipper.events.event import Event


@dataclass
class MultiKillEvent(Event):
    """
    An event representing multiple kills in quick succession.
    """

    killer: CMsgMatchMetaDataContents.Players
    victims: list[CMsgMatchMetaDataContents.Players]

    @classmethod
    def detect(
        cls,
        steam_id: int,
        match: CMsgMatchMetaDataContents.MatchInfo,
    ) -> list["MultiKillEvent"]:
        """
        Detect multi-kill events in a match.

        Args:
            steam_id: The Steam ID of the player
            match: The match data

        Returns:
            A list of MultiKillEvent objects

        Raises:
            ValueError: If the player is not found in the match
        """
        player_slot = get_player_slot(steam_id, match)
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
                kill.game_time_s - multi_kill[-1].game_time_s
                < Config.multikill_threshold_seconds
            ):  # within threshold
                multi_kill.append(kill)
                continue
            if len(multi_kill) >= Config.multikill_min_kills:  # multi kill
                multi_kills.append(multi_kill)
            # reset multi kill
            multi_kill = [kill]
        if len(multi_kill) >= Config.multikill_min_kills:
            multi_kills.append(multi_kill)

        return [
            cls(
                name="multikill",
                killer=killer,
                victims=[get_player_at_slot(k.killer_player_slot, match) for k in kd],
                game_time_s_start=timedelta(seconds=min([k.game_time_s for k in kd])),
                game_time_s_end=timedelta(seconds=max([k.game_time_s for k in kd])),
            )
            for kd in multi_kills
        ]

    def filename(self) -> str:
        """
        Generate a filename for the event.

        Returns:
            A string representing the filename
        """
        return f"{int(self.game_time_s_start.total_seconds())}-K{self.killer.hero_id}-V{len(self.victims)}"
