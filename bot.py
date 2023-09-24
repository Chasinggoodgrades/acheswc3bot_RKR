## Author: @Chasinggoodgrades
## Date: 2023-9-24
## Version: 1.0.0

## Imports
import discord
import requests
import asyncio

## Initialize bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

## Global variables
posted_lobbies = {}
def getLobbies():
    response = requests.get("https://api.wc3stats.com/gamelist")
    body = response.json()['body']
    lobbies = []
    for lobby in body:
        if "Hero" in lobby['map']:
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

async def updateLobbyMessages():
    await client.wait_until_ready()
    channel = client.get_channel(452619334150520844)
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
    await client.change_presence(activity=discord.Game('Run Kitty Run'))
    await updateLobbyMessages()

## Run bot
client.run('MTEwNDI3NTQyMDUxNTQwMTczOQ.GjaH6A.FuOgsQOcej4dGzIdIFlRwQtR-P5QotMaHEKlRM')
