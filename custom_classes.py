import textwrap
import random
import arcade
import numpy as np
import heapq
import tmx
import os
from items import *
from PIL import Image


wait_time = 0.02

rc = ROWS, COLS = (9, 16)
wh = WIDTH, HEIGHT = (64, 64)
sc = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)
FONT_WIDTH = 5*8

current_map = 'overworld'
raw_maps = {}
loc_array = {}
map_dir = [f for f in os.listdir('./Maps') if os.path.isfile(os.path.join('./Maps', f))]
img_dir = [f for f in os.listdir('./Images') if os.path.isfile(os.path.join('./Images', f))]

for file in map_dir:
    cur_map = tmx.TileMap.load('./Maps/{}'.format(file))
    file_name = file.split('.')[0]
    raw_maps[file_name] = {}
    for layer in cur_map.layers:
        map_data = []
        for tile in layer.tiles:
            if tile.gid != 0:
                map_data.append(tile.gid-1)
            else:
                map_data.append(-1)
        if len(cur_map.layers) > 1:
            try:
                raw_maps[file_name][int(layer.name)] = np.flip(np.array(map_data, dtype=int).reshape((cur_map.height, cur_map.width)), 0)
            except ValueError:
                raw_maps[file_name][layer.name] = np.flip(np.array(map_data, dtype=int).reshape((cur_map.height, cur_map.width)), 0)
                raw_maps[file_name]['{} Copy'.format(layer.name)] = raw_maps[file_name][layer.name][:]
        else:
            raw_maps[file_name] = np.flip(np.array(map_data, dtype=int).reshape((cur_map.height, cur_map.width)), 0)

for file in img_dir:
    file_name = file.split('.')[0]
    cur_img = Image.open('./Images/{}'.format(file))
    loc_array[file_name] = [[j, i, 64, 64] for i in range(0, cur_img.size[1], 64) for j in range(0, cur_img.size[0], 64)]
    cur_img.close()

tile_set = arcade.draw_commands.load_textures('./Images/8x8Tile.png', loc_array['8x8Tile'])
font = arcade.draw_commands.load_textures('./Images/8x8Font.png', loc_array['8x8Font'])

movemnet_keys = {
    'Up': (arcade.key.W, arcade.key.UP, arcade.key.NUM_8),
    'Down': (arcade.key.S, arcade.key.DOWN, arcade.key.NUM_2),
    'Left': (arcade.key.A, arcade.key.LEFT, arcade.key.NUM_4),
    'Right': (arcade.key.D, arcade.key.RIGHT, arcade.key.NUM_6),
    'Inv': (arcade.key.E, arcade.key.TAB),
    'Context': (arcade.key.SPACE, arcade.key.NUM_ADD),
    'Exit': (arcade.key.ESCAPE, ),
    'Map': (arcade.key.M, arcade.key.NUM_DECIMAL)
}


def astar(start, goal, array=raw_maps[current_map]['Collision']):
    def heuristic(a, b):
        return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:

        current = heapq.heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    continue
            else:
                continue
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return False


def roll_dice(s='1d'):
    d = list(map(int, s.split('d')))
    return int(s != '1d') * sum(sorted(list(random.randint(1, d[1])
                                            for _ in range(d[0])))[d[-1] * (len(d) > 2):]) or random.randint(0, 1)


class Player:
    def __init__(self):
        self.gold = Gold(100)
        self.stats = {
            'Str': roll_dice('4d6d1'),
            'Dex': roll_dice('4d6d1'),
            'Int': roll_dice('4d6d1'),
            'Wil': roll_dice('4d6d1'),
            'Per': roll_dice('4d6d1'),
            'HP': 8,
            'FP': 0,
            'XP': 0
        }
        self.inventory = [book, redbottle, greataxe]
        self.appearance = tile_set[1767]
        self.equipped = []
        self.x = 26
        self.y = 71

    @staticmethod
    def get_bag(bag, is_list=True):
        if is_list:
            return [['  {} '.format(i.name)] for i in bag]
        else:
            return [i.name for i in bag]

    def equip_stats(self):
        return [[str(i)] for i in self.equipped]

    def get_stats(self):
        return 'Str:{Str:02d} Dex:{Dex:02d} Int:{Int:02d} Wil:{Wil:02d} Per:{Per:02d}'.format(**self.stats).split()

    def get_points(self):
        return ['{HP:02d}'.format(**self.stats), '{FP:02d}'.format(**self.stats)]


class Actor:
    def __init__(self, yx, target, sprite, disposition):
        self.y, self.x = yx
        self.target = target
        self.sprite = sprite
        self.disposition = disposition  # 0 = Neutral, 1 = Aggressive, 2 = Friendly

    def move_me(self, goal, pathfind=True):
        if pathfind:
            global raw_maps, current_map
            if self.disposition > 0:
                path = astar((self.y, self.x), goal, raw_maps[current_map]['Collision'])
                if type(path) is list:
                    if len(path) > 1 + self.disposition - 1:
                        raw_maps[current_map]['Mid'][self.y, self.x] = raw_maps[current_map]['Mid Copy'][self.y, self.x]
                        raw_maps[current_map]['Collision'][self.y, self.x] = raw_maps[current_map]['Collision Copy'][self.y, self.x]
                        self.y, self.x = path[-1]
                        raw_maps[current_map]['Mid'][self.y, self.x] = self.sprite
                        raw_maps[current_map]['Collision'][self.y, self.x] = -1
                        print(self.x, self.y)
            else:
                raw_maps[current_map]['Collision'][self.y, self.x] = raw_maps[current_map]['Collision Copy'][self.y, self.x]
                raw_maps[current_map]['Mid'][self.y, self.x] = self.sprite
        else:
            raw_maps[current_map]['Mid'][self.y, self.x] = raw_maps[current_map]['Mid Copy'][self.y, self.x]
            raw_maps[current_map]['Collision'][self.y, self.x] = raw_maps[current_map]['Collision Copy'][self.y, self.x]
            self.y, self.x = goal
            raw_maps[current_map]['Mid'][self.y, self.x] = self.sprite
            raw_maps[current_map]['Collision'][self.y, self.x] = -1


class DialogItem:
    def __init__(self, text=None, speaker=None, dialog_opts=None):
        self.speaker = speaker
        if type(text) is str:
            self.text = textwrap.wrap(text, 22)
        else:
            self.text = text
        if type(dialog_opts) is list:
            if type(dialog_opts[0]) is list:
                self.dialog_opts = [[' {} '.format(opt) for opt in lin] for lin in dialog_opts]
            else:
                self.dialog_opts = [[' {} '.format(opt)] for opt in dialog_opts]
        else:
            self.dialog_opts = dialog_opts


nodes = {
    2: DialogItem(text='Anime makes you gay.', speaker='Your Mother'),
    3: DialogItem(text="Steal the boat?", dialog_opts=([['Yes', 'Why?', 'Property is theft'],
                                                        ['No', 'Steal half', 'Whose boat?']])),
}

