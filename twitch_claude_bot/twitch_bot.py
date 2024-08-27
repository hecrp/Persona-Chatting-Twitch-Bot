"""
This module contains the main TwitchBot class and related functionality.

The TwitchBot class is responsible for handling Twitch chat commands and
interacting with AI engines (Claude and GPT) to generate responses.
"""

import os
import yaml
from twitchio.ext import commands
from claude_api import get_claude_response, CLAUDE_PERSONAS, clear_message_history as clear_claude_history
from gpt_api import get_gpt_response, GPT_PERSONAS, clear_message_history as clear_gpt_history
import re
from typing import Dict, Any

# Constants
CONFIG_FILE = 'config.yml'
MAX_MESSAGE_LENGTH = 500

def load_config(file_name: str) -> Dict[str, Any]:
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(script_dir, file_name)
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        print(f"Error: '{file_name}' not found at {config_path}")
        return {}

config = load_config(CONFIG_FILE)
TWITCH_OAUTH_TOKEN = config.get('twitch', {}).get('oauth_token', '')
TWITCH_CHANNEL = config.get('twitch', {}).get('channel', '')

class TwitchBot(commands.Bot):
    """
    A Twitch bot that interacts with AI engines to respond to chat commands.

    This bot can switch between Claude and GPT engines, change personas,
    and respond to various commands in the Twitch chat.
    """

    def __init__(self):
        """
        Initialize the TwitchBot with default settings.
        """
        super().__init__(token=TWITCH_OAUTH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])
        self.current_engine = 'claude'
        self.current_persona = 'claude_the_wizard'

    async def event_ready(self):
        """
        Called once when the bot goes online.
        """
        print(f'Listo! | {self.nick}')

    async def event_message(self, message):
        """
        Runs every time a message is sent in chat.

        Args:
            message: The message object containing information about the sent message.
        """
        if message.echo:
            return
        await self.handle_commands(message)

    async def split_and_send_message(self, ctx: commands.Context, message: str):
        """
        Split a long message into smaller chunks and send them sequentially.

        This method breaks down a long message into sentences and sends them in chunks
        that do not exceed the maximum message length allowed by Twitch.

        Args:
            ctx (commands.Context): The context of the command execution.
            message (str): The message to be split and sent.
        """
        sentences = re.split('(?<=[.!?]) +', message)
        current_message = ""
        
        for sentence in sentences:
            if len(current_message) + len(sentence) + 1 > MAX_MESSAGE_LENGTH:
                if current_message:
                    await ctx.send(current_message.strip())
                    current_message = ""
            current_message += sentence + " "
        
        if current_message:
            await ctx.send(current_message.strip())

    @commands.command(name='prompt')
    @commands.cooldown(rate=1, per=3, bucket=commands.Bucket.user)
    async def prompt(self, ctx: commands.Context):
        """
        Handle the !prompt command to generate AI responses.

        This method extracts the prompt from the user's message, generates an AI response,
        and sends it back to the chat in manageable chunks.

        Args:
            ctx (commands.Context): The context of the command execution.
        """
        try:
            prompt = ctx.message.content.split('!prompt', 1)[1].strip()
            response = await self.get_ai_response(prompt)
            await self.split_and_send_message(ctx, response)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def get_ai_response(self, prompt: str) -> str:
        """
        Generate an AI response based on the current engine and persona.

        This method calls the appropriate AI engine (Claude or GPT) with the given prompt
        and current persona to generate a response.

        Args:
            prompt (str): The user's input prompt.

        Returns:
            str: The generated AI response prefixed with the persona name.
        """
        if self.current_engine == 'claude':
            response = await get_claude_response(prompt, self.current_persona)
            persona_name = CLAUDE_PERSONAS[self.current_persona].get('name', self.current_persona.replace('_', ' ').title())
        else:  # GPT
            response = await get_gpt_response(prompt, self.current_persona)
            persona_name = GPT_PERSONAS[self.current_persona].get('name', self.current_persona.replace('_', ' ').title())
        
        return f"{persona_name}: {response}"

    @commands.command(name='persona')
    async def persona(self, ctx: commands.Context, persona: str):
        """
        Change the current AI persona.

        This method updates the current persona if the provided persona name is valid
        for the current AI engine.

        Args:
            ctx (commands.Context): The context of the command execution.
            persona (str): The name of the persona to switch to.
        """
        personas = CLAUDE_PERSONAS if self.current_engine == 'claude' else GPT_PERSONAS
        if persona in personas:
            self.current_persona = persona
            persona_name = personas[persona].get('name', persona.replace('_', ' ').title())
            await ctx.send(f"Persona changed to {persona_name}")
        else:
            await ctx.send(f"Character not found. Available options: {', '.join(personas.keys())}")

    def get_persona_name(self, persona_data: Dict[str, Any]) -> str:
        """
        Get the display name of the current persona.

        This method returns the name of the current persona, using the 'name' field
        if available, or a formatted version of the persona key otherwise.

        Args:
            persona_data (Dict[str, Any]): The persona data dictionary.

        Returns:
            str: The display name of the current persona.
        """
        if self.current_engine == 'claude':
            return persona_data.get('name', self.current_persona.replace('_', ' ').title())
        else:
            return persona_data.get('name', self.current_persona.replace('_', ' ').title())

    @commands.command(name='engine')
    async def engine(self, ctx: commands.Context, engine: str):
        """
        Change the current AI engine.

        This method switches between Claude and GPT engines and sets a default persona
        for the newly selected engine.

        Args:
            ctx (commands.Context): The context of the command execution.
            engine (str): The name of the engine to switch to ('claude' or 'gpt').
        """
        if engine.lower() in ['claude', 'gpt']:
            self.current_engine = engine.lower()
            self.current_persona = 'claude_the_wizard' if engine.lower() == 'claude' else 'gpt_wizard'
            await ctx.send(f"Engine changed to {engine.upper()}. Default persona set.")
        else:
            await ctx.send("Invalid engine. Choose 'claude' or 'gpt'.")

    @commands.command(name='persona_list')
    async def persona_list(self, ctx: commands.Context):
        """
        List all available personas for the current AI engine.

        This method sends a message to the chat with all available personas
        for the currently selected AI engine.

        Args:
            ctx (commands.Context): The context of the command execution.
        """
        personas = CLAUDE_PERSONAS if self.current_engine == 'claude' else GPT_PERSONAS
        persona_names = [persona.replace('_', ' ').title() for persona in personas.keys()]
        await ctx.send(f"Available personas for {self.current_engine.upper()}: {', '.join(persona_names)}")

    @commands.command(name='help')
    async def help(self, ctx: commands.Context):
        """
        Display a list of available commands.

        This method sends a message to the chat with all available bot commands.

        Args:
            ctx (commands.Context): The context of the command execution.
        """
        commands_list = [
            "!prompt <text>",
            "!persona <persona_name>",
            "!engine <claude/gpt>",
            "!persona_list",
            "!clear_history",
            "!help"
        ]
        await ctx.send("Available commands: " + " | ".join(commands_list))

    @commands.command(name='clear_history')
    async def clear_history(self, ctx: commands.Context):
        """
        Clear the message history for the current AI engine.

        This method clears the conversation history for either Claude or GPT,
        depending on which engine is currently active.

        Args:
            ctx (commands.Context): The context of the command execution.
        """
        if self.current_engine == 'claude':
            clear_claude_history()
        else:
            clear_gpt_history()
        await ctx.send(f"Message history for {self.current_engine.upper()} has been cleared.")