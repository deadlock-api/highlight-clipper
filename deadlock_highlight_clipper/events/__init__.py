from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.events.death_event import DeathEvent
from deadlock_highlight_clipper.events.event import Event
from deadlock_highlight_clipper.events.kill_event import KillEvent
from deadlock_highlight_clipper.events.multikill_event import MultiKillEvent


def detect_events(
    steam_id: int, match: CMsgMatchMetaDataContents.MatchInfo
) -> list[Event]:
    return [
        *KillEvent.detect(steam_id, match),
        *DeathEvent.detect(steam_id, match),
        *MultiKillEvent.detect(steam_id, match),
    ]
