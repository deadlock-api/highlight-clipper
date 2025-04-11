"""
Configuration settings

This module centralizes all configuration settings for the application,
including environment variables, constants, and default values.
"""

import os
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Config:
    log_level: str = os.environ.get("LOG_LEVEL", "DEBUG")

    # Twitch
    twitch_client_id: str = os.environ.get("TWITCH_CLIENT_ID", "")
    twitch_access_token: str = os.environ.get("TWITCH_ACCESS_TOKEN", "")

    # Video
    clip_padding: timedelta = timedelta(
        seconds=int(os.environ.get("CLIP_PADDING_SECONDS", "10"))
    )

    # Event detection
    multikill_min_kills: int = int(os.environ.get("MULTIKILL_MIN_KILLS", "3"))
    multikill_threshold_seconds: int = int(
        os.environ.get("MULTIKILL_THRESHOLD_SECONDS", "10")
    )
    team_fights_min_kills: int = int(os.environ.get("TEAM_FIGHTS_MIN_KILLS", "5"))
    team_fights_threshold_seconds: int = int(
        os.environ.get("TEAM_FIGHTS_THRESHOLD_SECONDS", "10")
    )

    # Output
    output_directory: str = os.environ.get("OUTPUT_DIRECTORY", "clips")
