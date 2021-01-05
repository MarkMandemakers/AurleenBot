# Import modules
import discord
from discord.ext import commands
import os
import json

# Setup variables
swd = os.path.dirname(os.getcwd()) + "\AurleenBotSettings\\" # Settings working directory

# Load data from json file
try:
    with open(swd+'data.json') as f:
        data = json.load(f)
        BOT_TOKEN = data['bot_token']
        ADMINS = data['admins']
        PREFIX = data['prefix']
        f.close()
except Exception as e:
    print("Error, probably no data.json found: " + str(e))
# end try except

# Setup bots
bot = commands.Bot(command_prefix=PREFIX, description="A dice-rolling bot for D&D games.", case_insensitive=True, owner_id=170779579693137920)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help"))
    print(f"Ready as {bot.user} on Discord")

@bot.command(aliases=['roll'])
async def r(ctx, *args):
    print(f"Msg: {args}")
    await ctx.send("Test?")
# end command - r/roll

# @bot.listen('on_message')
# async def whatever_you_want_to_call_it(ctx):
#     print(ctx)
# end on_message

@bot.event
async def on_command_error(ctx, exception):
    print(ctx)
    print(exception)
    if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
        print("Command not found error")

# Shut down bot
@bot.command(aliases=['quit', 'stop'])
@commands.is_owner()
async def exit(ctx):
    print(f"[{ctx.message.author}] Shutting down...")
    await ctx.message.add_reaction("👋")
    await bot.logout()
# end command - quit

print("Starting up...")
bot.run(BOT_TOKEN)
