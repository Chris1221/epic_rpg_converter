import networkx as nx
import numpy as np
import os
import psycopg2

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

    c.add_edge('log', 'fish', weight = a.fish(area, True))
    c.add_edge('fish', 'log', weight = a.fish(area))

    # Add fish values.
    c.add_edge('fish', 'golden-fish', weight = 1/15)
    c.add_edge('golden-fish', 'fish', weight = 12) 

    c.add_edge('golden-fish', 'epic-fish', weight = 1/100)
    c.add_edge('epic-fish', 'golden-fish', weight = 80)

    ## Wood values
    c.add_edge('log', 'epic-log', weight = 1/25)
    c.add_edge('epic-log', 'log', weight = 20)

    c.add_edge('epic-log', 'super-log', weight = 1/10)
    c.add_edge('super-log', 'epic-log', weight = 8)

    c.add_edge('super-log', 'mega-log', weight = 1/10)
    c.add_edge('mega-log', 'super-log', weight = 8)

    c.add_edge('mega-log', 'hyper-log', weight = 1/10)
    c.add_edge('hyper-log', 'mega-log', weight = 8)

    c.add_edge('hyper-log', 'ultra-log', weight = 1/10)
    c.add_edge('ultra-log', 'hyper-log', weight = 8)

    ## Fruit
    c.add_edge('apple', 'log', weight = a.apple(area, True))
    c.add_edge('log', 'apple', weight = a.apple(area, False))

    c.add_edge('banana', 'apple', weight = 12)
    c.add_edge('apple', 'banana', weight = 1/15)
    
    ## Other
    c.add_edge('ruby', 'log', weight = a.ruby(area, False))
    c.add_edge('log', 'ruby', weight = a.ruby(area, True))

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

        text += f"{int(running)} {i} :arrow_right: {int(total)} {j}\n"
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
        self.cursor.execute("insert into users (name, area, number_of_connects) values (%s, %s, %s);", (user, 1, 0))
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







