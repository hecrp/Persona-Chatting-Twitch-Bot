"""
This is the main entry point for the Twitch Claude Bot application.

It sets up logging and initializes the TwitchBot.
"""

from twitch_bot import TwitchBot
import logging
import os
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    config_path = '../config.yml'
    if not os.path.exists(config_path):
        # Si estamos en Read the Docs, usamos valores por defecto
        if os.environ.get('READTHEDOCS') == 'True':
            return {
                'twitch': {
                    'channel': 'example_channel',
                    'bot_username': 'example_bot',
                    'oauth_token': 'example_oauth_token'
                },
                'ai_engines': {
                    'claude': {'api_key': 'example_claude_key'},
                    'gpt': {'api_key': 'example_gpt_key'}
                }
            }
        else:
            raise FileNotFoundError(f"Config file '{config_path}' not found")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Usa esta función en lugar de cargar directamente el archivo
config = load_config()

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