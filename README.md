# Discord Cat Bot

A feature-rich Discord bot that fetches random cat images and GIFs from [cataas.com](https://cataas.com) and sends them to Discord channels. Supports both server and user installation!

## Features

- `/cat [tag]` - Get a random cat picture, optionally filtered by tag (90+ tags with autocomplete!)
- `/cat-gif` - Get a random animated cat GIF
- `/cat-says <text> [tag] [font_size] [font_color]` - Get a cat picture with custom text
- `/cat-gif-says <text> [font_size] [font_color] [filter] [type]` - Get an animated cat GIF with custom text and effects
- `/cat-tags` - List all available tags
- **User-installable** - Install to your account and use in ANY server or DM!
- **Auto-retry** - Automatically retries on server errors for reliability
- **Tag autocomplete** - Discord dropdown shows available tags as you type

## Project Structure

```
discord-cat-bot/
├── bot.py                              # Main bot code
├── requirements.txt                     # Python dependencies
├── .env.example                         # Example environment file
├── README.md                            # This file
├── DEPLOYMENT.md                        # Server deployment guide
├── data/
│   └── tags.json                        # Curated list of cat tags
└── scripts/
    ├── install-service.sh               # Linux service installer
    ├── install-windows-service.ps1      # Windows service installer
    ├── run-windows-service.bat          # Windows background runner
    └── cat-bot.service                  # Systemd service template
```

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord bot token

### Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under the bot's username, click "Reset Token" to get your bot token
5. Enable the following Privileged Gateway Intents (if needed):
   - Message Content Intent (optional for this bot)

### Making the Bot User-Installable (Works in DMs and Servers!)

6. Go to "Installation" in the left sidebar
7. Under "Installation Contexts", check both:
   - **Guild Install** (for server installation)
   - **User Install** (for user installation - allows use in DMs!)
8. Under "Install Link", select "Discord Provided Link"
9. Under "Default Install Settings":
   - For **Guild Install**: Add scopes `bot` and `applications.commands`, permissions: `Send Messages`, `Attach Files`
   - For **User Install**: Add scope `applications.commands` (no permissions needed)
10. Go to "OAuth2" > "URL Generator"
11. Check both "Guild Install" and "User Install"
12. Select scopes: `applications.commands` (and `bot` for guild install)
13. Select bot permissions: `Send Messages`, `Attach Files`
14. Copy the generated URL and open it in your browser to install the bot
    - You can choose to install it to your user account (works in any server/DM)
    - Or install it to a specific server
    - Or both!

### Installation

1. Clone or download this repository

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory:
```bash
cp .env.example .env
```

4. Edit the `.env` file and add your Discord bot token:
```
DISCORD_BOT_TOKEN=your_actual_bot_token_here
```

### Running the Bot

**For testing/development:**
```bash
python bot.py
```

You should see a message saying the bot is logged in and ready.

## Running 24/7 as a Service

### Linux (Recommended for servers)

Use the provided installer script:

```bash
chmod +x scripts/install-service.sh
./scripts/install-service.sh
```

This will:
- Create a virtual environment if needed
- Install dependencies
- Set up a systemd service
- Start the bot automatically

**Manage the service:**
```bash
sudo systemctl status cat-bot    # Check bot status
sudo systemctl stop cat-bot      # Stop the bot
sudo systemctl start cat-bot     # Start the bot
sudo systemctl restart cat-bot   # Restart the bot
sudo journalctl -u cat-bot -f    # View live logs
```

The bot will automatically start on server reboot and restart if it crashes.

### Windows

**Option 1: Simple Background Runner (Easiest)**

Double-click `scripts/run-windows-service.bat` to run the bot in the background. It will automatically restart if it crashes. Keep the window open.

**Option 2: Windows Service (Runs in background, survives reboots)**

1. Download NSSM from https://nssm.cc/download or install via Chocolatey:
   ```powershell
   choco install nssm
   ```

2. Right-click `scripts/install-windows-service.ps1` and select "Run as Administrator"

3. The bot will be installed as a Windows Service

**Manage the Windows service:**
- Open `services.msc` or use these commands:
```powershell
nssm status DiscordCatBot     # Check status
nssm stop DiscordCatBot       # Stop the bot
nssm start DiscordCatBot      # Start the bot
nssm restart DiscordCatBot    # Restart the bot
```

### Docker (Optional)

Coming soon! If you want to run this in Docker, let me know.

## Usage

Once the bot is running and installed:

**If installed to your user account:**
- Use `/cat` in ANY server or DM conversation
- Use `/cat-gif` for animated cat GIFs
- Use `/cat-says Hello World!` for a cat with custom text
- **When you type a tag parameter, you'll see a dropdown list to choose from!**
- The bot follows you everywhere!

**If installed to a server:**
- Use `/cat` in any channel where the bot has permissions
- Use `/cat-gif` for animated cat GIFs
- Use `/cat-says Your text here` for custom messages
- **Tag autocomplete makes it easy to find the perfect cat!**

The bot will fetch a random cat image and send it to the channel or DM.

### Examples:

**See available tags:**
- `/cat-tags` - Shows all valid tags you can use

**Basic commands:**
- `/cat` - Random cat picture
- `/cat tag:cute` - Random cute cat
- `/cat tag:sleeping,fluffy` - Random cat with multiple tags (sleeping AND fluffy)
- `/cat-gif` - Random animated cat
- `/cat-gif tag:funny` - Random funny animated cat

**Cat with text:**
- `/cat-says Hello!` - Cat saying "Hello!"
- `/cat-says text:Meow tag:grumpy` - Grumpy cat saying "Meow"
- `/cat-says text:Good morning everyone` - Cat with your custom message
- `/cat-says text:Hello! font_size:100` - Cat with bigger text
- `/cat-says text:Hello! font_color:red` - Cat with red text
- `/cat-says text:Hi tag:cute font_size:80 font_color:#FF69B4` - Cute cat with custom size and pink color

**Animated cat GIF with text (the ultimate command!):**
- `/cat-gif-says Hello!` - Animated cat saying "Hello!"
- `/cat-gif-says text:Meow tag:funny` - Funny animated cat saying "Meow"
- `/cat-gif-says text:Meow font_size:50 font_color:orange` - Orange text on animated cat
- `/cat-gif-says text:Cool! filter:mono` - Animated cat with black & white filter
- `/cat-gif-says text:Hi tag:cute filter:sepia type:square` - Cute cat, sepia filter, square format
- `/cat-gif-says text:Party! tag:funny font_size:60 font_color:yellow filter:blur` - All the effects!

**Available tags:** A curated list of 90+ popular tags including cute, funny, sleeping, grumpy, fluffy, kitten, orange, black, white, tabby, siamese, persian, maine coon, and many more!

**Pro tip: When you start typing a tag, Discord will show you autocomplete suggestions with all available tags!**

**Available filters:** mono, sepia, negative, paint, blur

**Available types:** square, small, medium

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Add more curated tags to `data/tags.json`

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Cat images provided by [cataas.com](https://cataas.com) - Cat as a Service
- Built with [discord.py](https://github.com/Rapptz/discord.py)

## Troubleshooting

- **Commands not showing up**: Wait a few minutes after starting the bot for Discord to sync the commands. You can also try kicking and re-inviting the bot.
- **Bot doesn't respond**: Make sure the bot has permissions to send messages and attach files in the channel.
- **"DISCORD_BOT_TOKEN not found" error**: Make sure you've created a `.env` file with your bot token.

## License

This project is open source and available for anyone to use.

