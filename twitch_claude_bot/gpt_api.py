"""
This module provides functionality for interacting with the GPT API.

It includes functions for loading configurations, constructing prompts,
sending requests to the GPT API, and managing message history.
"""

import aiohttp
import json
import os
import yaml
import datetime
from collections import deque
from typing import Dict, List

# Constants
MAX_CONTEXT_MESSAGES = 10
CONFIG_FILE = 'config.yml'
PERSONAS_FILE = 'twitch_claude_bot/personas/gpt_personas.json'
LOG_FILE = 'gpt_interactions.log'
# Load configuration
def load_config(file_name: str) -> Dict:
    """
    Load configuration from a YAML file.

    Args:
        file_name (str): The name of the configuration file.

    Returns:
        Dict: A dictionary containing the configuration data.
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(script_dir, file_name)
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: '{file_name}' not found at {file_path}")
        return {}

on_rtd = os.environ.get('READTHEDOCS') == 'True'

if on_rtd:
    config = {
        'ai_engines': {
            'gpt': {
                'api_key': 'mock_api_key'
            },
            'claude': {
                'api_key': 'mock_claude_api_key'
            }
        },
        'twitch': {
            'channel': 'mock_channel',
            'bot_username': 'mock_bot_username',
            'oauth_token': 'mock_oauth_token'
        }
    }
else:
    config = load_config(CONFIG_FILE)
    
GPT_API_KEY = config.get('ai_engines', {}).get('gpt', {}).get('api_key', '')
GPT_API_URL = 'https://api.openai.com/v1/chat/completions'

# Load personas
GPT_PERSONAS = load_config(PERSONAS_FILE)

message_history = deque(maxlen=MAX_CONTEXT_MESSAGES)

async def get_gpt_response(prompt: str, persona: str = 'gpt_wizard') -> str:
    """
    Get a response from the GPT API based on the given prompt and persona.

    Args:
        prompt (str): The user's input prompt.
        persona (str, optional): The persona to use for the response. Defaults to 'gpt_wizard'.

    Returns:
        str: The AI-generated response.

    Raises:
        Exception: If the API request fails.
    """
    persona_config = GPT_PERSONAS.get(persona, {})
    full_prompt = construct_full_prompt(prompt, persona_config)
    conversation = construct_conversation(full_prompt)

    async with aiohttp.ClientSession() as session:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {GPT_API_KEY}'
        }
        data = {
            'model': 'gpt-4',
            'messages': conversation,
            'max_tokens': persona_config.get('max_tokens', 150),
            'temperature': persona_config.get('temperature', 0.7)
        }
        async with session.post(GPT_API_URL, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                response_text = result['choices'][0]['message']['content']
                max_length = persona_config.get('max_response_length', 500)
                response_text = response_text[:min(max_length, 500)]
                update_message_history(prompt, response_text)
                log_interaction(prompt, response_text)
                return response_text
            else:
                error_message = await response.text()
                raise Exception(f"API request failed with status {response.status}: {error_message}")

def construct_full_prompt(prompt: str, persona_config: Dict) -> str:
    """
    Construct a full prompt by combining the user's input with persona configuration.

    Args:
        prompt (str): The user's input prompt.
        persona_config (Dict): The configuration for the selected persona.

    Returns:
        str: The full constructed prompt.
    """
    prompt_parts = [
        persona_config.get('system_prompt', ''),
        f"Name: {persona_config.get('name', '')}",
        f"Description: {persona_config.get('description', '')}",
        prompt
    ]
    return '\n\n'.join(prompt_parts)

def construct_conversation(full_prompt: str) -> List[Dict]:
    """
    Construct a conversation history including the new prompt.

    Args:
        full_prompt (str): The full constructed prompt.

    Returns:
        List[Dict]: A list of conversation messages in the format required by the API.
    """
    conversation = [
        {"role": 'user' if i % 2 == 0 else 'assistant', "content": msg}
        for i, msg in enumerate(message_history)
    ]
    conversation.append({"role": "user", "content": full_prompt})
    return conversation

def update_message_history(prompt: str, response: str) -> None:
    """
    Update the message history with the new prompt and response.

    Args:
        prompt (str): The user's input prompt.
        response (str): The AI-generated response.
    """
    message_history.extend([prompt, response])

def log_interaction(prompt: str, response: str) -> None:
    """
    Log the interaction between the user and the AI.

    Args:
        prompt (str): The user's input prompt.
        response (str): The AI-generated response.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\nPrompt: {prompt}\nFull Answer: {response}\n\n"
    
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = os.path.join(script_dir, LOG_FILE)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)

def clear_message_history() -> None:
    """Clear the message history."""
    message_history.clear()