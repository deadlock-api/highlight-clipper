import asyncio
import logging
import os
from argparse import ArgumentParser
from datetime import timedelta

import coloredlogs
import httpx
from twitchAPI.object.api import Video

from deadlock_highlight_clipper import twitch, deadlock, utils, events, video_edit
from deadlock_highlight_clipper.deadlock import DeadlockMatchHistoryEntry
from deadlock_highlight_clipper.events.event import Event

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("hpack").setLevel(logging.INFO)
coloredlogs.install(level="DEBUG")

LOGGER = logging.getLogger(__name__)
http_client = httpx.AsyncClient(http2=True)
CLIP_PADDING = timedelta(seconds=10)


async def main(channel_id: str, steam_id: int):
    videos = await twitch.get_video_metadata(channel_id=channel_id)
    matches = await deadlock.get_matches(http_client, steam_id=steam_id)

    def is_match_in_video(video: Video, match: DeadlockMatchHistoryEntry) -> bool:
        video_start = video.created_at
        video_end = video.created_at + utils.parse_video_duration(video.duration)
        return video_start <= match.start_time <= video_end

    videos = {v: [m for m in matches if is_match_in_video(v, m)] for v in videos}
    for v, ms in videos.items():
        await process_video(steam_id, v, ms)


async def process_video(
    steam_id: int, video: Video, matches: list[DeadlockMatchHistoryEntry]
):
    LOGGER.info(f"[SteamID: {steam_id}] Processing video {video}")
    for match in matches:
        await process_match(steam_id, video, match)


async def process_match(steam_id: int, video: Video, match: DeadlockMatchHistoryEntry):
    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] Processing match {match.match_id}"
    )
    match_data = await deadlock.get_match(http_client, match.match_id)
    detected_events = events.detect_events(steam_id, match_data)
    if not detected_events:
        LOGGER.warning(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] No events detected"
        )
        return
    video_offset = await video_edit.extract_video_offset(
        match, video, detected_events[-1]
    )
    await asyncio.gather(
        *[
            process_event(steam_id, video, match, e, video_offset)
            for e in detected_events
        ]
    )


semaphore = asyncio.Semaphore(5)


async def process_event(
    steam_id: int,
    video: Video,
    match: DeadlockMatchHistoryEntry,
    event: Event,
    video_offset: timedelta,
):
    async with semaphore:
        await _process_event(steam_id, video, match, event, video_offset)


async def _process_event(
    steam_id: int,
    video: Video,
    match: DeadlockMatchHistoryEntry,
    event: Event,
    video_offset: timedelta,
):
    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Processing event {event.name} ({event.game_time_s_start}s-{event.game_time_s_end}s)"
    )

    out_folder = f"clips/{video.user_name}/{video.title}/{match.start_time.isoformat()}/{event.name}"
    os.makedirs(out_folder, exist_ok=True)

    out_file = f"{out_folder}/{event.filename()}.mp4"
    if os.path.exists(out_file):
        LOGGER.info(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} already processed, skipping"
        )
        return

    LOGGER.info(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} downloading video"
    )

    video_event_start = (
        video_edit.match_to_video_time(
            event.game_time_s_start, match, video, video_offset
        )
        - CLIP_PADDING
    )
    video_event_end = (
        video_edit.match_to_video_time(
            event.game_time_s_end, match, video, video_offset
        )
        + CLIP_PADDING
    )
    result = await video_edit.download_vod_part(
        video, out_file, video_event_start, video_event_end
    )
    if result:
        LOGGER.info(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} downloaded video"
        )
    else:
        LOGGER.error(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} failed to download video"
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--channel-id", type=str, required=True, help="Twitch channel ID"
    )
    parser.add_argument("-s", "--steam-id3", type=int, required=True, help="Steam ID3")
    args = parser.parse_args()

    asyncio.run(main(args.channel_id, args.steam_id3))
