"""
Data manipulation utility functions for the Deadlock Highlight Clipper.
"""

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents


class RecursiveNamespace:
    """
    A class that converts nested dictionaries into nested objects for easier access.

    Example:
        data = {'a': 1, 'b': {'c': 2}}
        ns = RecursiveNamespace(**data)
        print(ns.a)  # 1
        print(ns.b.c)  # 2
    """

    def __init__(self, **kwargs):
        """
        Initialize a RecursiveNamespace object.

        Args:
            **kwargs: Keyword arguments to convert to attributes
        """
        for key, val in kwargs.items():
            if type(val) == dict:
                setattr(self, key, self.__class__(**val))
            elif type(val) == list:
                setattr(self, key, list(map(self.map_entry, val)))
            else:
                setattr(self, key, val)

    @classmethod
    def map_entry(cls, entry):
        """
        Map a dictionary entry to a RecursiveNamespace object.

        Args:
            entry: A dictionary or other value

        Returns:
            A RecursiveNamespace object if entry is a dictionary, otherwise entry
        """
        if isinstance(entry, dict):
            return cls(**entry)
        return entry


def get_player_slot(steam_id: int, match: CMsgMatchMetaDataContents.MatchInfo) -> int:
    """
    Get the player slot for a player with the given Steam ID in a match.

    Args:
        steam_id: The Steam ID of the player
        match: The match data

    Returns:
        The player slot

    Raises:
        ValueError: If the player is not found in the match
    """
    for player in match.players:
        if player.account_id == steam_id:
            return player.player_slot
    raise ValueError(f"Steam ID {steam_id} not found in match")


def get_player_at_slot(
    slot: int, match: CMsgMatchMetaDataContents.MatchInfo
) -> CMsgMatchMetaDataContents.Players:
    """
    Get the player at the given slot in a match.

    Args:
        slot: The player slot
        match: The match data

    Returns:
        The player data

    Raises:
        ValueError: If no player is found at the given slot
    """
    for player in match.players:
        if player.player_slot == slot:
            return player
    raise ValueError(f"Player at slot {slot} not found in match")
