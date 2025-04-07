"""
Twitch API client for the Deadlock Highlight Clipper.
"""

from functools import lru_cache

from twitchAPI.object.api import Video
from twitchAPI.twitch import Twitch
from twitchAPI.type import VideoType

from deadlock_highlight_clipper.config import Config


@lru_cache
async def connect_twitch() -> Twitch:
    if not Config.twitch_client_id or not Config.twitch_access_token:
        raise ValueError(
            "TWITCH_CLIENT_ID and TWITCH_ACCESS_TOKEN must be set in environment variables"
        )

    twitch = Twitch(Config.twitch_client_id)
    twitch.auto_refresh_auth = False
    await twitch.set_user_authentication(Config.twitch_access_token, scope=[])
    return twitch


async def get_video_metadata(channel_id: str) -> list[Video]:
    twitch = await connect_twitch()
    return [
        v
        async for v in twitch.get_videos(
            user_id=channel_id, video_type=VideoType.ARCHIVE, first=100
        )
    ]
