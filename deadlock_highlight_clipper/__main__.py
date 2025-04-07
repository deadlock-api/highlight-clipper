import asyncio
import os
import subprocess
from argparse import ArgumentParser
from datetime import timedelta

import httpx
from twitchAPI.object.api import Video

from deadlock_highlight_clipper import twitch, deadlock, utils
from deadlock_highlight_clipper.deadlock import DeadlockMatchHistoryEntry
from deadlock_highlight_clipper.events.event import Event
from deadlock_highlight_clipper.events.event_detector import EventDetector

http_client = httpx.AsyncClient(http2=True)


async def process_event(
    steam_id: int, video: Video, match: DeadlockMatchHistoryEntry, event: Event
):
    print(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Processing event {event.name} ({event.game_time_s_start}s-{event.game_time_s_end}s)"
    )

    out_folder = f"events/{steam_id}/{video.id}/{match.match_id}"
    os.makedirs(out_folder, exist_ok=True)

    out_file = f"{out_folder}/{event.game_time_s_start.total_seconds()}s-{event.game_time_s_end.total_seconds()}s-{event.name}-{event.filename_postfix()}.mp4"
    if os.path.exists(out_file):
        print(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} already processed, skipping"
        )
        return

    print(
        f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} downloading video"
    )

    video_event_start = utils.format_timedelta(
        match.start_time
        + event.game_time_s_start
        - video.created_at
        + timedelta(seconds=36)
    )
    video_event_end = utils.format_timedelta(
        match.start_time
        + event.game_time_s_end
        - video.created_at
        + timedelta(seconds=36)
    )
    command = f"twitch-dl download {video.id} --start {video_event_start} --end {video_event_end} --output {out_file} --overwrite --quality source --format mp4"

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        if output:
            print(output.strip().decode())

    if process.returncode != 0:
        print(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} failed to download video"
        )
    else:
        print(
            f"[SteamID: {steam_id}] [Video: {video.title}] [Match: {match.match_id}] Event {event.name} downloaded video"
        )


async def process_match(steam_id: int, video: Video, match: DeadlockMatchHistoryEntry):
    print(
        f"[SteamID: {steam_id}] [Video: {video.title}] Processing match {match.match_id}"
    )
    match_data = await deadlock.get_match(http_client, match.match_id)
    event_detector = EventDetector(steam_id, match_data)
    events = event_detector.detect_events()
    await asyncio.gather(*[process_event(steam_id, video, match, e) for e in events])


async def process_video(
    steam_id: int, video: Video, matches: list[DeadlockMatchHistoryEntry]
):
    print(f"[SteamID: {steam_id}] Processing video {video}")
    await asyncio.gather(*[process_match(steam_id, video, match) for match in matches])


async def main(channel_id: str, steam_id: int):
    videos = await twitch.get_video_metadata(channel_id=channel_id)
    matches = await deadlock.get_matches(http_client, steam_id=steam_id)

    def is_match_in_video(video: Video, match: DeadlockMatchHistoryEntry) -> bool:
        video_start = video.created_at
        video_end = video.created_at + utils.parse_video_duration(video.duration)
        return video_start <= match.start_time <= video_end

    videos = {v: [m for m in matches if is_match_in_video(v, m)] for v in videos[:1]}
    await asyncio.gather(*[process_video(steam_id, v, ms) for v, ms in videos.items()])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--channel-id", type=str, required=True, help="Twitch channel ID"
    )
    parser.add_argument("-s", "--steam-id3", type=int, required=True, help="Steam ID3")
    args = parser.parse_args()

    asyncio.run(main(args.channel_id, args.steam_id3))
