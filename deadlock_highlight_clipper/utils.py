from datetime import timedelta

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents


def parse_video_duration(duration: str) -> timedelta:
    # duration is in the format 1h26m34s
    duration = duration.lower()
    hours, minutes, seconds = 0, 0, 0
    if "h" in duration:
        hours, duration = duration.split("h")
        hours = int(hours)
    if "m" in duration:
        minutes, duration = duration.split("m")
        minutes = int(minutes)
    if "s" in duration:
        seconds = int(duration[:-1])
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def format_timedelta(td: timedelta) -> str:
    # format timedelta to hh:mm:ss
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


class RecursiveNamespace:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if type(val) == dict:
                setattr(self, key, self.__class__(**val))
            elif type(val) == list:
                setattr(self, key, list(map(self.map_entry, val)))
            else:
                setattr(self, key, val)

    @classmethod
    def map_entry(cls, entry):
        if isinstance(entry, dict):
            return cls(**entry)
        return entry


def get_player_slot(steam_id: int, match: CMsgMatchMetaDataContents.MatchInfo) -> int:
    for player in match.players:
        if player.account_id == steam_id:
            return player.player_slot
    raise ValueError(f"Steam ID {steam_id} not found in match")
