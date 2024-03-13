## Author: @Chasinggoodgrades
## Date: 2023-9-24
## Version: 1.0.1

## Imports
import discord
import requests
import asyncio
import re

## Initialize bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Global variables
posted_lobbies = {}
regex_patterns = []

# Define the file path to regex.txt
file_path = 'regex.txt'
def read_regex_patterns(file_path):
    patterns = []
    with open(file_path, 'r') as file:
        for line in file:
            pattern = line.strip()  # Remove leading/trailing whitespace
            patterns.append(pattern)
    return patterns

# Read regex patterns from regex.txt
regex_patterns = read_regex_patterns(file_path)

def CheckStatus():
    response = requests.get("https://api.wc3stats.com/gamelist")
    print(response.status_code)
    print(response.json())
    return response.status_code
def getLobbies():
    response = requests.get("https://api.wc3stats.com/gamelist")
    body = response.json()['body']
    lobbies = []

    ## Regex
    exclude_map_pattern = re.compile(r'(TD|Tower)', re.IGNORECASE)
    map_name_pattern = re.compile('|'.join(regex_patterns), re.IGNORECASE)
    for lobby in body:
        map_name = lobby['map']
        if re.search(exclude_map_pattern, map_name):
            continue
        if re.search(map_name_pattern, map_name):
            lobbies.append(lobby)
    print(lobbies)
    return lobbies
def getLobbyString(lobby):
    return f"{lobby['name']}"
def embedLobby(lobby):
    embed = discord.Embed(color=0x00ff00)
    embed.set_author(name=getLobbyString(lobby))
    embed.add_field(name="Host", value=lobby['host'], inline=True)
    embed.add_field(name="Players", value=f"{lobby['slotsTaken']} / {lobby['slotsTotal']}", inline=True)
    embed.add_field(name="", value=lobby['map'], inline=False)
    return embed

## Listen for commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Check if the message is a command to list regex patterns
    if message.content.startswith('!list'):
        await list_regex(message.channel)

    # Check if the message is a command to add a new regex pattern
    elif message.content.startswith('!add'):
        await add_regex(message.channel, message.content[len('!add'):])

    # Check if the message is a command to remove an existing regex pattern
    elif message.content.startswith('!remove'):
        await remove_regex(message.channel, message.content[len('!remove'):])

    elif message.content.startswith('!status'):
        await message.channel.send(CheckStatus())

    else:
        # Your existing code for other functionalities...
        pass

async def list_regex(channel):
    """List all current regex patterns."""
    responsestring = "\n".join(regex_patterns)
    await channel.send(responsestring if responsestring else "No patterns found.")

async def add_regex(channel, new_pattern):
    """Add a new regex pattern."""
    regex_patterns.append(new_pattern.strip())
    with open(file_path, 'a') as file:
        file.write(new_pattern.strip() + '\n')
    await channel.send(f"'{new_pattern.strip()}' added to search list.")

async def remove_regex(channel, pattern_to_remove):
    """Remove an existing regex pattern."""
    pattern_to_remove = pattern_to_remove.strip()
    if pattern_to_remove in regex_patterns:
        regex_patterns.remove(pattern_to_remove)
        with open(file_path, 'w') as file:
            for pattern in regex_patterns:
                file.write(pattern + '\n')
        await channel.send(f"'{pattern_to_remove}' removed from search list.")
    else:
        await channel.send("Not found")

async def updateLobbyMessages():
    await client.wait_until_ready()
    channel = client.get_channel(_CHANNEL_HERE_)
    while not client.is_closed():
        lobbies = getLobbies()

        # Check for removed lobbies and turn their embeds red
        for lobby_id, posted_lobby_message in posted_lobbies.copy().items():
            if lobby_id not in [lobby['id'] for lobby in lobbies]:
                embed = posted_lobby_message.embeds[0]
                embed.color = discord.Color.red()
                await posted_lobby_message.edit(embed=embed)
                del posted_lobbies[lobby_id]

        # Update or post new lobbies
        for lobby in lobbies:
            lobby_id = lobby['id']
            if lobby_id in posted_lobbies:
                # Lobby already posted, update the embed
                embed = embedLobby(lobby)
                await posted_lobbies[lobby_id].edit(embed=embed)
            else:
                # New lobby, post a new embed
                embed = embedLobby(lobby)
                message = await channel.send(embed=embed)
                posted_lobbies[lobby_id] = message

        await asyncio.sleep(15)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('Warcraft III'))
    await updateLobbyMessages()

## Run bot
client.run('API_KEY_HERE')
