import discord
from discord import app_commands
import aiohttp
import os
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Tags storage
TAGS_FILE = 'data/tags.json'
_tags = []

def load_tags_from_file():
    """Load tags from file"""
    global _tags
    try:
        import json
        with open(TAGS_FILE, 'r') as f:
            tags = json.load(f)
            # Filter out empty or invalid tags
            _tags = [tag for tag in tags if tag and isinstance(tag, str) and len(tag.strip()) > 0]
            print(f'Loaded {len(_tags)} tags from file')
    except FileNotFoundError:
        print('Tags file not found!')
        _tags = []
    except Exception as e:
        print(f'Error loading tags: {e}')
        _tags = []

async def tag_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete function for tag parameters"""
    # Filter tags based on what user is typing
    if current:
        matches = [tag for tag in _tags if current.lower() in tag.lower()]
    else:
        matches = _tags
    
    # Discord limits to 25 choices
    matches = matches[:25]
    
    # Ensure all choices have valid names (1-100 chars)
    return [
        app_commands.Choice(name=tag, value=tag)
        for tag in matches
        if tag and len(tag) >= 1 and len(tag) <= 100
    ]

async def fetch_cat_with_retry(url: str, max_retries: int = 3):
    """Fetch cat image/gif from URL with retry logic for 500 errors"""
    import asyncio
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read(), None
                    elif response.status == 500 and attempt < max_retries - 1:
                        # Server error, wait a bit and retry
                        await asyncio.sleep(1)
                        continue
                    else:
                        return None, response.status
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return None, str(e)
    
    return None, 500


@client.event
async def on_ready():
    # Load tags from file
    load_tags_from_file()
    
    # Sync commands with Discord
    await tree.sync()
    print(f'Bot logged in as {client.user}')
    print(f'Bot is ready to serve cats!')

@tree.command(name="cat-tags", description="List all available cat tags")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def cat_tags(interaction: discord.Interaction):
    """Fetches and displays all available cat tags from cataas.com"""
    await interaction.response.defer()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/api/tags') as response:
                if response.status == 200:
                    tags = await response.json()
                    
                    if tags:
                        # Format tags nicely - split into chunks to avoid message length limits
                        tag_list = ", ".join(sorted(tags))
                        
                        # Discord has a 2000 character limit, so split if needed
                        if len(tag_list) <= 1900:
                            await interaction.followup.send(
                                f"**Available Cat Tags:**\n{tag_list}\n\n"
                                f"Use these with any command like: `/cat tag:cute` or `/cat-gif-says text:Hello tag:funny`"
                            )
                        else:
                            # Split into multiple messages
                            chunks = []
                            current_chunk = []
                            current_length = 0
                            
                            for tag in sorted(tags):
                                tag_with_comma = tag + ", "
                                if current_length + len(tag_with_comma) > 1800:
                                    chunks.append(", ".join(current_chunk))
                                    current_chunk = [tag]
                                    current_length = len(tag_with_comma)
                                else:
                                    current_chunk.append(tag)
                                    current_length += len(tag_with_comma)
                            
                            if current_chunk:
                                chunks.append(", ".join(current_chunk))
                            
                            # Send first chunk with header
                            await interaction.followup.send(
                                f"**Available Cat Tags (Part 1/{len(chunks)}):**\n{chunks[0]}"
                            )
                            
                            # Send remaining chunks
                            for i, chunk in enumerate(chunks[1:], 2):
                                await interaction.followup.send(
                                    f"**Part {i}/{len(chunks)}:**\n{chunk}"
                                )
                            
                            await interaction.followup.send(
                                "Use these with any command like: `/cat tag:cute` or `/cat-gif-says text:Hello tag:funny`"
                            )
                    else:
                        await interaction.followup.send("No tags found.")
                else:
                    await interaction.followup.send(
                        f"Failed to fetch tags. Status code: {response.status}"
                    )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="cat", description="Get a random cat picture")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.autocomplete(tag=tag_autocomplete)
async def cat(interaction: discord.Interaction, tag: str = None):
    """Fetches a random cat image from cataas.com and sends it to Discord
    
    Args:
        tag: Optional tag to filter cats (e.g., "cute", "sleeping", "grumpy"). Separate multiple tags with commas.
    """
    await interaction.response.defer()
    
    try:
        import urllib.parse
        
        # Build URL with optional tag
        if tag:
            encoded_tag = urllib.parse.quote(tag.replace(',', ','))
            url = f'https://cataas.com/cat/{encoded_tag}'
        else:
            url = 'https://cataas.com/cat'
        
        # Fetch with retry
        image_data, error = await fetch_cat_with_retry(url)
        
        if image_data:
            # Create a Discord file from the image data
            file = discord.File(
                fp=BytesIO(image_data),
                filename='cat.jpg'
            )
            
            # Send the image
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send(
                f"Failed to fetch cat image after retrying. Error: {error}"
            )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="cat-gif", description="Get a random animated cat GIF")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def cat_gif(interaction: discord.Interaction):
    """Fetches a random cat GIF from cataas.com and sends it to Discord"""
    await interaction.response.defer()
    
    try:
        url = 'https://cataas.com/cat/gif'
        
        # Fetch with retry
        gif_data, error = await fetch_cat_with_retry(url)
        
        if gif_data:
            # Create a Discord file from the GIF data
            file = discord.File(
                fp=BytesIO(gif_data),
                filename='cat.gif'
            )
            
            # Send the GIF
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send(
                f"Failed to fetch cat GIF after retrying. Error: {error}"
            )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="cat-says", description="Get a cat picture with custom text")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.autocomplete(tag=tag_autocomplete)
async def cat_says(
    interaction: discord.Interaction, 
    text: str,
    tag: str = None,
    font_size: int = None,
    font_color: str = None
):
    """Fetches a cat image with custom text from cataas.com and sends it to Discord
    
    Args:
        text: The text to display on the cat image
        tag: Optional tag to filter cats (e.g., "cute", "grumpy"). Separate multiple tags with commas.
        font_size: Optional font size (e.g., 50, 100)
        font_color: Optional font color (e.g., "red", "blue", "#FF0000")
    """
    await interaction.response.defer()
    
    try:
        # URL encode the text to handle special characters
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        # Build the URL with optional tag
        if tag:
            encoded_tag = urllib.parse.quote(tag.replace(',', ','))
            url = f'https://cataas.com/cat/{encoded_tag}/says/{encoded_text}'
        else:
            url = f'https://cataas.com/cat/says/{encoded_text}'
        
        # Add optional query parameters
        params = []
        
        if font_size is not None:
            params.append(f'fontSize={font_size}')
        
        if font_color is not None:
            params.append(f'fontColor={urllib.parse.quote(font_color)}')
        
        if params:
            url += '?' + '&'.join(params)
        
        # Fetch with retry
        image_data, error = await fetch_cat_with_retry(url)
        
        if image_data:
            # Create a Discord file from the image data
            file = discord.File(
                fp=BytesIO(image_data),
                filename='cat_says.jpg'
            )
            
            # Send the image
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send(
                f"Failed to fetch cat image after retrying. Error: {error}"
            )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

@tree.command(name="cat-gif-says", description="Get an animated cat GIF with custom text")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def cat_gif_says(
    interaction: discord.Interaction, 
    text: str,
    font_size: int = None,
    font_color: str = None,
    filter: str = None
):
    """Fetches an animated cat GIF with custom text from cataas.com and sends it to Discord
    
    Args:
        text: The text to display on the cat GIF
        font_size: Optional font size (e.g., 20, 50, 100)
        font_color: Optional font color (e.g., "red", "orange", "#FF0000")
        filter: Optional filter (e.g., "mono", "sepia", "negative", "paint", "blur")
    """
    await interaction.response.defer()
    
    try:
        # URL encode the text to handle special characters
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        # Build the URL
        url = f'https://cataas.com/cat/gif/says/{encoded_text}'
        
        # Add optional query parameters
        params = []
        
        if font_size is not None:
            params.append(f'fontSize={font_size}')
        
        if font_color is not None:
            params.append(f'fontColor={urllib.parse.quote(font_color)}')
        
        if filter is not None:
            params.append(f'filter={urllib.parse.quote(filter)}')
        
        if params:
            url += '?' + '&'.join(params)
        
        # Fetch with retry
        gif_data, error = await fetch_cat_with_retry(url)
        
        if gif_data:
            # Create a Discord file from the GIF data
            file = discord.File(
                fp=BytesIO(gif_data),
                filename='cat_gif_says.gif'
            )
            
            # Send the GIF
            await interaction.followup.send(file=file)
        else:
            await interaction.followup.send(
                f"Failed to fetch cat GIF after retrying. Error: {error}"
            )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
        exit(1)
    
    client.run(token)
