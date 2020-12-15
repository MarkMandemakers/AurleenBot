# AurleenBot
AurleenBot is a Discord bot for dice rolling in (digital) D&D Games.

### Features
- Roll any type of dice
- Roll multiple dice (types) at once, either regularly or at (dis)advantage
- Add modifier values with inline math
- Prefix support for D&D spells like [Bless](https://www.dndbeyond.com/spells/bless) and [Bane](https://www.dndbeyond.com/spells/bane)
- Show statistics of individual rolls (can be enabled or disabled)
- Display statistics of all d20's rolled
- Restrict certain commands to admin users


### Installation & Usage
AurleenBot was built in Python 3.7.x and requires the following dependencies:
- [discord.py](https://github.com/Rapptz/discord.py )
- [json](https://docs.python.org/3/library/json.html )
- [re](https://docs.python.org/3/library/re.html )
- [time](https://docs.python.org/3/library/time.html )
- [datetime](https://docs.python.org/3/library/datetime.html )
- [matplotlib](https://matplotlib.org/ )
- [NumPy](https://numpy.org/ )
- [os](https://docs.python.org/3/library/os.html )
- [GitPython](https://gitpython.readthedocs.io/en/stable/)

The bot could in theory be run using any Python execution method. Before it is ready for use, the following is required:
- Create a application in the [Discord Developer Portal](https://discordapp.com/developers/applications)
- Add a bot user to the application within the portal. For ease-of-use it is recommended to make the bot public and create an invite link to get the bot into a server.
- Create a `data.json` file using the [sample file](https://github.com/MarkMandemakers/AurleenBot/blob/master/SAMPLE_data.json) provided and add your bot token (found under the "Build-A-Bot" section in the Discord Developer Portal), as well as one or more Discord users that are seen as the bot's admins.
- Invite the bot to your server and run the Python script. You should be ready to roll!


### Sample Commands
- **!aurleenbot**  
  *Display sample commands like the ones below*
- **!r1d20**  
  *Roll a d20*
- **!r5d6**  
  *Roll five d6 and sum up*
- **!advantage (!adv) / !disadvantage (!dis)**  
  *Roll two d20 and keep the highest or lowest respectively*
- **!bless / !guidance**  
*Roll a d20 and add a d4, as achieved by the [Bless](https://www.dndbeyond.com/spells/bless) spell*
- **!bane**  
*Roll a d20 and subtract a d4, as achieved by the [Bane](https://www.dndbeyond.com/spells/bane) spell*
- **!reroll / !re-roll**  
*Re-Roll the previous roll command (__Note__ the bot re-rolls the last call from anyone, not just the message author)*
- **All commands support modifier dice, e.g. !r1d20+1d4**  
*Add + or - your modifier dice to add it to the total of the roll*
- **All commands also support a modifier, e.g. !r1d20+5 or !r1d20+1d4-2**  
*Add + or - your modifier to add it to the total of the roll*



### Author & License
AurleenBot is created by [Mark Mandemakers](https://github.com/MarkMandemakers) and is licensed under the MIT License - see the [LICENSE](https://github.com/MarkMandemakers/AurleenBot/blob/master/LICENSE) file for details.
