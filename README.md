## Resource conversion bot for Epic RPG
[![Invite to server](https://img.shields.io/badge/Discord-Invite%20to%20server-blue?logo=discord)](https://discord.com/api/oauth2/authorize?client_id=773260807638089768&permissions=8&scope=bot) [![Discord Bots](https://top.gg/api/widget/status/773260807638089768.svg)](https://top.gg/bot/773260807638089768)


This is a Discord bot which implements a simple shortest path graph-based conversion strategy between the many resources available in Epic RPG. It allows users to quickly switch areas as they progress through the game and intelligently alerts them to impossible trades (apples for logs in Area 1, for example). A user is automatically registered with the bot their first time using it, and information such as area preferences and usage statistics are persistently stored in a PostgreSQL database. Testing.


---

[Usage](https://github.com/Chris1221/epic_rpg_converter#Usage)
- [Converting Specific Items](https://github.com/Chris1221/epic_rpg_converter#converting-specific-items)
- [Converting Your Entire Inventory](https://github.com/Chris1221/epic_rpg_converter#converting-your-entire-inventory)
- [Trade Rates from an Area](https://github.com/Chris1221/epic_rpg_converter#trade-rates-from-an-area)
- [Your User Data](https://github.com/Chris1221/epic_rpg_converter#your-user-data)

[Developer](https://github.com/Chris1221/epic_rpg_converter#developer)
- [Intalling the Bot](https://github.com/Chris1221/epic_rpg_converter#installing-the-bot)
- [Registering your bot](https://github.com/Chris1221/epic_rpg_converter#registering-your-bot)
- [Setting up your database](https://github.com/Chris1221/epic_rpg_converter#setting-up-your-database)
- [Running the bot](https://github.com/Chris1221/epic_rpg_converter#running-the-bot)


## Usage

#### Converting Specific Items

To convert a specific number of resources to a different kind of item, tell the bot how many of the first that you have, and which item you want to convert them to:

```
!CONV n item1 item2
```

If this is not possible, or not possible in your current area (because, for example, you cannot trade apples to logs in area 1), the bot will tell you. Items which have two words must be seperated by a - and be all lower case.

**Example**:

```
!CONV 5 apple log
!CONV 5 hyper-log fish
!CONV 6 ruby epic-fish
```

#### Converting Your Entire Inventory
You can also see how many of a resource could be made from all of the resources in your inventory. This bot cannot interface directly with EPIC RPG because of how Discord allows bots to behave, so you must show your inventory to update it. That means running `rpg inv` or any other valid inventory command to update the values in your inventory for this bot. You must do this before trying to use any other inventory commands. To convert your entire inventory to a certain resource, tell the bot that you want to convert your inventory, and then the item that you want to convert it to. If you don't specify an item, the bot will return your current inventory.

```
!CONV inv (item)
```

Example:

```
!CONV i log
!CONV inv hyper-log
!CONV inventory epic-fish.
```

#### Trade Rates from an Area

Available trades and their rates are different between areas. To tell the bot which area you want to use, tell it that you want to change areas, and which area to use. This will be stored in your user profile until you change it. Example:

```
!CONV change-area 6
```

#### Your User Data
To see all of the data that the bot has collected on you, just ask it!

```
!CONV user
```

## Developer 

If you want to host your own instance of the bot, follow these steps.

### Installing the bot

Clone the repository to your own computer and change directories.

```sh
git clone git@github.com:Chris1221/epic_rpg_converter.git
cd epic_rpg_converter
```
Install all of the python dependencies.

```
pip install -r requirements.txt
```

Then install the bot (we use the `-e` option here so that you can edit the code and run it right away.).

```
pip install -e .
```

### Registering your bot

 register a new bot on the [Discord Developer Portal](https://discord.com/developers/docs/intro) and obtain a bot token. 



Create a file called `.env`. We use `python-dotenv` to manage secrets. 

```sh
## In .env
DISCORD_TOKEN=${YOUR_TOKEN}
```

### Setting up your database

Ensure that you have PostgreSQL installed. You can either [download it](https://www.postgresql.org/download/) from an official repository or if you are on OSX, install it with Homebrew.

```
brew install postgresql
```

Start your PostgreSQL server (`psql`) 

```sh
pg_ctl -D $DATA -l $LOG start
```

Replacing the `DATA` directory and `LOG` variables with values appropriate for your system. 

Your username will be your system username by default.

Open up the `.env` file from before and add three values:

```
DB_NAME="Name"
DB_USER="YOUR_NAME"
DB_PASS="A_PASSWORD"
```

The name will be the name of the database that is created, while the username and password do what they say on the tin.

### Running the bot

To run the bot, either call `epic_rpg_converter.bot.run()` or use the command line entry point:

```sh
convert_bot
```

After that, invite your bot to a server and play around. If you want to use a different trigger (`!CONV` used here) so that you can have both bots in the same server, change the `trigger` variable in `bot.py`.
