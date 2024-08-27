"""
This is the main entry point for the Twitch Claude Bot application.

It sets up logging and initializes the TwitchBot.
"""

from twitch_bot import TwitchBot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    The main function to run the Twitch Claude Bot.

    It initializes and runs the TwitchBot, catching and logging any exceptions that occur.
    """
    try:
        bot = TwitchBot()
        bot.run()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")

if __name__ == "__main__":
    main()