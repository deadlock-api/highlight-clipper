import os
from functools import lru_cache

from twitchAPI.object.api import Video
from twitchAPI.twitch import Twitch
from twitchAPI.type import VideoType


@lru_cache
async def connect_twitch() -> Twitch:
    twitch = Twitch(os.environ["TWITCH_CLIENT_ID"])
    twitch.auto_refresh_auth = False
    await twitch.set_user_authentication(os.environ["TWITCH_ACCESS_TOKEN"], scope=[])
    return twitch


async def get_video_metadata(channel_id: str) -> list[Video]:
    twitch = await connect_twitch()
    return [
        v
        async for v in twitch.get_videos(
            user_id=channel_id, video_type=VideoType.ARCHIVE, first=100
        )
    ]
