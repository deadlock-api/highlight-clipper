import asyncio
import os
import re
from datetime import timedelta

import cv2
import easyocr
import numpy as np
from twitchAPI.object.api import Video
from valveprotos_py.citadel_gcmessages_common_pb2 import CMsgMatchMetaDataContents

from deadlock_highlight_clipper import utils
from deadlock_highlight_clipper.__main__ import LOGGER
from deadlock_highlight_clipper.deadlock import DeadlockMatchHistoryEntry
from deadlock_highlight_clipper.events import Event


async def extract_video_offset(
    match: DeadlockMatchHistoryEntry | CMsgMatchMetaDataContents.MatchInfo,
    video: Video,
    event: Event,
) -> timedelta:
    filename = f"{video.id}_offset_calc.mp4"
    event_time_start = match_to_video_time(event.game_time_s_start, match, video)
    event_time_end = match_to_video_time(event.game_time_s_end, match, video)
    await extract_clip(
        video,
        event_time_start - timedelta(seconds=5),
        event_time_end + timedelta(seconds=5),
        filename,
    )
    cap = cv2.VideoCapture(filename)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    crop_x1, crop_x2 = width // 2 - 30, width // 2 + 30
    crop_y1, crop_y2 = 2, 25

    reader = easyocr.Reader(["en"])
    timestamps = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]
        text = reader.readtext(frame, detail=0)
        if not text:
            continue
        text = text[0]
        digits = "".join(re.findall(r"\d+", text))
        if len(digits) > 4 or len(digits) < 2:
            continue
        minutes, seconds = digits[:-2], digits[-2:]
        if not minutes:
            minutes = "0"
        timestamps.append(timedelta(minutes=int(minutes), seconds=int(seconds)))
    cap.release()
    if not timestamps:
        raise ValueError("No timestamps detected")

    LOGGER.debug(f"Detected {len(timestamps)} timestamps")
    timestamps = filter_outliers(timestamps)
    avg_timestamp = sum(timestamps, timedelta()) / len(timestamps)
    LOGGER.info(
        f"Detected Video Offset: {(event.game_time_s_start + event.game_time_s_end) / 2 - avg_timestamp}"
    )

    os.remove(filename)
    return (
        (event.game_time_s_start + event.game_time_s_end) / 2
        - avg_timestamp
        - timedelta(seconds=2)
    )


def filter_outliers(
    timestamps: list[timedelta], threshold: float = 1.5
) -> list[timedelta]:
    # filter unsorted timestamps
    filter_indices = set()
    for i in range(1, len(timestamps)):
        if timestamps[i] < timestamps[i - 1]:
            filter_indices.add(i)
    filtered_timestamps = [
        t for i, t in enumerate(timestamps) if i not in filter_indices
    ]

    # Convert timedelta to seconds
    seconds_list = [int(ts.total_seconds()) for ts in filtered_timestamps]

    q1 = np.percentile(seconds_list, 25)
    q3 = np.percentile(seconds_list, 75)
    iqr = q3 - q1
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr
    outlier_indices = set()
    for i, seconds in enumerate(seconds_list):
        if seconds < lower_bound or seconds > upper_bound:
            outlier_indices.add(i)
    return [t for i, t in enumerate(filtered_timestamps) if i not in outlier_indices]


def match_to_video_time(
    match_time: timedelta,
    match: DeadlockMatchHistoryEntry | CMsgMatchMetaDataContents.MatchInfo,
    video: Video,
    video_offset: timedelta = timedelta(),
) -> timedelta:
    return match_time + match.start_time - video.created_at + video_offset


async def extract_clip(
    video: Video,
    video_event_start: timedelta,
    video_event_end: timedelta,
    out_file: str,
) -> bool:
    video_event_start = utils.format_timedelta(video_event_start)
    video_event_end = utils.format_timedelta(video_event_end)
    command = f"twitch-dl download {video.id} --keep --start {video_event_start} --end {video_event_end} --output {out_file} --overwrite --quality source --format mp4"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, stderr = await process.communicate()
    LOGGER.debug(stdout.decode())
    return process.returncode == 0
