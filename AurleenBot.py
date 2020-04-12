import discord
import random
import json
import re

# DEBUG
print("Starting up...")

# Setup global variables
client = discord.Client()
rolled = 0

# Load data from json fil
try:
    with open('data.json') as f:
        data = json.load(f)
        BOT_TOKEN = data['bot_token']
except Exception as e:
    print("Error, probably no data.json found: " + str(e))
# end try except


# Dice rolling function
def roll(d):
    global rolled
    rolled += 1
    return random.randint(1, d)
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
    print('Ready on Discord as {0.user}'.format(client))
    # await client.change_presence(activity=discord.Game(name='Ready to roll!'))
    await client.change_presence(activity=discord.Game(name='Don\'t mind me, just testing the bot!'))
# end def


# When a message is received
@client.event
async def on_message(message):
    # Setup variables
    global rolled
    msg = ""
    add_msg = ""

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
    # end if

    # TODO
    # Run regular rolling when calling !d20 or !rd20

    # BOT INFORMATION
    if msg.startswith(('!help', "!aurleenbot", "!aurleen")):
        embed = discord.Embed(title="AurleenBot Sample Commands", color=0x76883c)
        embed.add_field(name="!r1d20", value="Roll a d20", inline=False)
        embed.add_field(name="!r5d6", value="Roll five d6 and sum up", inline=False)
        embed.add_field(name="!advantage (!adv) / !disadvantage (!dis)",
                        value="Roll two d20 and keep the highest or lowest respectively", inline=False)
        embed.add_field(name="!bless / !guidance", value="Roll a d20 and a d4", inline=False)
        embed.add_field(name="All commands support modifier dice, e.g. !r1d20+1d4",
                        value="Add + or - your modifier dice to add it to the total of the roll", inline=False)
        embed.add_field(name="All commands also support a modifier, e.g. !r1d20+5 or !r1d20+1d4-2",
                        value="Add + or - your modifier to add it to the total of the roll", inline=False)
        embed.set_footer(text="pls don't break me")
        await message.channel.send(embed=embed)
        print("Showed info")
        return
    # end if

    # Custom presets for 1d20 + 1d4
    if msg.startswith("!bless"):
        msg = msg.replace("!bless", "!r1d20+1d4")
        add_msg += "\n*Bless: +1d4*"
    # end if - bless preset

    if msg.startswith("!guidance"):
        msg = msg.replace("!guidance", "!r1d20+1d4")
        add_msg += "\n*Guidance: +1d4*"
    # end if - guidance preset

    if msg.startswith("!bane"):
        msg = msg.replace("!bane", "!r1d20-1d4")
        add_msg += "\n*Bane: -1d4*"
    # end if - guidance preset

    # Only process message if it is a command for rolling (i.e. starting with '!r')
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
            print("[" + str(message.content) + "] Not correct number of base dice")
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
            print("[" + str(message.content) + "] No dice left after unifying")
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
                print("[" + str(message.content) + "] Too many dice to roll, throwing error")
                await message.channel.send(
                    str(message.author.mention) + " Sorry, I cannot roll that many dice at once.\n"
                                                  "Please try to roll 20 dice or less.")
                # Do not proceed with message processing
                return
            # end if/else
        # end if/elif

        # Create roll description
        desc = str(dice_count[0]) + "d" + str(dice_type[0])
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
        desc += add_msg

        # Setup embedding for dice roll response
        embed = discord.Embed(title="Rolling for " + str(message.author.name), description=desc, color=0x76883c)
        total_result = 0
        max_possible = 0

        print("Type:", dice_type)
        print("Count:", dice_count)

        # Roll base dice
        if dice_type[0] == 20 and dice_count[0] == 1:
            # Start with 1d20, natural 1 or natural 20 can occur
            result = roll(20)
            embed.add_field(name="d20", value=result, inline=True)

            if result == 20:
                embed.set_footer(text="NATURAL 20")
            elif result == 1:
                embed.set_footer(text="NATURAL 1")
            # end if/elif

            total_result += result
            max_possible += 20
        else:
            for j in range(dice_count[0]):
                result = roll(dice_type[0])
                embed.add_field(name="d" + str(dice_type[0]) + " #" + str(j+1), value=result, inline=True)

                total_result += result
                max_possible += dice_type[0]
            # end for
        # end if/else
        print("Base:", total_result)
        print(len(dice_type))

        # Any other dice rolling
        for i in range(1, len(dice_type)):
            if abs(dice_count[i]) == 1:
                # Roll once
                result = roll(dice_type[i])

                if dice_count[i] < 0:
                    embed.add_field(name="-d" + str(dice_type[i]), value="-" + str(result),
                                    inline=True)

                    total_result -= result
                    # max_possible += dice_type[i]
                else:
                    embed.add_field(name="d" + str(dice_type[i]), value=result, inline=True)

                    total_result += result
                    max_possible += dice_type[i]
                # end if/else
            else:
                # Roll multiple dice
                for j in range(abs(dice_count[i])):
                    result = roll(dice_type[i])

                    if dice_count[i] < 0:
                        embed.add_field(name="-d" + str(dice_type[i]) + " #" + str(j+1), value="-" + str(result), inline=True)

                        total_result -= result
                        # max_possible += dice_type[i]
                    else:
                        embed.add_field(name="d" + str(dice_type[i]) + " #" + str(j+1), value=result, inline=True)

                        total_result += result
                        max_possible += dice_type[i]
                    # end if/else
                # end for
            # end if/else
        # end for
        print("Additional Dice:", total_result)

        # Add modifier to calculate total
        if modifier_total != 0:
            embed.add_field(name="Modifier", value=modifier_total, inline=True)
        # end if

        total_result += modifier_total
        max_possible += modifier_total
        embed.add_field(name="Total", value=total_result, inline=False)
        # embed.add_field(name="*out of*", value="*" + str(max_possible) +
        #                                        " (" + str(round(total_result/max_possible*100)) + "%)*", inline=True)

        # Send message to Discord
        await message.channel.send(embed=embed)
    # end if

    # General rolling
    # if message.content.startswith("!r") or message.content.startswith("/r"):
    #     regex = re.findall(r'\d+', message.content)
    #     nums = list(map(int, regex))
    #
    #     dice_count = nums[0]
    #     dice = nums[1]
    #
    #     # Limit dice count to 20
    #     if dice_count > 20:
    #         await message.channel.send("Please roll no more than 20 dice at once")
    #         dice_count = 20
    #     # end if
    #
    #     total = 0
    #     desc = str(dice_count) + "d" + str(dice)
    #
    #     if len(nums) > 2:
    #         if "-" in message.content:
    #             bonus = -1 * nums[2]
    #             desc += " - " + str(nums[2])
    #         else:
    #             bonus = nums[2]
    #             desc += " + " + str(nums[2])
    #     else:
    #         bonus = 0
    #     # end if/else
    #     embed = discord.Embed(title="Rolling for " + str(message.author.name), description=desc, color=0x76883c)
    #
    #     if dice_count == 1 and dice == 20:
    #         d20 = roll(20)
    #         total += d20
    #         embed.add_field(name="d20", value=d20, inline=True)
    #         if d20 == 20:
    #             embed.set_footer(text="NATURAL 20")
    #         elif d20 == 1:
    #             embed.set_footer(text="NATURAL 1")
    #         # end if/else
    #     else:
    #         for r in range(dice_count):
    #             roll = roll(dice)
    #             total += roll
    #             embed.add_field(name="d" + str(dice) + " #" + str(r+1), value=roll, inline=True)
    #         # end for
    #
    #     if len(nums) > 2:
    #         embed.add_field(name="Modifier", value=bonus, inline=True)
    #     # end if
    #
    #     total += bonus
    #     embed.add_field(name="Total", value=total, inline=False)
    #
    #     await message.channel.send(embed=embed)
    # # end if
    #
    # # Advantage
    # if message.content.startswith("!adv") or message.content.startswith("/adv"):
    #     regex = re.findall(r'\d+', message.content)
    #     nums = list(map(int, regex))
    #
    #     embed = discord.Embed(title="Rolling with advantage for " + str(message.author.name), color=0x76883c)
    #     total = 0
    #
    #     if len(nums) > 0:
    #         if "-" in message.content:
    #             bonus = -1 * int(nums[0])
    #         else:
    #             bonus = int(nums[0])
    #     else:
    #         bonus = 0
    #     # end if/else
    #
    #     d20_1 = roll(20)
    #     d20_2 = roll(20)
    #     total += max(d20_1, d20_2)
    #     embed.add_field(name="d20 #1", value=d20_1, inline=True)
    #     embed.add_field(name="d20 #2", value=d20_2, inline=True)
    #     if max(d20_1, d20_2) == 20:
    #         embed.set_footer(text="NATURAL 20")
    #     elif max(d20_1, d20_2) == 1:
    #         embed.set_footer(text="NATURAL 1")
    #     # end if/else
    #
    #     if len(nums) > 0:
    #         embed.add_field(name="Modifier", value=bonus, inline=True)
    #     # end if
    #
    #     total += bonus
    #     embed.add_field(name="Total", value=total, inline=False)
    #
    #     await message.channel.send(embed=embed)
    # # end if
    #
    # # Disadvantage
    # if message.content.startswith("!dis") or message.content.startswith("/dis"):
    #     regex = re.findall(r'\d+', message.content)
    #     nums = list(map(int, regex))
    #
    #     embed = discord.Embed(title="Rolling with disadvantage for " + str(message.author.name), color=0x76883c)
    #     total = 0
    #
    #     if len(nums) > 0:
    #         if "-" in message.content:
    #             bonus = -1 * int(nums[0])
    #         else:
    #             bonus = int(nums[0])
    #     else:
    #         bonus = 0
    #     # end if/else
    #
    #     d20_1 = roll(20)
    #     d20_2 = roll(20)
    #     total += min(d20_1, d20_2)
    #     embed.add_field(name="d20 #1", value=d20_1, inline=True)
    #     embed.add_field(name="d20 #2", value=d20_2, inline=True)
    #     if min(d20_1, d20_2) == 20:
    #         embed.set_footer(text="NATURAL 20")
    #     elif min(d20_1, d20_2) == 1:
    #         embed.set_footer(text="NATURAL 1")
    #     # end if/else
    #
    #     if len(nums) > 0:
    #         embed.add_field(name="Modifier", value=bonus, inline=True)
    #     # end if
    #
    #     total += bonus
    #     embed.add_field(name="Total", value=total, inline=False)
    #
    #     await message.channel.send(embed=embed)
    # # end if
    #
    # # Bless/Guidance spell
    # if message.content.startswith('!bless') or message.content.startswith('!guidance') or \
    #         message.content.startswith("/bless") or message.content.startswith("/guidance"):
    #     d20 = roll(20)
    #     d4 = roll(4)
    #     splitcall = message.content.split("+")
    #
    #     embed = discord.Embed(title="Rolling for " + str(message.author.name), color=0x76883c)
    #     embed.add_field(name="d20", value=d20, inline=True)
    #     embed.add_field(name="d4", value=d4, inline=True)
    #
    #     if len(splitcall) > 1:
    #         # add bonus to roll
    #         bonus = int(splitcall[1])
    #         embed.add_field(name="Modifier", value=bonus, inline=True)
    #     else:
    #         # default roll
    #         bonus = 0
    #     total = d20 + d4 + bonus
    #
    #     embed.add_field(name="Total", value=total, inline=False)
    #     if d20 == 20:
    #         embed.set_footer(text="NATURAL 20")
    #     elif d20 == 1:
    #         embed.set_footer(text="NATURAL 1")
    #     # end if/else
    #
    #     await message.channel.send(embed=embed)
    # # end if
    #
    # # await client.change_presence(activity=discord.Game(name='Rolled ' + str(rolled) + ' dice'))
    #
    # # Shutting down
    # if message.content.startswith('!quit') or message.content.startswith('!exit') or \
    #         message.content.startswith("/quit") or message.content.startswith("/exit"):
    #     await client.change_presence(activity=discord.Game(name='OFFLINE'))
    #     await message.channel.send("Shutting down...")
    #     print("Shutting down...")
    # # end if
    #
    # # help
    # if message.content.startswith('!help') or message.content.startswith('!AurleenBot') or \
    #         message.content.startswith('!Aurleenbot') or message.content.startswith('!aurleenbot'):
    #     embed = discord.Embed(title="AurleenBot Sample Commands", color=0x76883c)
    #     embed.add_field(name="!r1d20", value="Roll a d20", inline=False)
    #     embed.add_field(name="!r5d6", value="Roll five d6 and sum up", inline=False)
    #     embed.add_field(name="!advantage (!adv) / !disadvantage (!dis)",
    #                     value="Roll two d20 and keep the highest or lowest respectively", inline=False)
    #     embed.add_field(name="!bless / !guidance", value="Roll a d20 and a d4", inline=False)
    #     embed.add_field(name="All commands support a modifier, e.g. !r1d20+5",
    #                     value="Add + or - your modifier to add it to the total of the roll", inline=False)
    #     embed.set_footer(text="pls don't break me")
    #     await message.channel.send(embed=embed)
    #     print("Showed info")
    # # end if
# end def

client.run(BOT_TOKEN)
