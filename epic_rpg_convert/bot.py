import os
import random
import time
import numpy as np

import epic_rpg_convert as e

import discord
from discord.ext import commands
from dotenv import load_dotenv

inv_users = {'current': ""}

def run():
    trigger = "!CONV"

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = commands.Bot(command_prefix=trigger)

    db = e.methods.Database(os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASS"))

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')

    @bot.event
    async def on_message(message):
        print(message.content)

        guild = str(message.guild.id)

        split = message.content.rstrip().split(" ")

        if split[0] == "rpg":
            if split[1] == "i" or split[1] == "inv" or split[1] == "inventory":
                inv_users[guild] = str(message.author).replace("#", "_")
                print(f"Found inv: {inv_users[guild]}")

        if len(message.embeds) > 0:
            if e.methods.is_inventory(message):
                e.methods.parse_inv(message, db, inv_users[guild])

        if split[0] == trigger:

            user = str(message.author).replace("#", "_")

            if not db.user_exists(user):
                db.add_user(user)
                await message.channel.send(embed = e.subcommands.call_new_user(user))
                
            area = db.get_area(user)

            if len(split) == 1:
                embed = e.subcommands.call_help()
            else:
                if split[1] == ["ca", "area", "change", "change-area"]:
                    embed = e.subcommands.call_change_area(message, user, db)
                elif split[1] in ["h", "help"]:
                    embed = e.subcommands.call_help()
                elif split[1] in ["i", "inv", "inventory"]:
                    embed = e.subcommands.call_inventory(message, area, db, user)
                elif split[1] in ["u", "user"]:
                    embed = e.subcommands.call_user_summary(db, user)
                else: 
                    embed = e.subcommands.call_convert(message, area)

            await message.channel.send(embed = embed)
 
    bot.run(TOKEN)
