import epic_rpg_convert as e
import discord
import psycopg2
import psycopg2.errors
import networkx as nx
import numpy as np

possible_items = ['wooden_log',
        'epic_log',
        'super_log',
        'mega_log',
        'hyper_log',
        'ultra_log',
        'apple',
        'banana',
        'normie_fish',
        'golden_fish',
        'epic_fish',
        'ruby']

def call_convert(message, area, db, user):
    n, i1, i2 = e.methods.parse_input(message.content)

    if i2 == "log":
        i2 = "wooden-log"
    elif i2 == "fish":
        i2 = "normie-fish"

    if i1 == "log":
        i1 = "wooden-log"
    elif i1 == "fish":
        i1 = "normie-fish"

    i1 = e.methods.standardize_item_string(i1)
    i2 = e.methods.standardize_item_string(i2)

    if n.lower() in ["all", "inv"]:
        try:
            inv = db.get_items(user)
        except:
            db._rollback()
            return call_inventory_error(user)
        try:
            n = int(inv[i1])
        except KeyError:
            return call_inventory_error()
    else: 
        n  =int(n)
 
    graph = e.methods.create_base_graph(area)
    total = e.methods.convert(graph, i1,i2,n)
    if total == "Bad":
        return call_error(area)

    text = e.methods.details(graph, i1, i2, int(n))

    embedVar = discord.Embed( description=f"Conversions for Area {area}", color=0x44cc00)
    embedVar.add_field(name=e.methods.format_item_string(i1), value=n, inline=True)
    embedVar.add_field(name=e.methods.format_item_string(i2), value=str(total), inline=True)

    embedVar.add_field(name="Details", value=text, inline=False)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_error( area):
    embedVar = discord.Embed(title = "Error", description = "Something went wrong.")
    embedVar.add_field(name = "Area", value = f"{str(area)}")
    embedVar.add_field(name = "Details", value = "The trade that you asked for is impossible in the current area.")  
    embedVar.add_field(name = "Hint", value = "Psst... Have you updated your area correctly? The bot can't tell automatically so you have to use !CONV area X to let it know. You start in area 1 by default, and certain trades (like apples to anything) are impossible here. See !CONV help for details. :smile: ", inline = False)  
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_vote(user):
    username = user.split("_")[0]
    embedVar = discord.Embed(title = "Support the bot", description=f"If you like this bot, I would really appreciate a vote on top.gg! Your reward will be an internet hug. Thank you {username} :smile:", color=0xff0000)
    embedVar.add_field(name="Link", value="[Use this link to vote!](https://top.gg/bot/773260807638089768/vote)", inline=True)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_log_new_user(message):
    embed = discord.Embed(title = "New user added to database.", description = f"{message.author}")
    embed.add_field(name = "Guild", value = f"{message.guild}")
    embed.add_field(name = "Channel", value = f"{message.channel}")
    return embed


def call_change_area(message, user, db):
    command, subcommand, area = message.content.rstrip().split(" ")
    db.update_area(user, area)
    area = int(area)
    embedVar = discord.Embed( description="Area change", color=0xff0000)
    embedVar.add_field(name="User", value=message.author, inline=False)
    embedVar.add_field(name="Now in...", value=f"Area {str(area)}", inline=True)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

help_desc = "Convert between item types in Epic RPG." 
important_things =\
"""

Item names use __dashes__, not __spaces__. I.e. **epic-fish** not **epic fish**.

__Set your area__ before you try to do any trades. Some things are impossible.

Before using inventory commands, you **must** run `rpg inv` to *show* or *update* the bot's version of your inventory. It can't read your mind.

__This bot doesn't actually convert the items for you__ (it isn't allowed to), it just tells you **how many items** you could create.

"""

quick_commands =\
"""
Convert `n` of `item1` to `item2`: ```!CONV 50000 log epic-fish``` 
Convert your whole inventory to a single item: ```!CONV inv hyper-log```
Change area to `x`: ```!CONV area 7```
See your user data: ```!CONV user```
Vote for the bot: ```!CONV vote```
"""

more_help =\
"""
See the more detailed version of this menu with `!CONV help more` or check out the source code on [Github](https://github.com/Chris1221/epic_rpg_converter).
"""

def call_help():
    e = discord.Embed(title = "Help menu", description = help_desc, color =0x44cc00)
    e = e.add_field(name = ":exclamation: Important Information :exclamation:", value = important_things)
    e = e.add_field(name = ":clock1: Quick Commands :clock2:", value = quick_commands, inline = False)
    e = e.add_field(name = ":question: More help :question:", value = more_help, inline = False)
    e = e.add_field(name = ":partying_face: Join the official server :partying_face:", value = "Join the party at the official support server, [click here to join!](https://discord.gg/HeaGGmvPD7)", inline = False)
    return e

def call_long_help():
    embedVar = discord.Embed(title = "Help menu", description="Crafting items in Epic RPG requires converting between many different resource types, resulting in many tedious calculations. This bot completely automates the process of converting resources by telling you:\n\n1. How many of a certain item can craft a different item (i.e. if I have 200 apples, how many hyper logs can I craft?)\n\n2. How much of a certain item you could make out of your entire inventory (i.e. how many fish would I have if I converted every other item in my inventory to fish?)\nBecause trade rates are different between areas (and some trades are completely not allowed, like apples to logs in area 1), the bot also takes account of what area you are in.\n\n**NOTE**: This bot cannot actually perform the conversions for you, that would be against Discord's ToS. Instead, it tells you how many items you could create, so that you can make better decisions and weigh options.\n\n If you like this bot, please [vote for it on top.gg](https://top.gg/bot/773260807638089768/vote) so that others can find it too!", color=0x44cc00)
    embedVar = embedVar.add_field(name = "Converting Specific Items", value = "To convert a specific number of resources to a different kind of item, tell the bot how many of the first that you have, and which item you want to convert them to: ```!CONV n item1 item2``` If this is not possible, or not possible in your current area (because, for example, you cannot trade apples to logs in area 1), the bot will tell you. Items which have two words must be seperated by a `-` and be all lower case. \n**Example**: ```!CONV 5 apple log\n!CONV 5 hyper-log fish\n!CONV 6 ruby epic-fish```", inline = False)
    embedVar = embedVar.add_field(name = "Converting Your Entire Inventory", value = "You can also see how many of a resource could be made from all of the resources in your inventory. This bot cannot interface directly with EPIC RPG because of how Discord allows bots to behave, so you must **show** your inventory to update it. That means running ```rpg inv``` (or any other valid inventory command) to update the values in your inventory for this bot. **You must do this before trying to use any other inventory commands.** To convert your entire inventory to a certain resource, tell the bot that you want to convert your inventory, and then the item that you want to convert it to:```!CONV inv item``` **Example**: ```!CONV i log\n!CONV inv hyper-log\n!CONV inventory epic-fish.```", inline = False)
    embedVar = embedVar.add_field(name = "Trade Rates from an Area", value = "Available trades and their rates are different between areas. To tell the bot which area you want to use, tell it that you want to change areas, and which area to use. This will be stored in your user profile until you change it. **Example:** ```!CONV change-area 6```", inline= False)
    embedVar = embedVar.add_field(name = "Your User Data", value = "To see all of the data that the bot has collected on you, just ask it! ```!CONV user```")
    embedVar = embedVar.add_field(name = "Vote for this bot", value = "To vote for this bot, ask it for a link. ```!CONV vote```.")
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_new_user(user):
    embedVar = discord.Embed(title = f"Welcome to the party, {user}!", description = "I'm happy you've chosen to use my bot. Start converting items right away with ```CONV! n item1 item2```", color = 0xff0000)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_inventory_error(user):
    embedVar = discord.Embed(title = "Whoops, something went wrong...", description="Either I can't find your inventory, or the item that you have requested is not in it. Have you called `rpg i` recently?", color=0xff0000)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_user_summary(db, user):
    time = db.get_first_seen(user).strftime("%b %d, %Y at %H:%m:%S EST")
    uses = db.get_count(user)
    inv_time = db.get_last_updated_time_inv(user).strftime("%b %d, %Y at %H:%m:%S EST")
    username, uid = user.split("_")
    area = db.get_area(user)

    embedVar = discord.Embed(title = "Your user profile.", description = "Here's everything that I know about you.")
    embedVar = embedVar.add_field(name = "Username", value = f"{username}", inline = True)
    embedVar = embedVar.add_field(name = "Unique ID", value = f"{uid}", inline = True)
    embedVar = embedVar.add_field(name = "Times you've used the bot", value = f"{uses}", inline = True)
    
    embedVar = embedVar.add_field(name = "Current Area", value = f"{area}", inline = True)

    embedVar = embedVar.add_field(name = "First seen on", value = f"{time}", inline = False)
    embedVar = embedVar.add_field(name = "Inventory updated on", value = f"{inv_time}", inline = True)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar



def call_inventory(message, area, db, user):

    spl = message.content.rstrip().split(" ")
    try:
        inv = db.get_items(user)
    except:
        db._rollback()
        return call_inventory_error(user)

    time = db.get_last_updated_time_inv(user).strftime("%b %d, %Y at %H:%m:%S EST")
    
    if len(spl) == 2:

        inv_string = e.methods.print_inventory(inv)
        
        embedVar = discord.Embed(title = "Estimated Inventory", description="This is based off of the last time that you called `rpg inventory`, so if it is out of date, try run that command again.", color=0xff0000)
        embedVar = embedVar.add_field(name = "Your current inventory", value = inv_string, inline = True)
        embedVar = embedVar.add_field(name = "Last updated at", value = time, inline = True)
        embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
        return embedVar

    if len(spl) == 3:
        graph = e.methods.create_base_graph(area)
        
        s = ""
        i2 = spl[2].replace("-", "_")

        if i2 == "log":
            i2 = "wooden_log"
        elif i2 == "fish":
            i2 = "normie_fish"

        # silly for loop for try block, otherwise dict comp
        items = {}
        for k in possible_items:
            try: 
                items[k] = inv[k]
            except KeyError:
                items[k] = 0

        s = "Individual conversions:\n\n"

        for item in possible_items:
            path = nx.shortest_path(graph, item, i2)
            current_add = 0
            for i, j in zip(path, path[1:]):
                w = graph[i][j]['weight']
                amount = np.floor(w*items[i])
                items[j] += amount 
                items[i] -= np.floor(amount / w)
 
                if e.methods.format_item_string(j) == e.methods.format_item_string(i2):
                    current_add += amount

            if current_add > 0:
                s += f"**{e.methods.format_item_string(item)}** :arrow_right: {str(int(current_add))} **{e.methods.format_item_string(i2)}**\n"

        total = items[i2]

        if total != total:
            return call_error(area)

        embedVar = discord.Embed( description=f"Conversions for Area {area}", color=0x00ff00)
        embedVar.add_field(name="Inventory", value="Everything!", inline=True)
        embedVar.add_field(name=e.methods.format_item_string(i2), value=str(int(total)), inline=True)

        embedVar.add_field(name="Details", value = s, inline = False)
        embedVar.add_field(name="Note", value = "The values above are a simplification of the real calculation. There are many different orders in which items can be converted. The procedure shows, in order, converting all of the given item to the target item (or as close as possible), using any left over items for the subsequent conversions.", inline = False)
        embedVar.add_field(name= "Inventory last updated at:", value = time)
#        embedVar.add_field(name="Details", value=s, inline=False)
        embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
        return embedVar



