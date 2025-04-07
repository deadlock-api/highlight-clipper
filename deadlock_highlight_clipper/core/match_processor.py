"""
Core match processing functionality for the Deadlock Highlight Clipper.
"""

import asyncio
import logging
import os
from datetime import timedelta
from typing import List

import httpx
from twitchAPI.object.api import Video

from deadlock_highlight_clipper.clients.deadlock import (
    DeadlockMatchHistoryEntry,
    get_match,
)
from deadlock_highlight_clipper.config import Config
from deadlock_highlight_clipper.events import detect_events, Event
from deadlock_highlight_clipper.utils.video import (
    extract_video_offset,
    match_to_video_time,
    download_vod_part,
)

LOGGER = logging.getLogger(__name__)


async def process_video(
    steam_id: int,
    video: Video,
    matches: List[DeadlockMatchHistoryEntry],
    http_client: httpx.AsyncClient,
) -> None:
    """
    Process a video by processing all matches in it.

    Args:
        steam_id: The Steam ID of the player
        video: The video metadata
        matches: The matches to process
        http_client: An HTTP client
    """
    LOGGER.info(
        f"[SteamID: {steam_id}] Processing video {video.title} with {len(matches)} matches"
    )
    for match in matches:
        await process_match(steam_id, video, match, http_client)


async def process_match(
    steam_id: int,
    video: Video,
    match: DeadlockMatchHistoryEntry,
    http_client: httpx.AsyncClient,
) -> None:
    """
    Process a match by detecting and processing events.

    Args:
        steam_id: The Steam ID of the player
        video: The video metadata
        match: The match to process
        http_client: An HTTP client
    """
    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] Processing match {match.match_id}"
    )
    match_data = await get_match(http_client, match.match_id)
    detected_events = detect_events(steam_id, match_data)
    if not detected_events:
        LOGGER.warning(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] No events detected"
        )
        return
    video_offset = await extract_video_offset(match, video, detected_events[-1])

    # Create a semaphore to limit concurrent processing
    semaphore = asyncio.Semaphore(5)

    async def wrapper(steam_id, video, match, event, video_offset):
        async with semaphore:
            await process_event(steam_id, video, match, event, video_offset)

    await asyncio.gather(
        *[wrapper(steam_id, video, match, e, video_offset) for e in detected_events]
    )


async def process_event(
    steam_id: int,
    video: Video,
    match: DeadlockMatchHistoryEntry,
    event: Event,
    video_offset: timedelta,
) -> None:
    """
    Internal function to process an event.

    Args:
        steam_id: The Steam ID of the player
        video: The video metadata
        match: The match data
        event: The event to process
        video_offset: The offset between match time and video time
    """
    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] "
        f"Processing event {event.name} ({event.game_time_s_start}s-{event.game_time_s_end}s)"
    )

    title = video.title.replace("/", "-").replace(".", "-")
    out_folder = f"{Config.output_directory}/{video.user_name}/{video.created_at.date().isoformat()}-{title}/{match.start_time.time().isoformat()}/{event.name}"
    os.makedirs(out_folder, exist_ok=True)

    out_file = f"{out_folder}/{event.filename()}.mp4"
    if os.path.exists(out_file):
        LOGGER.info(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] "
            f"Event {event.name} already processed, skipping"
        )
        return

    start_time = (
        match_to_video_time(event.game_time_s_start, match, video, video_offset)
        - Config.clip_padding
    )
    end_time = (
        match_to_video_time(event.game_time_s_end, match, video, video_offset)
        + Config.clip_padding
    )

    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] "
        f"Downloading clip for event {event.name} from {start_time} to {end_time}"
    )

    success = await download_vod_part(video, out_file, start_time, end_time)
    if not success:
        LOGGER.error(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] "
            f"Failed to download clip for event {event.name}"
        )
        return

    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] "
        f"Successfully processed event {event.name}"
    )
