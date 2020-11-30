import os
import random
import time
import numpy as np

import epic_convert as e

import discord
from discord.ext import commands
from dotenv import load_dotenv

area_db = {}

def run():
    trigger = "!CONV"

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = commands.Bot(command_prefix=trigger)

    db = e.methods.Database("testdb", "ccole", "password")

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')

    @bot.event
    async def on_message(message):
        print(message.content)

        split = message.content.rstrip().split(" ")

        if split[0] == trigger:

            user = str(message.author).replace("#", "_")

            if not db.user_exists(user):
                db.add_user(user)
                
            area = db.get_area(user)

            if len(split) == 1:
                embed = e.subcommands.call_help()
            else:
                if split[1] == "change-area":
                    embed = e.subcommands.call_change_area(message, user, db)
                elif split[1] == "help":
                    embed = e.subcommands.call_help()
                else: 
                    embed = e.subcommands.call_convert(message, area)

            await message.channel.send(embed = embed)
 
    bot.run(TOKEN)
