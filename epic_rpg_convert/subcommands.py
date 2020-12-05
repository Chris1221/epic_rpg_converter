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
        'apple',
        'banana',
        'normie_fish',
        'golden_fish',
        'epic_fish',
        'ruby']

def call_convert(message, area):
    n, i1, i2 = e.methods.parse_input(message.content)
    
    if i2 == "log":
        i2 = "wooden-log"
    elif i2 == "fish":
        i2 = "normie-fish"

    i1 = e.methods.standardize_item_string(i1)
    i2 = e.methods.standardize_item_string(i2)

    graph = e.methods.create_base_graph(area)
    total = e.methods.convert(graph, i1,i2,int(n))
    if total == "Bad":
        return call_error(area)

    text = e.methods.details(graph, i1, i2, int(n))

    embedVar = discord.Embed( description=f"Conversions for Area {area}", color=0x00ff00)
    embedVar.add_field(name=e.methods.format_item_string(i1), value=n, inline=True)
    embedVar.add_field(name=e.methods.format_item_string(i2), value=str(total), inline=True)

    embedVar.add_field(name="Details", value=text, inline=False)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_error( area):
    embedVar = discord.Embed(title = "Error", description = "Something went wrong.")
    embedVar.add_field(name = "Area", value = f"You are in Area str(area)")
    embedVar.add_field(name = "Details", value = "The trade that you asked for is impossible in the current area.")  
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_change_area(message, user, db):
    command, subcommand, area = message.content.rstrip().split(" ")
    if subcommand == "change-area":
        db.update_area(user, area)
        area = int(area)
        embedVar = discord.Embed( description="Area change", color=0xff0000)
        embedVar.add_field(name="User", value=message.author, inline=False)
        embedVar.add_field(name="Now in...", value=f"Area {str(area)}", inline=True)
        embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
        return embedVar

def call_help():
    embedVar = discord.Embed(title = "Help menu", description="How to use the bot.", color=0xff0000)
    embedVar = embedVar.add_field(name = "Basic usage", value = "`n item1 item2`\n Convert `n` `item1` to `item2`, if possible." )
    embedVar = embedVar.add_field(name = "Other commands", value = "- `change-area` `n`\n\t\tChanges to use trade rates from a specific area.\n- `help`\n\t\t Show this menu.")
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar


def call_inventory_error(user):
    embedVar = discord.Embed(title = "Whoops, something went wrong...", description="I can't find your inventory, have you called `rpg i` recently?", color=0xff0000)
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



