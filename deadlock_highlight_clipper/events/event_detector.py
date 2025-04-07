from dataclasses import dataclass

from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper.events.event import Event
from deadlock_highlight_clipper.events.kill_event import KillEvent


@dataclass
class EventDetector:
    steam_id: int
    match: CMsgMatchMetaDataContents.MatchInfo

    def detect_events(self) -> list[Event]:
        return [*KillEvent.detect(self.steam_id, self.match)]
