## Resource conversion bot for Epic RPG

This is a Discord bot which implements a simple shortest path graph-based conversion strategy between the many resources available in Epic RPG. It allows users to quickly switch areas as they progress through the game and intelligently alerts them to impossible trades (apples for logs in Area 1, for example). A user is automatically registered with the bot their first time using it, and information such as area preferences and usage statistics are persistently stored in a PostgreSQL database. 


[To invite the bot to your server, click here.](https://discord.com/api/oauth2/authorize?client_id=773260807638089768&permissions=8&scope=bot)

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
