# Deadlock Highlight Clipper

A Python tool for automatically extracting highlight clips from Twitch VODs of Deadlock gameplay.

## Overview

Deadlock Highlight Clipper is a utility that:

1. Connects to the Twitch API to retrieve VODs from a specified channel
2. Fetches match data from the Deadlock API for a specific player
3. Detects significant events in the matches
4. Extracts video clips of these events from the Twitch VODs
5. Saves the clips with descriptive filenames for easy organization

This tool is perfect for content creators, streamers, or players who want to automatically extract their best moments from Deadlock gameplay without manually reviewing hours of footage.

## Features

- **Twitch Integration**: Automatically retrieves VODs from a specified Twitch channel
- **Deadlock API Integration**: Fetches detailed match data and player statistics
- **Event Detection**: Identifies significant gameplay events
- **Clip Extraction**: Precisely extracts video clips of detected events
- **Organized Output**: Saves clips with descriptive filenames including event type, timestamp, and player information

## Requirements

- Twitch API credentials (Client ID and Access Token)
- [twitch-dl](https://github.com/ihabunek/twitch-dl) command-line tool

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/deadlock-highlight-clipper.git
   cd deadlock-highlight-clipper
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Set up environment variables:
   ```
   export TWITCH_CLIENT_ID=your_client_id
   export TWITCH_ACCESS_TOKEN=your_access_token
   ```

## Usage

Run the tool with the following command:

```
python -m deadlock_highlight_clipper -c CHANNEL_ID -s STEAM_ID3
```

Where:
- `CHANNEL_ID` is the Twitch channel ID to extract VODs from
- `STEAM_ID3` is the Steam ID3 of the player whose highlights you want to extract

Example:
```
python -m deadlock_highlight_clipper -c 12345678 -s 76561198123456789
```

## Output

Clips are saved in the following directory structure:
```
events/
├── {steam_id}/
│   ├── {video_id}/
│   │   ├── {match_id}/
│   │   │   ├── {start_time}-{end_time}-{event_name}-{event_details}.mp4
```

## Extending

The event detection system is designed to be extensible. To add new event types:

1. Create a new class that inherits from the `Event` base class
2. Implement the required methods: `detect()` and `filename_postfix()`
3. Add your new event class to the `EventDetector.detect_events()` method

## Acknowledgements

- [Deadlock API](https://deadlock-api.com) for providing match data
- [Twitch API](https://dev.twitch.tv/docs/api/) for VOD access
- [twitch-dl](https://github.com/ihabunek/twitch-dl) for VOD downloading capabilities
