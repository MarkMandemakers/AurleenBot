import discord
import json
import re
import time
from datetime import datetime
from matplotlib import pyplot as plt
from numpy import random as np
import os
import sys
import math
# import git

# DEBUG
print("Starting up...") # STarting

# Setup global variables
client = discord.Client()
nat20_img = "https://i.imgur.com/5wigsBM.png" # color; blank: https://i.imgur.com/vRMbnn9.png
nat1_img = "https://i.imgur.com/jfV3bEg.png" # color; blank: https://i.imgur.com/zB9gKje.png
rolled = 0
prev_call = ""
d20_stats = [0] * 20
d20_rolled = 0
current_servers = []
field_limit = 21 
total_dice_limit = 100
cwd = os.getcwd() + "/"
swd = ""
initiative = {}
initiative_embed = ""
ADMINS = ""
BOT_TOKEN = ""
PREFIX = ""

# Load loc.json to find location of settings files
try:
    with open(cwd+'loc.json') as f:
        loc = json.load(f)
        swd = loc['swd']
        if swd[-1] != "/": swd += "/"
        f.close()
except Exception as e:
    # If not found, attempt to look in cwd for data.json
    print(f"Error, likely no loc.json found: {e}")
    print("Looking for data.json in AurleenBot working directory")
# end try except

# Load data from json file
data_folder = cwd if swd == "" else swd
try:
    with open(data_folder+'data.json') as f:
        data = json.load(f)
        BOT_TOKEN = data['bot_token']
        ADMINS = data['admins']
        PREFIX = data['prefix']
        f.close()
except Exception as e:
    print(f"Error, probably no data.json found: {e}")
    sys.exit()
# end try except

# Load Discord settings from json file
if os.path.isfile(f"{data_folder}discord.json"):
    try:
        with open(swd+'discord.json') as f2:
            discord_data = json.load(f2)
            f2.close()
    except Exception as e:
        print(f"Error, probably no discord.json found: {e}")
    # end try except
else:
    # If discord.json doesn't exist, create the file
    try:
        fp = open(f"{data_folder}discord.json", "x")
        discord_data = {}
        fp.close()
    except Exception as e:
        print(f"Cannot create discord.json: {e}")
    # end try except
# end if

# Update Discord.json data
def update_discord():
    # Update server name
    for g in client.guilds:
        discord_data[str(g.id)]['name'] = g.name
    # end for

    try:
        with open(swd+"discord.json", 'w') as fp:
            json.dump(discord_data, fp, indent=2)
            fp.close()
            print("Updated discord.json")
        # end with
    except Exception as e:
        print("Error, probably no discord.json found: " + str(e))
    # end try/except
# end def


# Dice rolling function
def roll(d, n=1):
    global rolled
    rolled += n
    return np.randint(low=1, high=d+1, size=n)
# end def


# Print statistics to console
def print_stats():
    global d20_stats
    global d20_rolled
    print("Rolled " + str(d20_rolled) + "x; " + str(d20_stats))
# end def


# Generate statistics image
def gen_stats_img(save=False):
    global d20_stats
    global d20_rolled

    x = range(1, 21)
    plt.clf()
    plt.bar(x, d20_stats)
    plt.hlines(d20_rolled/20, 0.5, 20.5, linestyles='dashed')
    plt.xticks(x)
    plt.xlabel("d20 Value")
    plt.ylabel("Frequency")
    plt.title("Distribution after " + str(d20_rolled) + " d20 rolls")
    plt.xlim(0.5, len(x) + .5)
    plt.savefig("stats.png")
    # plt.show()

    if save:
        plt.savefig(f"{swd}stats/{str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}.png")
    # end if
# end def


# Unify dice from same type
def unify_dice(dtype, count):
    # Setup variables
    new_type = []
    new_count = []

    for i in range(len(dtype)):
        if dtype[i] not in new_type:
            # If the dice is not in the new array already, just add it
            new_type.append(dtype[i])
            new_count.append(count[i])
        else:
            # If the dice was already in the new array, add the count of the two
            for j in range(len(new_type)):
                if new_type[j] == dtype[i]:
                    # Type is the same
                    new_count[j] += count[i]
                    break
            # end for
    # end for

    # Remove dice if the count is now zero
    for i in range(len(new_type)):
        if new_count[i] == 0:
            del new_type[i]
            del new_count[i]
        # end if
    # end for

    return [new_type, new_count]
# end def


# Add server to Discord.json
def add_server(g):
    if str(g.id) not in discord_data:
        discord_data[str(g.id)] = {}
        discord_data[str(g.id)]['name'] = g.name
        discord_data[str(g.id)]['admins'] = []
        discord_data[str(g.id)]['channels'] = []
        # discord_data[str(g.id)]['macros'] = {}
    # end if
    print(f"Added server {g} to data")
# end def


# Load JSON data
def load_json():
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
# end def


# When done setting up the bot user in Discord
@client.event
async def on_ready():
    # print(client.guilds)
    guild_list = []
    for g in client.guilds:
        guild_list.append(g.name)
        if str(g.id) not in discord_data:
            add_server(g)
        # end if
    # end for

    update_discord()

    print(f"Ready on Discord as {client.user}, watching {len(discord_data)} servers {guild_list}")
    # await client.change_presence(activity=discord.Game(name='Ready to roll!'))

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{PREFIX}help"))
    # await client.change_presence(activity=discord.Game(name=version_info)) # Set status to version nr
    # await client.change_presence(activity=discord.Game(name='Don\'t mind me, just testing the bot!'))
    # print_stats()
# end def


# When the bot joins a new server
@client.event
async def on_guild_join(guild):
    print(f"Joined new server: {guild} (id {guild.id})")
    if guild.id not in discord_data:
        add_server(guild)
    # end if
    update_discord()
# end def


# When a message is received
@client.event
async def on_message(message):
    start = time.time()
    # Setup variables
    global rolled
    global prev_call
    global d20_stats
    global d20_rolled
    global ADMINS
    global PREFIX
    msg = ""
    add_msg = ""
    title_preset = ""
    warning = ""

    # print()

    # Ignore messages from the bot itself or ones that are no commands
    if message.author == client.user or not message.content.startswith(PREFIX):
        return
    # end if

    # DEBUG
    # if message.content.startswith("!debug"):
    # await message.channel.send(message.author.name + message.author.display_name)
    # end if

    # If a command is called, convert message and proceed
    if message.content.startswith(PREFIX):
        # Convert message to lowercase and remove spaces and prefix for easier processing
        msg = message.content.lower()
        msg = msg.replace(" ", "")
        msg_with_prefix = str(msg)
        msg = msg.replace(PREFIX, "")
        # print(f"{time.time() - start} sec")
    # end if

    ###########################################################################################################
    # ADMIN
    ###########################################################################################################
    # Let an admin shut down the bot
    if str(message.author) in ADMINS:
        if msg.startswith(("quit", "stop", "exit")):
            print("[" + str(message.author) + "] Shutting down...")
            if d20_rolled > 1:
                gen_stats_img(True)
            # end if
            update_discord()
            await client.change_presence(status=discord.Status.dnd, afk=True, activity=discord.Game(name='OFFLINE'))
            await message.add_reaction("👋")
            await client.close()
            time.sleep(1)
        # end if - Bot stop

        # Let an admin reset the bot
        if msg.startswith("reset"):
            print("[" + str(message.author) + "] Resetting...")
            if d20_rolled > 0:
                gen_stats_img(True)
            # end if
            rolled = 0
            d20_stats = [0] * 20
            d20_rolled = 0
            # print(d20_rolled)
            # print(d20_stats)
            print_stats()
            np.seed()

            # Load data from json file (same as reload command)
            load_json()
            print("Reloaded data.json")
            await message.add_reaction("🔄")
            # await message.add_reaction("👍")
            # await message.add_reaction("✅")
            return
        # end if - Bot reset

        # Set channel to watch
        if msg.startswith("watch"):
            if isinstance(message.channel, discord.channel.DMChannel):
                await message.channel.send(f"Cannot watch a Direct Message Channel...")
            # end if

            if message.channel.id in discord_data[str(message.guild.id)]['channels']:
                await message.channel.send(f"Already watching this channel. \nType **{PREFIX}unwatch** to disable")
                # await message.add_reaction(":eyes:")
            else:
                discord_data[str(message.guild.id)]['channels'].append(message.channel.id)
                await message.channel.send(f"Now watching this channel. :eyes:\nType **{PREFIX}unwatch** to disable")
                print(f"Now watching channel \"{message.channel}\" in \"{message.guild}\"")
            # end if/else
            update_discord()
            return
        # end if - watch channel

        # Disable channel to watch
        if msg.startswith("unwatch"):
            if isinstance(message.channel, discord.channel.DMChannel):
                await message.channel.send(f"Cannot watch a Direct Message Channel...")
            # end if

            if message.channel.id in discord_data[str(message.guild.id)]['channels']:
                discord_data[str(message.guild.id)]['channels'].remove(message.channel.id)
                await message.channel.send(f"Stopped watching this channel. \nType **{PREFIX}watch** to enable again")
                # await message.add_reaction(":eyes:")
                print(f"Stopped watching channel \"{message.channel}\" in \"{message.guild}\"")
            else:
                discord_data[str(message.guild.id)]['channels'].append(message.channel.id)
                await message.channel.send(f"Channel is not being watched. \nType **{PREFIX}watch** to enable")
            # end if/else
            update_discord()
            return
        # end if - unwatch channel
    elif msg.startswith(("quit", "stop", "exit", "reset", "watch", "unwatch")):
        await message.channel.send(f"{str(message.author.mention)} Sorry, but you are not an admin...")
    # end if - ADMIN COMMANDS

    ###########################################################################################################
    # BOT INFORMATION
    ###########################################################################################################
    if msg.startswith(("help", "aurleen")):
        embed = discord.Embed(title="AurleenBot Sample Commands", color=0x76883c)
        embed.add_field(name=f"{PREFIX}r1d20", value="Roll a d20", inline=False)
        embed.add_field(name=f"{PREFIX}r5d6", value=f"Roll five d6 and sum up\n(__Note__ Up to {total_dice_limit} dice can be rolled at once)", inline=False)
        embed.add_field(name=f"{PREFIX}advantage ({PREFIX}adv) / {PREFIX}disadvantage ({PREFIX}dis)",
                        value="Roll two d20 and keep the highest or lowest respectively", inline=False)
        embed.add_field(name=f"{PREFIX}reroll / {PREFIX}re-roll", value="Re-Roll the previous roll command\n(__Note__ I re-roll the last call to me from anyone, not just from you)\n\u200b\n", inline=False)

        embed.add_field(name=f"Presets:", value="\u200b", inline=False)
        embed.add_field(name=f"{PREFIX}bless / {PREFIX}guidance", value="Roll a d20 and add a d4", inline=False)
        embed.add_field(name=f"{PREFIX}bane", value="Roll a d20 and subtract a d4\n\u200b\n", inline=False)

        embed.add_field(name=f"Additions for any command:", value="\u200b", inline=False)
        embed.add_field(name=f"Dice Modifiers, e.g. {PREFIX}r1d20+1d4",
                        value="Add + or - your modifier dice to add it to the total of the roll", inline=False)
        embed.add_field(name=f"Value Modifiers, e.g. {PREFIX}r1d20+5 or {PREFIX}r1d20+1d4-2",
                        value="Add + or - your modifier to add it to the total of the roll", inline=False)
        embed.add_field(name=f"Roll Checks, e.g. {PREFIX}r1d00<=7", value="Supported checks: *>, >=, =, ==, <, <=*", inline=False)
        embed.add_field(name="Private Rolls:",
                        value=f"- Add *dm* or *h* to your command to get the result via DM,\ne.g. {PREFIX}dm1d20 or {PREFIX}hadv+6\n- You can also just DM me on Discord", inline=False)
        embed.set_footer(text="pls don't break me")
        await message.channel.send(embed=embed)
        print("[" + str(message.author) + "] Showed info")
        # prev_call = ""
        return
    # end if - bot information

    # PING (BOT STATUS)
    if msg.startswith("ping"):
        await message.channel.send(f"Pong!")
        print(f"Latency: {client.latency}")
        return
    # end if - ping

    # RELOAD DATA FILES
    if msg.startswith("reload"):
        # Load data from json file
        load_json()
        await message.add_reaction("🔄")
        print("Reloaded data.json")
        return
    # end if - ping

    # D20 STATISTICS
    if str(message.author) in ADMINS and msg.startswith("stat"):
        if d20_rolled > 0:
            print("[" + str(message.author) + "] Displaying stats")
            # Print to console
            print_stats()

            # Generate image
            gen_stats_img()

            # Send image to Discord
            await message.channel.send(file=discord.File('stats.png'))
            return
        else:
            print("[" + str(message.author) + "] No stats yet")
            await message.channel.send(str(message.author.mention) +
                                       " There are no statistics about d20 rolls to show yet...")
            # Do not proceed with message processing
            return
        # end if/else
    # end if - d20 statistics



    ###########################################################################################################
    # RE-ROLLING
    ###########################################################################################################
    if msg.startswith(("reroll", "re-roll")) and (isinstance(message.channel, discord.channel.DMChannel) or message.channel.id in discord_data[str(message.guild.id)]['channels'] or len(discord_data[str(message.guild.id)]['channels']) == 0):
        if prev_call == "":
            # Throw error since there is nothing to re-roll
            print("[" + str(message.content) + "; " + str(message.author) + "] Nothing to re-roll")
            await message.channel.send(str(message.author.mention) +
                                       " There is nothing to re-roll...")
            # Do not proceed with message processing
            return
        else:
            # Execute as normal
            msg = prev_call
            title_preset = "Re-"
        # end if/else
    # end if - re-rolling


    ###########################################################################################################
    # HIDDEN / DM ROLLS
    ###########################################################################################################
    dm_roll = False
    if msg.startswith(("dm", "h")):
        # Replace whole command up until first integer (expected: dice count) or +/- with "regular roll"
        cmd_split_index = re.search('[\+\-\d]', msg)
        if "dis" in msg: 
            msg = msg.replace(msg[:cmd_split_index.start()], "dis")
        elif "adv" in msg:
            msg = msg.replace(msg[:cmd_split_index.start()], "adv")
        else:
            msg = msg.replace(msg[:cmd_split_index.start()], "r")
        # end if

        dm_roll = True
        # Proceed regular command handling
    # end if - Hidden/DM Rolls


    ###########################################################################################################
    # CHECK ROLL
    ###########################################################################################################
    # Check if rolls is equal, greater or less than value
    check_roll = []
    if '>=' in msg:
        check_roll = ['>=', int(msg.split('>=')[1])]
    elif '>' in msg:
        check_roll = ['>', int(msg.split('>')[1])]
    elif '<=' in msg:
        check_roll = ['<=', int(msg.split('<=')[1])]
    elif '<' in msg:
        check_roll = ['<', int(msg.split('<')[1])]
    elif '==' in msg:
        check_roll = ['==', int(msg.split('==')[1])]
    elif '=' in msg:
        check_roll = ['==', int(msg.split('=')[1])]
    # end if


    ###########################################################################################################
    # ROLLING WITH ADVANTAGE / DISADVANTAGE
    ###########################################################################################################    
    if msg.startswith(("adv", "dis")) and (isinstance(message.channel, discord.channel.DMChannel) or message.channel.id in discord_data[str(message.guild.id)]['channels'] or len(discord_data[str(message.guild.id)]['channels']) == 0):
        prev_call = msg
        # Find additional modifier (dice or not)
        modifier_dice = re.findall('[\+\-]r*\d*d\d+', msg)
        modifier = re.findall('[\+\-]\d+(?![d\d])', msg)

        # Check if we should roll with advantage or disadvantage
        disadvantage = ("dis" in msg)

        # If the format is correct, proceed with message processing
        # Setup variables and get total dice count
        total_dice_count = 2  # Start at two due to (dis)advantage

        # Setup variables for dice and modifier
        dice_count = []
        dice_type = []
        modifier_total = 0

        # Go through all modifier dice and find type/count
        for dice in modifier_dice:
            dice_split = dice.replace("+", "").replace("r", "").split("d")
            dice_type.append(int(dice_split[1]))
            dice_count.append(int(dice_split[0]))
        # end for

        # Cleanup
        del modifier_dice

        [dice_type, dice_count] = unify_dice(dice_type, dice_count)
        for c in dice_count:
            total_dice_count += abs(int(c))
        # end for

        # Find total modifier (without dice)
        for mod in modifier:
            modifier_total += int(mod)
        # end for

        # Cleanup
        del modifier

        # Check if dice limit is reached or no dice are left after unifying
        if total_dice_count == 0:
            print("[" + str(message.content) + "; " + str(message.author) + "] No dice left after unifying")
            await message.channel.send(str(message.author.mention) +
                                       " This doesn\'t add up with the number of dice you want to roll.\n"
                                       f"Please use **{PREFIX}help** to see what formats are supported.")
            # Do not proceed with message processing
            return
        elif total_dice_count > total_dice_limit:
            # Throw error
            print("[" + str(message.content) + "; " + str(message.author) + "] Too many dice to roll, throwing error")
            await message.channel.send(f"{message.author.mention} Sorry, I cannot roll that many dice at once.\nPlease try to roll {total_dice_limit} dice or less.")
            # Do not proceed with message processing
            return
        # end if/elif

        # Create roll description
        desc = "2d20 (at "
        if disadvantage:
            desc += "dis"
        # end if
        desc += "advantage)"

        for i in range(0, len(dice_type)):
            if int(dice_count[i]) < 0:
                desc += str(dice_count[i]).replace("-", " - ") + "d" + str(dice_type[i])
            else:
                desc += " + " + str(dice_count[i]) + "d" + str(dice_type[i])
            # end if/else
        # end for
        if int(modifier_total) < 0:
            desc += str(modifier_total).replace("-", " - ")
        elif int(modifier_total) > 0:
            desc += " + " + str(modifier_total)
        # end if/elif

        # Add to description if we are checking a roll
        if len(check_roll) > 0:
            desc += f" {check_roll[0]} {check_roll[1]}"
        # end if

        # Setup embedding for dice roll response
        embed = discord.Embed(title=title_preset + "Rolling for " + str(message.author.display_name), description=desc,
                              color=0x76883c)
        footer = ""
        total_result = 0
        max_possible = 20
        min_possible = 0
        nr_of_embeds = 1

        # Split into more embeds if rolling more than embed limit dice, less than hard limit
        # Add one to dice count because of empty cell in advantage row
        if field_limit < total_dice_count + 1 <= total_dice_limit:
            added_embeds = []
            nr_of_embeds = math.ceil((total_dice_count + 1) / field_limit)
            embed.title += f" (1/{nr_of_embeds})"
            for i in range(nr_of_embeds-1):
                added_embeds.append(discord.Embed(title=f"{title_preset}Rolling for {message.author.display_name} ({i+2}/{nr_of_embeds})", description="\u200b", color=0x76883c))
            # end for
        # end

        # Keep track of nr of field added to embed
        fields = 0
        embed_count = -1

        # Roll base dice at (dis)advantage
        d20s = roll(20, 2)
        if disadvantage:
            total_result = min(d20s)
            if total_result == 20:
                footer = "NATURAL 20"
                embed.set_thumbnail(url=nat20_img)
            elif total_result == 1:
                footer = "NATURAL 1"
                embed.set_thumbnail(url=nat1_img)
            # end if/elif
        else:
            total_result = max(d20s)
            if total_result == 20:
                footer = "NATURAL 20"
                embed.set_thumbnail(url=nat20_img)
            elif total_result == 1:
                footer = "NATURAL 1"
                embed.set_thumbnail(url=nat1_img)
            # end if/elif
        # end if/else

        # Store statistics
        d20_rolled += 2
        d20_stats[d20s[0] - 1] += 1
        d20_stats[d20s[1] - 1] += 1
        min_possible += 1

        # Highlight the selected result
        if d20s[0] == total_result:
            embed.add_field(name="d20 #1", value="**" + str(d20s[0]) + "**", inline=True)
            fields += 1
        else:
            embed.add_field(name="d20 #1", value=str(d20s[0]), inline=True)
            fields += 1
        # end if/else
        if d20s[1] == total_result:
            embed.add_field(name="d20 #2", value="**" + str(d20s[1]) + "**", inline=True)
            fields += 1
        else:
            embed.add_field(name="d20 #2", value=str(d20s[1]), inline=True)
            fields += 1
        # end if/else
        # Add empty field to fill out the row
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        fields += 1

        # Any other dice rolling
        for i in range(0, len(dice_type)):
            # Roll all dice of this type at once
            results = roll(dice_type[i], abs(dice_count[i]))

            for result in results:
                # Go through all results
                if fields == field_limit:
                    embed_count += 1
                    fields = 0
                # end if

                if dice_count[i] < 0:
                    # Negative dice modifier
                    if result == dice_type[i] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[i]), value=f"*-{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[i]), value=f"*-{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[i]), value=f"-{str(result)}", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[i]), value=f"-{str(result)}", inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[i]
                else:
                    # Positive dice modifier
                    if result == dice_type[i] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[i]), value=f"*{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[i]), value=f"*{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[i]), value=result, inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[i]), value=result, inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result += result
                    max_possible += dice_type[i]
                    min_possible += 1
                # end if/else

                # Add d20 statistics
                if dice_type[i] == 20:
                    d20_rolled += 1
                    d20_stats[result - 1] += 1
                # end if
            # end for
        # end for

        # Add modifier to calculate total
        if modifier_total != 0:
            if nr_of_embeds > 1:
                # add to last embed
                if modifier_total > 0:
                    added_embeds[-1].add_field(name="Modifier", value=f"+{modifier_total}", inline=True)
                else:
                    added_embeds[-1].add_field(name="Modifier", value=modifier_total, inline=True)
                # end if
            else:
                if modifier_total > 0:
                    embed.add_field(name="Modifier", value=f"+{modifier_total}", inline=True)
                else:
                    embed.add_field(name="Modifier", value=modifier_total, inline=True)
                # end if
            # end if
        # end if

        total_result += modifier_total
        max_possible += modifier_total
        min_possible += modifier_total

        # Add total to embedding, handle check if needed
        if len(check_roll) > 0:
            if eval(f"{total_result}{check_roll[0]}{check_roll[1]}"):
                # embed.add_field(name="Total", value=f"{total_result} (Success)", inline=False)
                if footer == "":
                    footer += "SUCCESS"
                else:
                    footer += "\nSUCCESS"
                # end if
            else:
                # embed.add_field(name="Total", value=f"{total_result} (Fail)", inline=False)
                if footer == "":
                    footer += "FAIL"
                else:
                    footer += "\nFAIL"
                # end if
            # end if
        # end if
        if nr_of_embeds > 1:
            # add to last embed
            added_embeds[-1].add_field(name="Total", value=total_result, inline=False)
        else:
            embed.add_field(name="Total", value=total_result, inline=False)
        # end if

        # Add stats of roll
        if footer == "":
            # Footer is empty (so no nat. 1 or 20)
            if nr_of_embeds > 1:
                added_embeds[-1].set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " + str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            else:
                embed.set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " + str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            # end if
        else:
            footer += ("\nmin. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " +
                        str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            embed.set_footer(text=footer)
            
            if nr_of_embeds > 1:
                added_embeds[-1].set_footer(text=footer)
            else:
                embed.set_footer(text=footer)
            # end if
        # end if/else
        
        # Send message to Discord or DM and update status
        if nr_of_embeds > 1:
            if dm_roll:
                # Adjust title to see it in notification
                embed.title = f"Rolling {desc}: {total_result}"
                embed.description = ""
                # Send DM
                await message.author.send(warning, embed=embed)

                # Send other embeds
                for e in added_embeds:
                    e.title = f"Rolling {desc}: {total_result}"
                    await message.author.send(warning, embed=e)
                # end for

                await message.add_reaction("🎲")
            else:
                # Send to server
                await message.channel.send(warning, embed=embed)

                # Send other embeds
                for e in added_embeds:
                    await message.channel.send(warning, embed=e)
                # end for
            # end if
        else:
            if dm_roll:
                # Adjust title to see it in notification
                embed.title = f"Rolling {desc}: {total_result}"
                embed.description = ""
                # Send DM
                await message.author.send(warning, embed=embed)
                await message.add_reaction("🎲")
            else:
                # Send to server
                await message.channel.send(warning, embed=embed)
            # end if
        # end if
        # await client.change_presence(activity=discord.Game(name="Rolled " + str(rolled) + " dice"))
        # print(str(time.time() - start) + "sec")
        return
    # end if - advantage / disadvantage

    ###########################################################################################################
    # PRESETS
    ###########################################################################################################

    # Quick-roll a d20 using !roll
    if msg.startswith("roll"):
        # Convert to regular d20
        msg = msg.replace("roll", "r1d20")
        
        prev_call = msg
    # end if - quick-roll d20

    # Custom presets for 1d20 + 1d4
    if msg.startswith("bless"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("bless", "r1d20+1d4")
        add_msg = "*Bless: +1d4*"
        prev_call = msg
    # end if - bless preset

    if msg.startswith("guidance"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("guidance", "r1d20+1d4")
        add_msg = "*Guidance: +1d4*"
        prev_call = msg
    # end if - guidance preset

    if msg.startswith("bane"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("bane", "r1d20-1d4")
        add_msg = "*Bane: -1d4*"
        prev_call = msg
    # end if - guidance preset

    # Handle slight errors in command (e.g. !rd20, !d20)
    if msg_with_prefix.startswith((f"{PREFIX}rd", f"{PREFIX}d")):
        # Is a dice mentioned in there?
        format_dice = re.findall(f'\{PREFIX}r*\d*d\d+', msg_with_prefix)
        if len(format_dice) > 0:
            # Fix the command
            msg_with_prefix = msg_with_prefix.replace(f"{PREFIX}rd", f"{PREFIX}r1d")
            msg_with_prefix = msg_with_prefix.replace(f"{PREFIX}d", f"{PREFIX}r1d")
            msg = msg_with_prefix.replace(PREFIX, "")

            # Print warning to console and prepare to add to embedding
            print("[" + str(message.content) + "; " + str(message.author) + "] Incorrect command format")
            if warning == "":
                warning = message.author.mention + " You did not use the correct format for rolling, " \
                                                   "but I assume you meant `" + str(msg) + "`. " \
                                                   f"\nUse **{PREFIX}help** to see what formats are supported."
            else:
                warning += "\nYou did not use the correct format for rolling, " \
                           "but I assume you meant `" + str(msg) + "`. " \
                           f"\nUse **{PREFIX}help** to see what formats are supported."
            # end if/else
        # end if
        # Continue using fixed command
    # end if - slight errors in command

    # Handle other slight error in command (e.g. !1d20)
    error_regex = re.findall(f'\{PREFIX}\d+d\d+', msg_with_prefix)
    if len(error_regex) > 0:
        # Fix the command
        msg_with_prefix = msg_with_prefix.replace(PREFIX, f"{PREFIX}r")
        msg = msg_with_prefix.replace(PREFIX, "")

        # Print warning to console and prepare to add to embedding
        print("[" + str(message.content) + "; " + str(message.author) + "] Incorrect command format")
        if warning == "":
            warning = message.author.mention + " You did not use the correct format for rolling, " \
                                               "but I assume you meant `" + str(msg) + "`. " \
                                               f"\nUse **{PREFIX}help** to see what formats are supported."
        else:
            warning += "\nYou did not use the correct format for rolling, " \
                       "but I assume you meant `" + str(msg) + "`. " \
                       f"\nUse **{PREFIX}help** to see what formats are supported."
        # end if/else
        # Continue using fixed command
    # end if - Handle other slight error in command (e.g. !1d20)
    

    ###########################################################################################################
    # REGULAR DICE ROLLS
    ###########################################################################################################
    # # Send a DM with roll result instead of in server
    # dm_roll = False
    # if msg.startswith(("dm", "h")) and (message.channel.id in discord_data[str(message.guild.id)]['channels'] or len(discord_data[str(message.guild.id)]['channels']) == 0):
    #     # Replace whole command up until first integer (expected: dice count) with "regular roll"
    #     cmd_split_index = re.search('\d', msg)
    #     msg = msg.replace(msg[:cmd_split_index.start()], "r")

    #     dm_roll = True
    #     # Proceed regular command handling
    # # end if - Regular DM Roll


    if msg.startswith("r") and (isinstance(message.channel, discord.channel.DMChannel) or message.channel.id in discord_data[str(message.guild.id)]['channels'] or len(discord_data[str(message.guild.id)]['channels']) == 0):
        # Regex search on message to see what the command is asking for
        # !r(\d+d\d+)       !r1d20 (base dice)
        # !(r*)d\d+         base dice (incorrect command, i.e. !rd20, !d20
        # \+\d*d\d+         positive modifier (only dice)
        # \-\d*d\d+         negative modifier (only dice)
        # \+\d+[^d]         positive modifier (no dice)
        # \-\d+[^d]         negative modifier (no dice)

        base_dice = re.findall(f'r(\d+d\d+)', msg)
        modifier_dice = re.findall('[\+\-]r*\d*d\d+', msg)
        modifier = re.findall('[\+\-]\d+(?![d\d])', msg)

        # print(f"msg: {msg}\nbase dice: {base_dice}\nmodifier dice: {modifier_dice}\nmodifier: {modifier}")

        # Check command format
        if len(base_dice) != 1:
            # No base dice found (or too many), return error message
            print("[" + str(message.content) + "; " + str(message.author) + "] Not correct number of base dice")
            await message.channel.send(str(message.author.mention) + " Something seems to be off with that command.\n"
                                                                     f"Please use **{PREFIX}help** to see what formats are supported.")
            # Do not proceed with message processing
            return
        # end if

        # If the format is correct, proceed with message processing
        # Setup variables and get total dice count
        total_dice_count = 0
        base_dice_split = base_dice[0].split("d")
        base_dice_count = int(base_dice_split[0])
        # total_dice_count += base_dice_count
        base_dice_type = int(base_dice_split[1])

        # Setup variables for dice and modifier
        dice_count = []
        dice_type = []
        modifier_total = 0

        # Add base dice to dice arrays
        dice_type.append(base_dice_type)
        dice_count.append(base_dice_count)

        # Some cleanup
        del base_dice
        del base_dice_count
        del base_dice_type
        del base_dice_split

        # Go through all modifier dice and find type/count
        for dice in modifier_dice:
            dice_split = dice.replace("+", "").replace("r", "").split("d")
            dice_type.append(int(dice_split[1]))
            dice_count.append(int(dice_split[0]))
        # end for

        # Cleanup
        del modifier_dice

        [dice_type, dice_count] = unify_dice(dice_type, dice_count)
        for c in dice_count:
            total_dice_count += abs(int(c))
        # end for

        # Find total modifier (without dice)
        for mod in modifier:
            modifier_total += int(mod)
        # end for

        # Cleanup
        del modifier

        # Check if dice limit is reached or no dice are left after unifying
        if total_dice_count == 0:
            print("[" + str(message.content) + "; " + str(message.author) + "] No dice left after unifying")
            await message.channel.send(str(message.author.mention) +
                                       " This doesn\'t add up with the number of dice you want to roll.\n"
                                       f"Please use **{PREFIX}help** to see what formats are supported.")
            # Do not proceed with message processing
            return
        elif total_dice_count > total_dice_limit:
            # Throw error
            print("[" + str(message.content) + "; " + str(message.author) + "] Too many dice to roll, throwing error")
            await message.channel.send(f"{message.author.mention} Sorry, I cannot roll that many dice at once.\nPlease try to roll {total_dice_limit} dice or less.")
            # Do not proceed with message processing
            return
        # end if/elif

        # Create roll description
        desc = add_msg + "\n" if add_msg != "" else ""
        desc += str(dice_count[0]) + "d" + str(dice_type[0])
        for i in range(1, len(dice_type)):
            if int(dice_count[i]) < 0:
                desc += str(dice_count[i]).replace("-", " - ") + "d" + str(dice_type[i])
            else:
                desc += " + " + str(dice_count[i]) + "d" + str(dice_type[i])
            # end if/else
        # end for
        if int(modifier_total) < 0:
            desc += str(modifier_total).replace("-", " - ")
        elif int(modifier_total) > 0:
            desc += " + " + str(modifier_total)
        # end if/elif

        # Add to description if we are checking a roll
        if len(check_roll) > 0:
            desc += f" {check_roll[0]} {check_roll[1]}"
        # end if

        # Setup embedding for dice roll response
        embed = discord.Embed(title=f"{title_preset}Rolling for {message.author.display_name}", description=desc, color=0x76883c)
        footer = ""
        total_result = 0
        max_possible = 0
        min_possible = 0
        nr_of_embeds = 1

        # Split into more embeds if rolling more than embed limit dice, less than hard limit
        if field_limit < total_dice_count <= total_dice_limit:
            added_embeds = []
            nr_of_embeds = math.ceil(total_dice_count / field_limit)
            embed.title += f" (1/{nr_of_embeds})"
            for i in range(nr_of_embeds-1):
                added_embeds.append(discord.Embed(title=f"{title_preset}Rolling for {message.author.display_name} ({i+2}/{nr_of_embeds})", description="\u200b", color=0x76883c))
            # end for
        # end

        # Keep track of nr of field added to embed
        fields = 0
        embed_count = -1

        # Roll base dice
        if dice_type[0] == 20 and dice_count[0] == 1:
            # Start with 1d20, natural 1 or natural 20 can occur
            result = roll(20)[0]
            embed.add_field(name="d20", value=result, inline=True)
            fields += 1

            if result == 20:
                footer = "NATURAL 20"
                embed.set_thumbnail(url=nat20_img)
            elif result == 1:
                footer = "NATURAL 1"
                embed.set_thumbnail(url=nat1_img)
            # end if/elif

            # Add d20 statistics
            d20_rolled += 1
            d20_stats[result - 1] += 1

            total_result += result
            max_possible += 20
            min_possible += 1
        else:
            # Roll all dice of base type at once
            results = roll(dice_type[0], abs(dice_count[0]))

            for result in results:
                # Go through all results
                if fields == field_limit:
                    embed_count += 1
                    fields = 0
                # end if

                if dice_count[0] < 0:
                    # Negative base dice count
                    if result == dice_type[0] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[0]), value=f"*-{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[0]), value=f"*-{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[0]), value=f"-{str(result)}", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[0]), value=f"-{str(result)}", inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[0]
                else:
                    # Positive base dice count
                    if result == dice_type[0] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[0]), value=f"*{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[0]), value=f"*{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[0]), value=result, inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[0]), value=result, inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result += result
                    max_possible += dice_type[0]
                    min_possible += 1
                # end if/else

                # Add d20 statistics
                if dice_type[0] == 20:
                    d20_rolled += 1
                    d20_stats[result - 1] += 1
                # end if
            # end for
        # end if/else

        # Any other dice rolling
        for i in range(1, len(dice_type)):
            # Roll all dice of this type at once
            results = roll(dice_type[i], abs(dice_count[i]))

            for result in results:
                # Go through all results
                if fields == field_limit:
                    embed_count += 1
                    fields = 0
                # end if

                if dice_count[i] < 0:
                    # Negative dice modifier
                    if result == dice_type[i] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[i]), value=f"*-{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[i]), value=f"*-{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="-d" + str(dice_type[i]), value=f"-{str(result)}", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="-d" + str(dice_type[i]), value=f"-{str(result)}", inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[i]
                    print(min_possible)
                else:
                    # Positive dice modifier
                    if result == dice_type[i] or result == 1:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[i]), value=f"*{str(result)}*", inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[i]), value=f"*{str(result)}*", inline=True)
                        # end if
                        fields += 1
                    else:
                        if embed_count == -1:
                            embed.add_field(name="d" + str(dice_type[i]), value=result, inline=True)
                        else:
                            added_embeds[embed_count].add_field(name="d" + str(dice_type[i]), value=result, inline=True)
                        # end if
                        fields += 1
                    # end if

                    total_result += result
                    max_possible += dice_type[i]
                    min_possible += 1
                # end if/else

                # Add d20 statistics
                if dice_type[i] == 20:
                    d20_rolled += 1
                    d20_stats[result - 1] += 1
                # end if
            # end for
        # end for

        # Add modifier to calculate total
        if modifier_total != 0:
            if nr_of_embeds > 1:
                # add to last embed
                if modifier_total > 0:
                    added_embeds[-1].add_field(name="Modifier", value=f"+{modifier_total}", inline=True)
                else:
                    added_embeds[-1].add_field(name="Modifier", value=modifier_total, inline=True)
                # end if
            else:
                if modifier_total > 0:
                    embed.add_field(name="Modifier", value=f"+{modifier_total}", inline=True)
                else:
                    embed.add_field(name="Modifier", value=modifier_total, inline=True)
                # end if
            # end if
        # end if

        total_result += modifier_total
        max_possible += modifier_total
        min_possible += modifier_total

        # Add total to embedding, handle check if needed
        if len(check_roll) > 0:
            if eval(f"{total_result}{check_roll[0]}{check_roll[1]}"):
                # embed.add_field(name="Total", value=f"{total_result} (Success)", inline=False)
                if footer == "":
                    footer += "SUCCESS"
                else:
                    footer += "\nSUCCESS"
                # end if
            else:
                # embed.add_field(name="Total", value=f"{total_result} (Fail)", inline=False)
                if footer == "":
                    footer += "FAIL"
                else:
                    footer += "\nFAIL"
                # end if
            # end if
        # end if
        if nr_of_embeds > 1:
            # add to last embed
            added_embeds[-1].add_field(name="Total", value=total_result, inline=False)
        else:
            embed.add_field(name="Total", value=total_result, inline=False)
        # end if
        

        # Store message for re-rolling
        prev_call = msg

        # Add stats of roll
        if footer == "":
            # Footer is empty (so no nat. 1 or 20)
            if nr_of_embeds > 1:
                added_embeds[-1].set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " + str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            else:
                embed.set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " + str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            # end if
        else:
            footer += ("\nmin. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " + str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            
            if nr_of_embeds > 1:
                added_embeds[-1].set_footer(text=footer)
            else:
                embed.set_footer(text=footer)
            # end if
        # end if/else

        # Send message to Discord or DM and update status
        if nr_of_embeds > 1:
            if dm_roll:
                # Adjust title to see it in notification
                embed.title = f"Rolling {desc}: {total_result}"
                embed.description = ""
                # Send DM
                await message.author.send(warning, embed=embed)

                # Send other embeds
                for e in added_embeds:
                    e.title = f"Rolling {desc}: {total_result}"
                    await message.author.send(warning, embed=e)
                # end for

                await message.add_reaction("🎲")
            else:
                # Send to server
                await message.channel.send(warning, embed=embed)

                # Send other embeds
                for e in added_embeds:
                    await message.channel.send(warning, embed=e)
                # end for
            # end if
        else:
            if dm_roll:
                # Adjust title to see it in notification
                embed.title = f"Rolling {desc}: {total_result}"
                embed.description = ""
                # Send DM
                await message.author.send(warning, embed=embed)
                await message.add_reaction("🎲")
            else:
                # Send to server
                await message.channel.send(warning, embed=embed)
            # end if
        # end if
        # await client.change_presence(activity=discord.Game(name="Rolled " + str(rolled) + " dice"))
        print(str(time.time() - start) + "sec; now rolled " + str(rolled) + " dice")
        return
    # end if - Regular dice roll


# end def

client.run(BOT_TOKEN)
