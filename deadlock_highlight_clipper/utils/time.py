"""
Time-related utility functions for the Deadlock Highlight Clipper.
"""

from datetime import timedelta


def parse_video_duration(duration: str) -> timedelta:
    """
    Parse a video duration string in the format '1h26m34s' into a timedelta object.

    Args:
        duration: A string representing the duration in the format '1h26m34s'

    Returns:
        A timedelta object representing the duration
    """
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
    """
    Format a timedelta object as a string in the format 'hh:mm:ss'.

    Args:
        td: A timedelta object

    Returns:
        A string representing the timedelta in the format 'hh:mm:ss'
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
