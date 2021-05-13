
# AurleenBot
AurleenBot is a Discord bot for dice rolling in (digital) D&D Games.

### Features
- Roll any type of dice
- Roll multiple dice (types) at once, either regularly or at (dis)advantage
- Roll up to 100 dice at once (by default), since this could be useful in some cases. Looking at you [Meteor Swarm](https://www.dndbeyond.com/spells/meteor-swarm)...
- Add modifier values with inline math
- Check if rolls pass a certain threshold
- Private rolls with results via Discord DM
- Prefix support for D&D spells like [Bless](https://www.dndbeyond.com/spells/bless) and [Bane](https://www.dndbeyond.com/spells/bane)
- Show statistics of individual rolls
- Display statistics of all d20's rolled
- Restrict certain commands to admin users
- Per-server settings, e.g. watch specific channels


### Installation & Usage
AurleenBot was built in Python 3.7.x and requires the following dependencies:
- [discord.py](https://github.com/Rapptz/discord.py ) (version >= 1.5)
- [json](https://docs.python.org/3/library/json.html )
- [re](https://docs.python.org/3/library/re.html )
- [time](https://docs.python.org/3/library/time.html )
- [datetime](https://docs.python.org/3/library/datetime.html )
- [matplotlib](https://matplotlib.org/ )
- [NumPy](https://numpy.org/ )
- [os](https://docs.python.org/3/library/os.html )
- [sys](https://docs.python.org/3/library/sys.html )
- [math](https://docs.python.org/3/library/math.html )

The bot could in theory be run using any Python execution method. Before it is ready for use, the following is required:
- Create a application in the [Discord Developer Portal](https://discordapp.com/developers/applications)
- Add a bot user to the application within the portal. For ease-of-use it is recommended to make the bot public and create an invite link to get the bot into a server.
- Create a `data.json` file using the [data sample file](https://github.com/MarkMandemakers/AurleenBot/blob/master/SAMPLE_data.json) provided and add your bot token (found under the "Build-A-Bot" section in the Discord Developer Portal), as well as one or more Discord users that are seen as the bot's admins.
- This file can either be stored in the same directory of `AurleenBot.py`, or can be stored in a different location (e.g. Dropbox). In the latter case, create `loc.json` based on the [loc sample file](https://github.com/MarkMandemakers/AurleenBot/blob/master/SAMPLE_loc.json). In the file add the directory location of the `data.json` file.
- The bot will create a `discord.json` file storing per-server data in the same location as `data.json`
- Invite the bot to your server and run the Python script. You should be ready to roll!


### Sample Commands
- **!aurleenbot / !help**  
  *Display sample commands like the ones below*
- **!r1d20**  
  *Roll a d20*
- **!r5d6**  
  *Roll five d6 and sum up (__Note__ There is a limit on the number of dice that can be rolled at once; by default this is 100 but can be changed in the Python file)*
- **!advantage (!adv) / !disadvantage (!dis)**  
  *Roll two d20 and keep the highest or lowest respectively*
- **!reroll / !re-roll**  
  *Re-Roll the previous roll command (__Note__ The bot re-rolls the last call from anyone, not just the message author)*
  
### Presets
- **!bless / !guidance**  
  *Roll a d20 and add a d4, as achieved by the [Bless](https://www.dndbeyond.com/spells/bless) spell*
- **!bane**  
  *Roll a d20 and subtract a d4, as achieved by the [Bane](https://www.dndbeyond.com/spells/bane) spell*
  
### Command Additions
- **Dice Modifiers, e.g. !r1d20+1d4**  
  *Add + or - your modifier dice to add it to the total of the roll*
- **Value Modifiers, e.g. !r1d20+5 or !r1d20+1d4-2**  
  *Add + or - your modifier to add it to the total of the roll*
- **Roll Checks, e.g. !r1d100<=7**  
  *Supported checks: >, >=, =, ==, <, <=*
- **Private Rolls:**  
	- *Add dm or h to command to get result via Discord DM, e.g. !dm1d20 or !hadv+6*
	- *Rolls also work if you send Discord DM to the bot*



### Author & License
AurleenBot is created by [Mark Mandemakers](https://github.com/MarkMandemakers) and is licensed under the MIT License - see the [LICENSE](https://github.com/MarkMandemakers/AurleenBot/blob/master/LICENSE) file for details.
