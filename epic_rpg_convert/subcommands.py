import epic_convert as e
import discord
def call_convert(message, area):
    n, i1, i2 = e.methods.parse_input(message.content)
    graph = e.methods.create_base_graph(area)
    total = e.methods.convert(graph, i1,i2,int(n))
    if total == "Bad":
        return call_error(message, area)

    text = e.methods.details(graph, i1, i2, int(n))

    embedVar = discord.Embed( description=f"Conversions for Area {area}", color=0x00ff00)
    embedVar.add_field(name=i1, value=n, inline=True)
    embedVar.add_field(name=i2, value=str(total), inline=True)

    embedVar.add_field(name="Details", value=text, inline=False)
    embedVar.set_footer(text = "Need help? Find more commands with !CONV help.")
    return embedVar

def call_error(message, area):
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



