# Persona Chatting Twitch Bot

This personal project consists of a Twitch chatbot that uses AI language models (Claude and GPT) to interact with viewers in different personas. The bot can switch between different AI engines and personas, providing a unique and engaging experience for Twitch chat participants.

For detailed documentation, please visit our [ReadTheDocs page](https://persona-chatting-twitch-bot.readthedocs.io).
## Features

- Supports two AI engines: Claude and GPT.
- Multiple personas for each engine.
- Commands to change personas and engines.
- Customizable response settings for each persona using JSON files.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/hecrp/Persona-Chatting-Twitch-Bot.git
   cd twitch-claude-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Prior to running the bot, you need to set up your Twitch credentials and gpt/claude API keys. 

1. Copy the `config.example.yml` file to `config.yml`:
   ```
   cp config.example.yml config.yml
   ```

2. Edit `config.yml` to set up your Twitch credentials and AI API keys.

## Usage

To start the bot, run:
   ```
   python main.py
   ```

## Commands

- `!prompt <text>`: Ask a question to the current persona.
- `!persona <name>`: Change the bot's persona.
- `!persona_list`: Show available personas for the current engine.
- `!engine <claude/gpt>`: Switch between Claude and GPT engines.
- `!help`: Display available commands.


## Run with Docker (Testing)

To run the Twitch Claude Bot using Docker, follow these steps:

1. Make sure you have Docker installed on your system.

2. Build the Docker image:
   ```
   docker build -t persona-chatting-bot .
   ```

3. Run the Docker container:
   ```
   docker run -d --name persona-chatting-bot persona-chatting-bot
   ```

   Note: Make sure your `config.yml` file is properly set up before building the Docker image.


## Customizing Personas

You can customize the bot's personas by modifying the `claude_personas.json` and `gpt_personas.json` files located in the `twitch_claude_bot/personas/` directory. Each persona is defined as a JSON object with specific attributes that control the AI's behavior and responses.

Here's a small example of how a persona is defined in `claude_personas.json`:

```json
{
  "claude_the_wizard": {
    "name": "Claude The Wizard Persona",
    "description": "A wise wizard in the style of Merlin, knowledgeable in arcane secrets and ancient magic.
                     Always give answers using a maximum of 30   words but don't metion it when talking.",
    "prompt_prefix": "You are Claude the Wizard, a powerful sorcerer with centuries of knowledge. 
                     Your voice is deep and resonant, and your words are    sprinkled with arcane terms.",
    "prompt_suffix": "Remember to maintain your role as a wise wizard at all times.",
    "background": "You were born eons ago in an era of great wizards and have lived through multiple magical ages.",
    "personality_traits": [
      "Wise",
      "Mysterious"
    ],
    "knowledge_areas": [
      "Elemental magic",
      "Divination"
    ],
    "speech_patterns": [
      "Compares complex concepts to natural phenomena"
    ],
    "max_response_length": 300
  },
  // Add more personas as needed
}  
```

Replace `name` with a unique name for your persona, and customize the `description` and any other attribute as needed. 


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Twitch API](https://dev.twitch.tv/docs/api/)
- [Anthropic Claude API](https://www.anthropic.com)
- [OpenAI GPT API](https://openai.com/api/)

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
