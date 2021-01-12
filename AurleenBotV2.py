# Import modules
import discord
from discord.ext import commands
import os
import json
import re

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



# Process dice roll
def process_diceroll(msg, adv = False):
    # Setup variables
    d20 = False     # Contains a d20? Used for natural 20/1
    warning = ''    # Warning to add to result message (e.g. incorrect formatting)

    # Find dice and modifiers in command
    dice = re.findall('-*\d*d\d*', msg)
    modifiers = re.findall('[\+\-]\d+(?![d\d])', msg)
    print(dice)
    print(modifiers)

    # Split dice into types and counts
    dice_count = {}

    for d in dice:
        # Split int dice count and dice type
        dsplit = d.split('d')
        
        # Is there a d20 in the command?
        if int(dsplit[1]) == 20:
            d20 = True
        # end if

        if dsplit[1] in dice_count:
            # Add warning if no dice count was specified
            if dsplit[0] == '':
                print("[" + str(ctx.message.content) + "; " + str(ctx.message.author) + "] Incorrect command format")
                if warning == "":
                    warning = ctx.message.author.mention + " You did not use the correct format for rolling, " \
                                                    "but I assume you meant `" + str(msg) + "`. " \
                                                    f"\nUse **{PREFIX}help** to see what formats are supported."
                else:
                    warning += "\nYou did not use the correct format for rolling, " \
                            "but I assume you meant `" + str(msg) + "`. " \
                            f"\nUse **{PREFIX}help** to see what formats are supported."
                # end if/else

                dice_count[dsplit[1]] += 1
            else:
                dice_count[dsplit[1]] += int(dsplit[0])
            # end if/else
        else:
            if dsplit[0] == '':
                print("[" + str(ctx.message.content) + "; " + str(ctx.message.author) + "] Incorrect command format")
                if warning == "":
                    warning = ctx.message.author.mention + " You did not use the correct format for rolling, " \
                                                    "but I assume you meant `" + str(msg) + "`. " \
                                                    f"\nUse **{PREFIX}help** to see what formats are supported."
                else:
                    warning += "\nYou did not use the correct format for rolling, " \
                            "but I assume you meant `" + str(msg) + "`. " \
                            f"\nUse **{PREFIX}help** to see what formats are supported."
                # end if/else

                dice_count[dsplit[1]] = 1
            else:
                dice_count[dsplit[1]] = int(dsplit[0])
            # end if/else
        # end if/else  
    # end for - process dice

    # Process modifiers
    total_modifier = 0

    for m in modifiers:
        total_modifier += int(m)
    # end for - process modifiers

    # Roll dice
    ## TODO
# end def - process dice rolls


# Setup bots
bot = commands.Bot(command_prefix=PREFIX, description="A dice-rolling bot for D&D games.", case_insensitive=True, owner_id=170779579693137920)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help"))
    print(f"Ready as {bot.user} on Discord")
# end def - on_ready

@bot.event
async def on_command_error(ctx, exception):
    # Skip if error is not "command not found" OR command does not start with !r
    if not isinstance(exception, discord.ext.commands.errors.CommandNotFound):
        return
    # end if

    # Convert message for easier processing
    msg = ctx.message.content.lower()
    msg = msg.replace(" ", "")
    print(msg)

    # BLESS / GUIDANCE
    if msg.startswith(f"{PREFIX}bless") or msg.startswith(f"{PREFIX}guidance"):
        msg = msg.replace(f"{PREFIX}bless", f"{PREFIX}1d20+1d4")
        msg = msg.replace(f"{PREFIX}guidance", f"{PREFIX}1d20+1d4")
        process_diceroll(msg)
    # end if

    # BANE
    if msg.startswith(f"{PREFIX}bane"):
        msg = msg.replace(f"{PREFIX}bane", f"{PREFIX}1d20-1d4")
        process_diceroll(msg)
    # end if
    
    # REGULAR DICE ROLLS
    if msg.startswith(f"{PREFIX}r"):
        # Process the actual dice roll command
        process_diceroll(msg)
    # end if
# end def - on command error / rolling

# Shut down bot
@bot.command(aliases=['quit', 'stop'])
@commands.is_owner()
async def exit(ctx):
    print(f"[{ctx.message.author}] Shutting down...")
    await bot.change_presence(status=discord.Status.dnd, afk=True, activity=discord.Game(name='OFFLINE'))
    await ctx.message.add_reaction("👋")
    await bot.logout()
# end command - quit

print("Starting up...")
bot.run(BOT_TOKEN)