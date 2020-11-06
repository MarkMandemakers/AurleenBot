import discord
import json
import re
import time
from datetime import datetime
from matplotlib import pyplot as plt
from numpy import random as np
import os

# DEBUG
print("Starting up...")

# Setup global variables
client = discord.Client()
rolled = 0
roll_stats = True
prev_call = ""
d20_stats = [0] * 20
d20_rolled = 0
nat20_img = "https://i.imgur.com/5wigsBM.png" # color; blank: https://i.imgur.com/vRMbnn9.png
nat1_img = "https://i.imgur.com/jfV3bEg.png" # color; blank: https://i.imgur.com/zB9gKje.png
current_servers = []

# Load data from json file
try:
    with open('data.json') as f:
        data = json.load(f)
        BOT_TOKEN = data['bot_token']
        ADMINS = data['admins']
        f.close()
except Exception as e:
    print("Error, probably no data.json found: " + str(e))
# end try except

# Load Discord settings from json file
try:
    with open('discord.json') as f2:
        discord_data = json.load(f2)
        f2.close()
except Exception as e:
    print("Error, probably no discord.json found: " + str(e))
# end try except


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
        cdir = os.curdir
        plt.savefig(cdir + "/stats/" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".png")
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


# When done setting up the bot user in Discord
@client.event
async def on_ready():
    print(client.guilds)
    for g in client.guilds:
        current_servers.append(g.id)
    # end for

    print(f"Ready on Discord as {client.user}, watching {len(current_servers)} servers")
    await client.change_presence(activity=discord.Game(name='Ready to roll!'))
    # await client.change_presence(activity=discord.Game(name='Don\'t mind me, just testing the bot!'))
    # print_stats()
# end def


# When the bot joins a new server
@client.event
async def on_guild_join(guild):
    print(f"Joined new server: {guild} (id {guild.id})")
    if guild.id not in current_servers:
        current_servers.append(guild.id)
    # end if
# end def


# When a message is received
@client.event
async def on_message(message):
    start = time.time()
    # Setup variables
    global rolled
    global roll_stats
    global prev_call
    global d20_stats
    global d20_rolled
    msg = ""
    add_msg = ""
    title_preset = ""
    warning = ""

    print()

    # Ignore messages from the bot itself or ones that are no commands
    if message.author == client.user or not message.content.startswith("!"):
        return
    # end if

    # DEBUG
    # if message.content.startswith("!debug"):
    # await message.channel.send(message.author.name + message.author.display_name)
    # end if

    # If a command is called, convert message and proceed
    if message.content.startswith("!"):
        # Convert message to lowercase and remove spaces for easier processing
        msg = message.content.lower()
        msg = msg.replace(" ", "")
        print(f"{time.time() - start} sec")
    # end if

    ###########################################################################################################
    # ADMIN
    ###########################################################################################################
    # Let an admin shut down the bot
    if str(message.author) in ADMINS and msg.startswith(("!quit", "!stop", "!exit")):
        print("[" + str(message.author) + "] Shutting down...")
        if d20_rolled > 1:
            gen_stats_img(True)
        # end if
        await client.change_presence(status=discord.Status.dnd, afk=True, activity=discord.Game(name='OFFLINE'))
        await message.add_reaction("👋")
        await client.close()
    # end if - Bot stop

    # Let an admin reset the bot
    if str(message.author) in ADMINS and msg.startswith("!reset"):
        print("[" + str(message.author) + "] Resetting...")
        if d20_rolled > 0:
            gen_stats_img(True)
        # end if
        rolled = 0
        roll_stats = True
        d20_stats = [0] * 20
        d20_rolled = 0
        # print(d20_rolled)
        # print(d20_stats)
        print_stats()
        np.seed()
        # prev_call = ""
        await client.change_presence(activity=discord.Game(name='Ready to roll!'))
        await message.add_reaction("👍")
        # await message.add_reaction("✅")
        return
    # end if - Bot reset

    # Let admin toggle "out of" for rolls
    if str(message.author) in ADMINS and msg.startswith("!toggle"):
        roll_stats = not roll_stats
        # prev_call = ""
        if roll_stats:
            print("[" + str(message.author) + "] Turned roll statistics ON...")
            await message.add_reaction("✅")
        else:
            print("[" + str(message.author) + "] Turned roll statistics OFF...")
            await message.add_reaction("❎")
        # end if/else
        return
    # end if - toggle

    ###########################################################################################################
    # BOT INFORMATION
    ###########################################################################################################
    if msg.startswith(('!help', "!aurleenbot", "!aurleen")):
        embed = discord.Embed(title="AurleenBot Sample Commands", color=0x76883c)
        embed.add_field(name="!r1d20", value="Roll a d20", inline=False)
        embed.add_field(name="!r5d6", value="Roll five d6 and sum up", inline=False)
        embed.add_field(name="!advantage (!adv) / !disadvantage (!dis)",
                        value="Roll two d20 and keep the highest or lowest respectively", inline=False)
        embed.add_field(name="!bless / !guidance", value="Roll a d20 and a d4", inline=False)
        embed.add_field(name="!reroll / !re-roll", value="Re-Roll the previous roll command "
                                                         "\n(__Note__ I re-roll the last call to me from anyone, "
                                                         "not just from you)",
                        inline=False)
        embed.add_field(name="All commands support modifier dice, e.g. !r1d20+1d4",
                        value="Add + or - your modifier dice to add it to the total of the roll", inline=False)
        embed.add_field(name="All commands also support a modifier, e.g. !r1d20+5 or !r1d20+1d4-2",
                        value="Add + or - your modifier to add it to the total of the roll", inline=False)
        embed.add_field(name="Note: You can also roll privately",
                        value="Just DM me on Discord", inline=False)
        embed.set_footer(text="pls don't break me")
        await message.channel.send(embed=embed)
        print("[" + str(message.author) + "] Showed info")
        # prev_call = ""
        return
    # end if - bot information

    # D20 STATISTICS
    if str(message.author) in ADMINS and msg.startswith("!stat"):
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
    if msg.startswith(("!reroll", "!re-roll")):
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
    # ROLLING WITH ADVANTAGE/ DISADVANTAGE
    ###########################################################################################################
    if msg.startswith(("!adv", "!dis")):
        prev_call = msg
        # Find additional modifier (dice or not)
        modifier_dice = re.findall('[\+\-]\d*d\d+', msg)
        modifier = re.findall('[\+\-]\d+(?![d\d])', msg)

        # Check if we should roll with advantage or disadvantage
        disadvantage = ("!dis" in msg)

        # If the format is correct, proceed with message processing
        # Setup variables and get total dice count
        total_dice_count = 2  # Start at two due to (dis)advantage

        # Setup variables for dice and modifier
        dice_count = []
        dice_type = []
        modifier_total = 0

        # Go through all modifier dice and find type/count
        for dice in modifier_dice:
            dice_split = dice.replace("+", "").split("d")
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
                                       "Please use **!help** to see what formats are supported.")
            # Do not proceed with message processing
            return
        elif total_dice_count > 20:
            # if len(dice_type) == 1:
            #     # No modifier dice
            #     dice_count[0] = 20
            #     # Add message to description and print warning to console
            #     add_msg = "\n*(I can only roll up to 20 dice at once)*"
            #     print("[" + str(message.content) + "] Too many dice to roll, limiting base dice count to 20")
            # else:
            # There are modifier dice, now just throw error
            print("[" + str(message.content) + "; " + str(message.author) + "] Too many dice to roll, throwing error")
            await message.channel.send(
                str(message.author.mention) + " Sorry, I cannot roll that many dice at once.\n"
                                              "Please try to roll 20 dice or less.")
            # Do not proceed with message processing
            return
            # end if/else
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
        desc += add_msg

        # Setup embedding for dice roll response
        embed = discord.Embed(title=title_preset + "Rolling for " + str(message.author.name), description=desc,
                              color=0x76883c)
        footer = ""
        total_result = 0
        max_possible = 20
        min_possible = 0

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
        else:
            embed.add_field(name="d20 #1", value=str(d20s[0]), inline=True)
        # end if/else
        if d20s[1] == total_result:
            embed.add_field(name="d20 #2", value="**" + str(d20s[1]) + "**", inline=True)
        else:
            embed.add_field(name="d20 #2", value=str(d20s[1]), inline=True)
        # end if/else

        # Any other dice rolling
        for i in range(0, len(dice_type)):
            # Roll all dice of this type at once
            results = roll(dice_type[i], abs(dice_count[i]))

            for result in results:
                # Go through all results
                if dice_count[i] < 0:
                    # Negative dice modifier
                    embed.add_field(name="-d" + str(dice_type[i]), value="-" + str(result),
                                    inline=True)

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[i]
                else:
                    # Positive dice modifier
                    embed.add_field(name="d" + str(dice_type[i]), value=result, inline=True)

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
            embed.add_field(name="Modifier", value=modifier_total, inline=True)
        # end if

        total_result += modifier_total
        max_possible += modifier_total
        min_possible += modifier_total

        # Add total to embedding
        embed.add_field(name="Total", value=total_result, inline=False)

        # Add stats if wanted
        if roll_stats:
            if footer == "":
                # Footer is empty (so no nat. 1 or 20)
                embed.set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " +
                                      str(round(
                                          (total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            else:
                footer += ("\nmin. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " +
                           str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
                embed.set_footer(text=footer)
            # end if/else
        # end if

        # Send message to Discord and update status
        await message.channel.send(warning, embed=embed)
        # await client.change_presence(activity=discord.Game(name="Rolled " + str(rolled) + " dice"))
        print(str(time.time() - start) + "sec")
        return
    # end if - advantage / disadvantage

    ###########################################################################################################
    # PRESETS
    ###########################################################################################################

    # Quick-roll a d20 using !roll
    if msg == "!roll":
        # Convert to regular d20
        msg = "!r1d20"
        
        prev_call = msg
    # end if - quick-roll d20

    # Custom presets for 1d20 + 1d4
    if msg.startswith("!bless"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("!bless", "!r1d20+1d4")
        add_msg = "*Bless: +1d4*"
        prev_call = msg
    # end if - bless preset

    if msg.startswith("!guidance"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("!guidance", "!r1d20+1d4")
        add_msg = "*Guidance: +1d4*"
        prev_call = msg
    # end if - guidance preset

    if msg.startswith("!bane"):
        # Replace preset with corresponding dice, add comment and continue as normal
        msg = msg.replace("!bane", "!r1d20-1d4")
        add_msg = "*Bane: -1d4*"
        prev_call = msg
    # end if - guidance preset

    # Handle !roll as well as !r
    if msg.startswith("!roll"):
        msg = msg.replace("!roll", "!r")
    # end if - handle !roll

    # Handle slight errors in command (e.g. !rd20, !d20)
    if msg.startswith(("!rd", "!d")):
        # Is a dice mentioned in there?
        format_dice = re.findall('!r*\d*d\d+', msg)
        if len(format_dice) > 0:
            # Fix the command
            msg = msg.replace("!rd", "!r1d")
            msg = msg.replace("!d", "!r1d")

            # Print warning to console and prepare to add to embedding
            print("[" + str(message.content) + "; " + str(message.author) + "] Incorrect command format")
            if warning == "":
                warning = message.author.mention + " You did not use the correct format for rolling, " \
                                                   "but I assume you meant `" + str(msg) + "`. " \
                                                   "\nUse **!help** to see what formats are supported."
            else:
                warning += "\nYou did not use the correct format for rolling, " \
                           "but I assume you meant `" + str(msg) + "`. " \
                           "\nUse **!help** to see what formats are supported."
            # end if/else
        # end if
        # Continue using fixed command
    # end if - slight errors in command

    # Handle other slight error in command (e.g. !1d20)
    error_regex = re.findall('!\d+d\d+', msg)
    if len(error_regex) > 0:
        # Fix the command
        msg = msg.replace("!", "!r")
        error_regex[0].replace("!", "")
        error_split = error_regex[0].split("d")

        # Print warning to console and prepare to add to embedding
        print("[" + str(message.content) + "; " + str(message.author) + "] Incorrect command format")
        if warning == "":
            warning = message.author.mention + " You did not use the correct format for rolling, " \
                                               "but I assume you meant `" + str(msg) + "`. " \
                                               "\nUse **!help** to see what formats are supported."
        else:
            warning += "\nYou did not use the correct format for rolling, " \
                       "but I assume you meant `" + str(msg) + "`. " \
                       "\nUse **!help** to see what formats are supported."
        # end if/else
        # Continue using fixed command
    # end if - Handle other slight error in command (e.g. !1d20)

    ###########################################################################################################
    # REGULAR DICE ROLLS
    ###########################################################################################################
    if msg.startswith("!r"):
        # Regex search on message to see what the command is asking for
        # !r(\d+d\d+)       !r1d20 (base dice)
        # !(r*)d\d+         base dice (incorrect command, i.e. !rd20, !d20
        # \+\d*d\d+         positive modifier (only dice)
        # \-\d*d\d+         negative modifier (only dice)
        # \+\d+[^d]         positive modifier (no dice)
        # \-\d+[^d]         negative modifier (no dice)

        base_dice = re.findall('!r(\d+d\d+)', msg)
        modifier_dice = re.findall('[\+\-]\d*d\d+', msg)
        modifier = re.findall('[\+\-]\d+(?![d\d])', msg)

        # Check command format
        if len(base_dice) != 1:
            # No base dice found (or too many), return error message
            print("[" + str(message.content) + "; " + str(message.author) + "] Not correct number of base dice")
            await message.channel.send(str(message.author.mention) + " Something seems to be off with that command.\n"
                                                                     "Please use **!help** to see what formats are supported.")
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
            dice_split = dice.replace("+", "").split("d")
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
                                       "Please use **!help** to see what formats are supported.")
            # Do not proceed with message processing
            return
        elif total_dice_count > 20:
            # if len(dice_type) == 1:
            #     # No modifier dice
            #     dice_count[0] = 20
            #     # Add message to description and print warning to console
            #     add_msg = "\n*(I can only roll up to 20 dice at once)*"
            #     print("[" + str(message.content) + "] Too many dice to roll, limiting base dice count to 20")
            # else:
            # There are modifier dice, now just throw error
            print("[" + str(message.content) + "; " + str(message.author) + "] Too many dice to roll, throwing error")
            await message.channel.send(
                str(message.author.mention) + " Sorry, I cannot roll that many dice at once.\n"
                                              "Please try to roll 20 dice or less.")
            # Do not proceed with message processing
            return
            # end if/else
        # end if/elif

        # Create roll description
        desc = add_msg + "\n"
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

        # Setup embedding for dice roll response
        embed = discord.Embed(title=title_preset + "Rolling for " + str(message.author.name), description=desc,
                              color=0x76883c)
        footer = ""
        total_result = 0
        max_possible = 0
        min_possible = 0

        # Roll base dice
        if dice_type[0] == 20 and dice_count[0] == 1:
            # Start with 1d20, natural 1 or natural 20 can occur
            result = roll(20)[0]
            embed.add_field(name="d20", value=result, inline=True)

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
                if dice_count[0] < 0:
                    # Negative base dice count
                    embed.add_field(name="-d" + str(dice_type[0]), value="-" + str(result),
                                    inline=True)

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[0]
                else:
                    # Positive base dice count
                    embed.add_field(name="d" + str(dice_type[0]), value=result, inline=True)

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
                if dice_count[i] < 0:
                    # Negative dice modifier
                    embed.add_field(name="-d" + str(dice_type[i]), value="-" + str(result),
                                    inline=True)

                    total_result -= result
                    max_possible -= 1
                    min_possible -= dice_type[i]
                    print(min_possible)
                else:
                    # Positive dice modifier
                    embed.add_field(name="d" + str(dice_type[i]), value=result, inline=True)

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
            embed.add_field(name="Modifier", value=modifier_total, inline=True)
        # end if

        total_result += modifier_total
        max_possible += modifier_total
        min_possible += modifier_total

        # Add total to embedding
        embed.add_field(name="Total", value=total_result, inline=False)

        # Store message for re-rolling
        prev_call = msg

        # Add stats if wanted
        if roll_stats:
            if footer == "":
                # Footer is empty (so no nat. 1 or 20)
                embed.set_footer(text="min. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " +
                                      str(round(
                                          (total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
            else:
                footer += ("\nmin. " + str(min_possible) + "; max. " + str(max_possible) + " 🡢 " +
                           str(round((total_result - min_possible) / (max_possible - min_possible) * 100)) + "%")
                embed.set_footer(text=footer)
            # end if/else
        # end if

        # Send message to Discord and update status
        await message.channel.send(warning, embed=embed)
        # await client.change_presence(activity=discord.Game(name="Rolled " + str(rolled) + " dice"))
        print(str(time.time() - start) + "sec; now rolled " + str(rolled) + " dice")
        return
    # end if - Regular dice roll


# end def

client.run(BOT_TOKEN)
