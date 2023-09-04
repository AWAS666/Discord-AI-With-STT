import asyncio, os

from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
from discord import FFmpegOpusAudio
from modules.desktop_audio import DesktopAudio

#from sinks.stream_sink import StreamSink #Outputs audio to desired output audio device (tested on windows)
from sinks.whisper_sink import WhisperSink #User whisper to transcribe audio and outputs to TTS

TOKEN = os.environ['DISCORD_TOKEN']

#This is who you allow to use commands with the bot, either by role, user or both.
#can be a list, both being empty means anyone can command the bot. Roles should be lowercase, USERS requires user IDs
COMMAND_ROLES = []
COMMANDS_USERS = []

#Enter the channel IDs for which channels you want the bot to reply to users. Keep empty to allow all channels.
REPLY_CHANNELS = []

loop = asyncio.get_event_loop()
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents, loop=loop)
 
voice_channel = None

@client.command()
async def quit(ctx):
    client.close()

# join vc
@client.command()
async def join(ctx):
    global voice_channel
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        try:
            await channel.connect()
        except Exception as e:
            print(e)
        voice_channel = ctx.guild.voice_client
        source = DesktopAudio(int(os.environ['AUDIO_DEVICE_ID']))
        voice_channel.play(source)
       
        await ctx.send("Joining.")
    else:
        await ctx.send("You are not in a VC channel.")

# leave vc
@client.command()
async def leave(ctx):
    global voice_channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        voice_channel = None
    else:
        await ctx.send("Not in VC.")

@client.event
async def on_ready():
    for guild in client.guilds:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message : discord.Message):  
    #Ignore your own message
    if message.author == client.user:
            return
    
    #To ignore DMs
    if hasattr(message.channel, 'DMChannel'):
        print("Ignore DMS")
        return           
    
    if len(message.content) > 0:

        #! is a command message
        if message.content[0] == "!":
            
            if COMMAND_ROLES == [] and COMMANDS_USERS == []:
                await client.process_commands(message)
            elif message.author.id in COMMANDS_USERS:
                await client.process_commands(message)
            elif any(role.name in COMMAND_ROLES for role in message.author.roles):
                await client.process_commands(message)              
            return       


#Stops the bot if they are speaking
@client.command()
async def stop(ctx):    
    ctx.guild.voice_client.stop()

async def get_username(user_id):
    return await client.fetch_user(user_id)

client.run(TOKEN)