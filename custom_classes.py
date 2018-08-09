import arcade
import numpy as np
import heapq
import tmx
import os
import time
from items import *
from PIL import Image

wait_time = 0.01

rc = ROWS, COLS = (9, 16)
wh = WIDTH, HEIGHT = (64, 64)
sc = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)

current_map = 'overworld'
raw_maps = {}
loc_array = {}
options_menu = [['Settings'], ['Gameplay'], ['Exit']]
map_dir = [f for f in os.listdir('./Maps') if os.path.isfile(os.path.join('./Maps', f))]
img_dir = [f for f in os.listdir('./Images') if os.path.isfile(os.path.join('./Images', f))]
char_width = {' ': 32, '!': 16, '"': 32, '#': 48, '$': 32, '%': 32, '&': 48, "'": 16, '(': 24, ')': 24, '*': 32, '+': 32, ',': 16, '-': 32, '.': 16, '/': 32,
              '0': 32, '1': 32, '2': 32, '3': 32, '4': 32, '5': 32, '6': 32, '7': 32, '8': 32, '9': 32, ':': 16, ';': 16, '<':  32, '=': 32, '>': 32, '?': 32,
              '@': 48, 'A': 32, 'B': 32, 'C': 32, 'D': 32, 'E': 32, 'F': 32, 'G': 32, 'H': 32, 'I': 32, 'J': 32, 'K': 32, 'L': 32, 'M': 48, 'N': 32, 'O': 32,
              'P': 32, 'Q': 32, 'R': 32, 'S': 32, 'T': 32, 'U': 32, 'V': 32, 'W': 48, 'X': 32, 'Y': 32, 'Z': 32, '[': 24, '\\': 32, ']': 24, '^': 32, '_': 32,
              '`': 8,  'a': 32, 'b': 32, 'c': 32, 'd': 32, 'e': 32, 'f': 32, 'g': 32, 'h': 32, 'i': 16, 'j': 32, 'k': 32, 'l': 24, 'm': 48, 'n': 32, 'o': 32,
              'p': 32, 'q': 32, 'r': 32, 's': 32, 't': 32, 'u': 32, 'v': 32, 'w': 48, 'x': 32, 'y': 32, 'z': 32, '{': 32, '|': 16, '}': 32, '~': 32
}

for file in map_dir:  # Some layers need copies, and i figure having backups cant hurt
    map_file = tmx.TileMap.load('./Maps/{}'.format(file))
    file_name = file.split('.')[0]
    raw_maps[file_name] = {}
    for layer in map_file.layers:
        map_data = []
        raw_maps[file_name]['Sprite'] = np.zeros(shape=(map_file.width, map_file.height), dtype=int)
        raw_maps[file_name]['Sprite Copy'] = np.zeros(shape=(map_file.width, map_file.height), dtype=int)
        for tile in layer.tiles:
            if tile.gid != 0:
                map_data.append(tile.gid-1)
            else:
                map_data.append(-1)
        if len(map_file.layers) > 1:
            try:
                raw_maps[file_name][int(layer.name)] = np.flip(np.array(map_data, dtype=int).reshape((map_file.height, map_file.width)), 0)
            except ValueError:
                raw_maps[file_name][layer.name] = np.flip(np.array(map_data, dtype=int).reshape((map_file.height, map_file.width)), 0)
                raw_maps[file_name]['{} Copy'.format(layer.name)] = np.flip(np.array(map_data, dtype=int).reshape((map_file.height, map_file.width)), 0)
        else:
            raw_maps[file_name] = np.flip(np.array(map_data, dtype=int).reshape((map_file.height, map_file.width)), 0)

for img in img_dir:
    img_name = img.split('.')[0]
    cur_img = Image.open('./Images/{}'.format(img))
    loc_array[img_name] = [[j, i, WIDTH, HEIGHT] for i in range(0, cur_img.size[1], WIDTH) for j in range(0, cur_img.size[0], HEIGHT)]
    cur_img.close()

tile_set = arcade.draw_commands.load_textures('./Images/Tile.png', loc_array['Tile'])
font = arcade.draw_commands.load_textures('./Images/Font.png', loc_array['Font'])

movemnet_keys = {
    'Up': (arcade.key.W, arcade.key.UP, arcade.key.NUM_8, arcade.key.NUM_UP),
    'Down': (arcade.key.S, arcade.key.DOWN, arcade.key.NUM_2, arcade.key.NUM_DOWN),
    'Left': (arcade.key.A, arcade.key.LEFT, arcade.key.NUM_4, arcade.key.NUM_LEFT),
    'Right': (arcade.key.D, arcade.key.RIGHT, arcade.key.NUM_6, arcade.key.NUM_RIGHT),
    'Inv': (arcade.key.E, arcade.key.TAB, arcade.key.NUM_ENTER),
    'Context': (arcade.key.SPACE, arcade.key.NUM_ADD),
    'Exit': (arcade.key.ESCAPE, ),
    'Map': (arcade.key.M, arcade.key.NUM_DECIMAL),
    'NE': (arcade.key.NUM_9, arcade.key.NUM_PAGE_UP),
    'NW': (arcade.key.NUM_7, arcade.key.NUM_HOME),
    'SE': (arcade.key.NUM_3, arcade.key.NUM_PAGE_DOWN),
    'SW': (arcade.key.NUM_1, arcade.key.NUM_END),
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
    return int(s != '1d') * sum(sorted(list(np.random.randint(1, d[1])
                                            for _ in range(d[0])))[d[-1] * (len(d) > 2):]) or np.random.randint(0, 1)


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
        self.inventory = [book, redbottle, greataxe, book, redbottle, greataxe, book, redbottle, greataxe]
        self.appearance = 1767
        self.equipped = []
        self.x = 26
        self.y = 71
        self.state = 'Walking'

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
        return '{HP:02d} {FP:02d}'.format(**self.stats).split()


class Actor:
    def __init__(self, yx, sprite, disposition, target_distance):
        self.y, self.x = yx
        self.sprite = sprite
        self.disposition = disposition
        self.target_distance = target_distance

    def move_me(self, goal):
        path = astar((self.y, self.x), goal, raw_maps[current_map]['Collision'])
        if path:
            if len(path) > self.target_distance:
                self.y, self.x = path[-1]
