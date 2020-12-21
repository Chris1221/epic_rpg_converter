import networkx as nx
import numpy as np
import os
import psycopg2
import json
import datetime
import re
## Conversion logic

## Items are stored as edges in a graph, with
## paths weighted by conversion amounts.
##
## Clearly this is directed (as constructing
## and deconstructing have different amounts)

class Area:
    def __init__(self):
        self.areas = {}

    def apple(self, area, recip = False):
        rates = [0,0,3,4,4,15,15,8,12,12,8,8,8,8]
        allowed = [False,False,True,True,True,True,True,True,True,True,True,True,True,True]
        if allowed[area-1]:
            if recip:
                return 1 / rates[area-1]
            else:
                return rates[area-1]
        else:
            return 0

    def fish(self, area, recip = False):
        rates = [1,1,1,2,2,3,3,3,2,3,3,3,3,3]
        if recip:
            return 1 / rates[area-1]
        else:
            return rates[area-1]

    def ruby(self, area, recip = False):
        rates = [0,0,0,0,450,675,675,675,850,500,500,350,350,350] 
        allowed = [False,False,False,False,True,True,True,True,True,True,True,True,True,True]
        if allowed[area-1]:
            if recip:
                return 1 / rates[area-1]
            else:
                return rates[area-1]
        else:
            return 0

def create_base_graph(area = 1):
    c = nx.DiGraph()
    a = Area()

    ## Base definition in terms of wood and fish.
    ## This needs to be generalized per area.

    c.add_edge('wooden_log', 'normie_fish', weight = a.fish(area, True))
    c.add_edge('normie_fish', 'wooden_log', weight = a.fish(area))

    # Add fish values.
    c.add_edge('normie_fish', 'golden_fish', weight = 1/15)
    c.add_edge('golden_fish', 'normie_fish', weight = 12) 

    c.add_edge('golden_fish', 'epic_fish', weight = 1/100)
    c.add_edge('epic_fish', 'golden_fish', weight = 80)

    ## Wood values
    c.add_edge('wooden_log', 'epic_log', weight = 1/25)
    c.add_edge('epic_log', 'wooden_log', weight = 20)

    c.add_edge('epic_log', 'super_log', weight = 1/10)
    c.add_edge('super_log', 'epic_log', weight = 8)

    c.add_edge('super_log', 'mega_log', weight = 1/10)
    c.add_edge('mega_log', 'super_log', weight = 8)

    c.add_edge('mega_log', 'hyper_log', weight = 1/10)
    c.add_edge('hyper_log', 'mega_log', weight = 8)

    c.add_edge('hyper_log', 'ultra_log', weight = 1/10)
    c.add_edge('ultra_log', 'hyper_log', weight = 8)

    ## Fruit
    c.add_edge('apple', 'wooden_log', weight = a.apple(area, False))
    c.add_edge('wooden_log', 'apple', weight = a.apple(area, True))

    c.add_edge('banana', 'apple', weight = 12)
    c.add_edge('apple', 'banana', weight = 1/15)
    
    ## Other
    c.add_edge('ruby', 'wooden_log', weight = a.ruby(area, False))
    c.add_edge('wooden_log', 'ruby', weight = a.ruby(area, True))

    return c


def convert(graph, item1, item2, n):
    path = nx.shortest_path(graph, item1, item2)
    total = 0
    for i, j in zip(path, path[1:]):
        w = graph[i][j]['weight']
        if w == 0: return "Bad"
        if not total:
            total += n * w
        else:
            total *= w
        print(f"STEP: Weight {w}, total {total}")

    return int(np.floor(total))

def details(graph, item1, item2, n):
    path = nx.shortest_path(graph, item1, item2)
    total = 0
    text = ""
    running = n
    for i, j in zip(path, path[1:]):
        w = graph[i][j]['weight']
        if not total:
            total += n * w
        else:
            total *= w

        text += f"{int(running)} **{format_item_string(i)}**\t:arrow_right:\t{int(total)} **{format_item_string(j)}**\n"
        running = total
        #print(f"STEP: Weight {w}, total {total}")
    return text



def parse_input(message):
    """ Example !CONV 1 epic-log golden-fish """
    parts = message.rstrip().split(" ")
    n = parts[1]
    i1 = parts[2]
    i2 = parts[3]

    return (n, i1, i2)

def add_user(user, user_db):
    user_db[user] = 1

def get_area(message, area_db):
    if message.author not in area_db:
        area_db[message.author] = 1
        area = 1
    else:
        area = area_db[message.author]

    return area


class Database:
    def __init__(self,name, user, password):
        try: 
            self.con = psycopg2.connect(database = name)
            self.cursor = self.con.cursor()
        except psycopg2.OperationalError:
            os.system(f"createdb {name}")
            os.system(f'psql -c "\c {name}" -c "\i sql/make_database.sql"')
            self.con = psycopg2.connect(database = name)
            self.cursor = self.con.cursor()
    
    def add_user(self, user):
        self.cursor.execute("insert into users (name, area, number_of_connects, first_seen) values (%s, %s, %s, %s);", (user, 1, 0, datetime.datetime.now()))
        self.con.commit() 
        self.cursor.execute("insert into inventory (username) values (%s);", (user,))
        self.con.commit() 

        print(f"Added user {user} to database")

    def user_exists(self, user):
        self.cursor.execute('select exists(select area from users where name= %s);', (user,))
        self.con.commit()
        return self.cursor.fetchall()[0][0]

    def get_area(self, user):
        self.cursor.execute("select area from users where name = %s", (user,))
        self.con.commit()
        return self.cursor.fetchall()[0][0]

    def update_area(self, user, area):
        self.cursor.execute("update users set area = %s where name = %s", (area, user,))
        self.con.commit()
        self.count(user)

    def count(self, user):
        self.cursor.execute("select number_of_connects from users where name = %s", (user,))
        self.con.commit()
        n = self.cursor.fetchall()[0][0]

        self.cursor.execute("update users set number_of_connects = %s where name = %s", (n + 1, user))
        self.con.commit()

    def get_count(self, user):
        self.cursor.execute("select number_of_connects from users where name = %s", (user,))
        self.con.commit()
        return self.cursor.fetchall()[0][0]

    def add_items(self, user, items):
        self.cursor.execute(f"update inventory set items = %s, last_update = %s where username = %s", (json.dumps(items), datetime.datetime.now(), user,))
        self.con.commit()

    def get_items(self, user):
        self.cursor.execute(f"select items from inventory where username = %s", (user,))
        self.con.commit()
        return json.loads(self.cursor.fetchall()[0][0])

    def get_last_updated_time_inv(self, user):
        self.cursor.execute(f"select last_update from inventory where username = %s", (user,))
        self.con.commit()
        return self.cursor.fetchall()[0][0]
    
    def get_first_seen(self, user):
        self.cursor.execute(f"select first_seen from users where name = %s", (user,))
        self.con.commit()
        return self.cursor.fetchall()[0][0]

    def _rollback(self):
        self.cursor.execute("rollback")



## Inventory stuff.
# This would probably be better off as a class
# with a __repr__ and constructor from either
# message or db.
def parse_inv(message, db, user):
    items = message.embeds[0].fields[0]
    if items.name != "Items":
        print("Error: Inventory is not formatted correctly.")
    else:
        dict_of_items = {s.split("**")[1].lower().replace(" ", "_"): int(s.split("**")[2].lstrip(": ")) for s in items.value.split("\n")}
        db.add_items(user, dict_of_items)

def is_inventory(message):
    return "inventory" in str(message.embeds[0].author)

def print_inventory(inv):
    s = ""
    for (item, amount) in inv.items():
        s += f"**{format_item_string(item)}**: {str(amount)}\n"

    return s

def format_item_string(item):
    spl = re.split("_|\-", item)
    spl[0] = spl[0].capitalize()
    return " ".join(spl)


def standardize_item_string(item):
    return item.replace("-", "_")
