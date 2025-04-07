import asyncio
import logging
from argparse import ArgumentParser

import coloredlogs

from deadlock_highlight_clipper.config import Config
from deadlock_highlight_clipper.core import run

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("hpack").setLevel(logging.INFO)
coloredlogs.install(level=Config.log_level)

LOGGER = logging.getLogger(__name__)


def main():
    """
    Main entry point for the Deadlock Highlight Clipper.
    """
    parser = ArgumentParser(description="Deadlock Highlight Clipper")
    parser.add_argument(
        "-c", "--channel-id", type=str, required=True, help="Twitch channel ID"
    )
    parser.add_argument("-s", "--steam-id3", type=int, required=True, help="Steam ID3")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.channel_id, args.steam_id3))
    except KeyboardInterrupt:
        LOGGER.info("Interrupted by user")
    except Exception as e:
        LOGGER.exception(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
