"""
Core application functionality for the Deadlock Highlight Clipper.
"""

import logging
from typing import Dict, List

import httpx
from twitchAPI.object.api import Video

from deadlock_highlight_clipper.clients.deadlock import (
    DeadlockMatchHistoryEntry,
    get_matches,
)
from deadlock_highlight_clipper.clients.twitch import get_video_metadata
from deadlock_highlight_clipper.core.match_processor import process_video
from deadlock_highlight_clipper.utils.time import parse_video_duration

LOGGER = logging.getLogger(__name__)


async def run(channel_id: str, steam_id: int) -> None:
    """
    Run the Deadlock Highlight Clipper.

    Args:
        channel_id: The Twitch channel ID
        steam_id: The Steam ID of the player
    """
    # Create an HTTP client
    http_client = httpx.AsyncClient(http2=True)

    try:
        # Get videos and matches
        videos = await get_video_metadata(channel_id=channel_id)
        matches = await get_matches(http_client, steam_id=steam_id)

        # Filter matches by video
        videos_with_matches = filter_matches_by_video(videos, matches)

        # Process videos
        for video, matches in videos_with_matches.items():
            await process_video(steam_id, video, matches, http_client)
    finally:
        # Close the HTTP client
        await http_client.aclose()


def filter_matches_by_video(
    videos: List[Video], matches: List[DeadlockMatchHistoryEntry]
) -> Dict[Video, List[DeadlockMatchHistoryEntry]]:
    """
    Filter matches by video.

    Args:
        videos: A list of videos
        matches: A list of matches

    Returns:
        A dictionary mapping videos to matches
    """

    def is_match_in_video(video: Video, match: DeadlockMatchHistoryEntry) -> bool:
        video_start = video.created_at
        video_end = video.created_at + parse_video_duration(video.duration)
        return video_start <= match.start_time <= video_end

    return {v: [m for m in matches if is_match_in_video(v, m)] for v in videos}
