import os
import random
import time
import numpy as np
import logging
from datetime import datetime

import epic_rpg_convert as e

import discord
from discord.ext import commands
from dotenv import load_dotenv

d = datetime.now()
up = d.strftime("%d/%m/%y %H:%M")


inv_users = {'current': ""}

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

client = discord.Client()
def run():
    trigger = "!CONV"

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = commands.Bot(command_prefix=trigger)

    db = e.methods.Database(os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASS"))


    @bot.event
    async def on_ready():
        n = len(bot.guilds)
        logging.info(f'{bot.user.name} has connected to {n} guilds on Discord!')
    

    @bot.event
    async def on_message(message):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!conv help"))
        if message.author == bot.user:
            return
        
        guild = message.guild.id
        channel = bot.get_channel(int(os.getenv("CHANNEL_ID")))
        user_channel = bot.get_channel(int(os.getenv("NEW_USER_CHANNEL_ID")))

        if not message.author.bot:
            if message.content.split(" ")[0].upper() == "!CONV":
                message_logger = discord.Embed(title = "Message log", description = f"{message.content}", color=0xff0000)
                message_logger.add_field(name = "Username", value = f"{message.author}", inline = True)
                message_logger.add_field(name = "Guild", value = f"{message.guild}", inline = True)
                message_logger.add_field(name = "Channel", value = f"{message.channel}", inline = True)
            
                if message.content.split(" ")[0].lower() != "rpg":
                    await channel.send(embed = message_logger)


        split = message.content.rstrip().split(" ")
        split = [i.lower() for i in split]

        if split[0].lower() == "rpg":
            if split[1] == "i" or split[1] == "inv" or split[1] == "inventory":
                inv_users[guild] = str(message.author).replace("#", "_")
                #print(f"Found inv: {inv_users[guild]}")


        user = str(message.author).replace("#", "_")

        if len(message.embeds) > 0:
            if e.methods.is_inventory(message):
                try:
                    e.methods.parse_inv(message, db, inv_users[guild])
                except (KeyError, IndexError):
                    #e.subcommands.call_inventory_error(user)
                    logging.warning("Tried to parse an inventory but failed.")

        if split[0].upper() == trigger:

            user = str(message.author).replace("#", "_")

            if not db.user_exists(user):
                db.add_user(user)
                await user_channel.send(embed = e.subcommands.call_log_new_user(message))
                await message.channel.send(embed = e.subcommands.call_new_user(user))
                
            area = db.get_area(user)

            if len(split) == 1:
                embed = e.subcommands.call_help()
            else:
                if split[1] in ["ca", "area", "change", "change-area"]:
                    embed = e.subcommands.call_change_area(message, user, db)
                elif split[1] in ["h", "help"]:
                    if len(split) > 2:
                        if split[2] in ["more", "long"]:
                            embed = e.subcommands.call_long_help()
                        else:
                            embed = e.subcommands.call_help()
                    else:
                        embed = e.subcommands.call_help()
                elif split[1] in ["i", "inv", "inventory", "all"]:
                    if len(split) > 3:
                        embed = e.subcommands.call_convert(message, area, db, user)
                    else:
                        embed = e.subcommands.call_inventory(message, area, db, user)
                elif split[1] in ["u", "user"]:
                    embed = e.subcommands.call_user_summary(db, user)
                elif split[1] in ["v", "vote"]:
                    embed = e.subcommands.call_vote(user)
                elif split[1] in ["info"]:
                    n = len(bot.guilds)
                    embed = e.subcommands.call_info(str(n), up)
                else: 
                    embed = e.subcommands.call_convert(message, area, db, user)

            await message.channel.send(embed = embed)
 
    bot.run(TOKEN)
