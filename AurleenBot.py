import discord
import random
import json
import re

# Setup global variables
client = discord.Client()
rolled = 0

# Load data from json fil
try:
    with open('data.json') as f:
        data = json.load(f)
        CLIENT_ID = data['client_id']
except Exception as e:
    print("Error, probably no data.json found: " + str(e))
# end try except


# Roll dice
def rolld(d):
    global rolled
    rolled += 1
    return random.randint(1, d)
# end def


# When done setting up the bot user in Discord
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='Ready to roll!'))
# end def


# When a message is received
@client.event
async def on_message(message):
    global rolled

    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    # end if

    # General rolling
    if message.content.startswith("!r") or message.content.startswith("/r"):
        regex = re.findall(r'\d+', message.content)
        nums = list(map(int, regex))

        dice_count = nums[0]
        dice = nums[1]

        # TODO
        # Add desription to embed, e.g. "5d6 + 5"
        embed = discord.Embed(title="Rolling for " + str(message.author), color=0x76883c)
        total = 0

        if len(nums) > 2:
            if "-" in message.content:
                bonus = -1 * nums[2]
            else:
                bonus = nums[2]
        else:
            bonus = 0
        # end if/else

        if dice_count == 1 and dice == 20:
            d20 = rolld(20)
            total += d20
            embed.add_field(name="d20", value=d20, inline=True)
            if d20 == 20:
                embed.set_footer(text="NATURAL 20")
            elif d20 == 1:
                embed.set_footer(text="NATURAL 1")
            # end if/else
        else:
            for r in range(dice_count):
                roll = rolld(dice)
                total += roll
                embed.add_field(name="d" + str(dice) + " #" + str(r+1), value=roll, inline=True)
            # end for

        if len(nums) > 2:
            embed.add_field(name="Modifier", value=bonus, inline=True)
        # end if

        total += bonus
        embed.add_field(name="Total", value=total, inline=False)

        await message.channel.send(embed=embed)
    # end if

    # Advantage
    if message.content.startswith("!adv") or message.content.startswith("/adv"):
        regex = re.findall(r'\d+', message.content)
        nums = list(map(int, regex))

        embed = discord.Embed(title="Rolling with advantage for " + str(message.author), color=0x76883c)
        total = 0

        if len(nums) > 0:
            if "-" in message.content:
                bonus = -1 * int(nums[0])
            else:
                bonus = int(nums[0])
        else:
            bonus = 0
        # end if/else

        d20_1 = rolld(20)
        d20_2 = rolld(20)
        total += max(d20_1, d20_2)
        embed.add_field(name="d20 #1", value=d20_1, inline=True)
        embed.add_field(name="d20 #2", value=d20_2, inline=True)
        if max(d20_1, d20_2) == 20:
            embed.set_footer(text="NATURAL 20")
        elif max(d20_1, d20_2) == 1:
            embed.set_footer(text="NATURAL 1")
        # end if/else

        if len(nums) > 0:
            embed.add_field(name="Modifier", value=bonus, inline=True)
        # end if

        total += bonus
        embed.add_field(name="Total", value=total, inline=False)

        await message.channel.send(embed=embed)
    # end if

    # Disadvantage
    if message.content.startswith("!dis") or message.content.startswith("/dis"):
        regex = re.findall(r'\d+', message.content)
        nums = list(map(int, regex))

        embed = discord.Embed(title="Rolling with disadvantage for " + str(message.author), color=0x76883c)
        total = 0

        if len(nums) > 0:
            if "-" in message.content:
                bonus = -1 * int(nums[0])
            else:
                bonus = int(nums[0])
        else:
            bonus = 0
        # end if/else

        d20_1 = rolld(20)
        d20_2 = rolld(20)
        total += min(d20_1, d20_2)
        embed.add_field(name="d20 #1", value=d20_1, inline=True)
        embed.add_field(name="d20 #2", value=d20_2, inline=True)
        if min(d20_1, d20_2) == 20:
            embed.set_footer(text="NATURAL 20")
        elif min(d20_1, d20_2) == 1:
            embed.set_footer(text="NATURAL 1")
        # end if/else

        if len(nums) > 0:
            embed.add_field(name="Modifier", value=bonus, inline=True)
        # end if

        total += bonus
        embed.add_field(name="Total", value=total, inline=False)

        await message.channel.send(embed=embed)
    # end if

    # Bless/Guidance spell
    if message.content.startswith('!bless') or message.content.startswith('!guidance') or \
            message.content.startswith("/bless") or message.content.startswith("/guidance"):
        d20 = rolld(20)
        d4 = rolld(4)
        splitcall = message.content.split("+")

        embed = discord.Embed(title="Rolling for " + str(message.author), color=0x76883c)
        embed.add_field(name="d20", value=d20, inline=True)
        embed.add_field(name="d4", value=d4, inline=True)

        if len(splitcall) > 1:
            # add bonus to roll
            bonus = int(splitcall[1])
            embed.add_field(name="Modifier", value=bonus, inline=True)
        else:
            # default roll
            bonus = 0
        total = d20 + d4 + bonus

        embed.add_field(name="Total", value=total, inline=False)
        if d20 == 20:
            embed.set_footer(text="NATURAL 20")
        elif d20 == 1:
            embed.set_footer(text="NATURAL 1")
        # end if/else

        await message.channel.send(embed=embed)
    # end if

    await client.change_presence(activity=discord.Game(name='Rolled ' + str(rolled) + ' dice'))

    # Shutting down
    if message.content.startswith('!quit') or message.content.startswith('!exit') or \
            message.content.startswith("/quit") or message.content.startswith("/exit"):
        await client.change_presence(activity=discord.Game(name='OFFLINE'))
        await message.channel.send("Shutting down...")
        print("Shutting down...")
    # end if
# end def

client.run(CLIENT_ID)
