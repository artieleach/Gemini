import arcade
import numpy as np
import heapq
import tmx
import os
import time
import textwrap
from PIL import Image

wait_time = 0.01

rc = ROWS, COLS = (9, 16)
wh = WIDTH, HEIGHT = (64, 64)
sc = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)

current_map = 'overworld'
raw_maps = {}
loc_array = {}
options_menu = ['Settings', 'Gameplay', 'Exit']

map_dir = [f for f in os.listdir('./Maps') if os.path.isfile(os.path.join('./Maps', f))]
img_dir = [f for f in os.listdir('./Images') if os.path.isfile(os.path.join('./Images', f))]
char_width = {' ': 32, '!': 16, '"': 32, '#': 48, '$': 32, '%': 32, '&': 48, "'": 16, '(': 24, ')': 24, '*': 32, '+': 32, ',': 16, '-': 32, '.': 16, '/': 32,
              '0': 32, '1': 32, '2': 32, '3': 32, '4': 32, '5': 32, '6': 32, '7': 32, '8': 32, '9': 32, ':': 16, ';': 16, '<':  32, '=': 32, '>': 32, '?': 32,
              '@': 48, 'A': 32, 'B': 32, 'C': 32, 'D': 32, 'E': 32, 'F': 32, 'G': 32, 'H': 32, 'I': 32, 'J': 32, 'K': 32, 'L': 32, 'M': 48, 'N': 32, 'O': 32,
              'P': 32, 'Q': 32, 'R': 32, 'S': 32, 'T': 32, 'U': 32, 'V': 32, 'W': 48, 'X': 32, 'Y': 32, 'Z': 32, '[': 24, '\\': 32, ']': 24, '^': 32, '_': 32,
              '`': 8,  'a': 32, 'b': 32, 'c': 32, 'd': 32, 'e': 32, 'f': 32, 'g': 32, 'h': 32, 'i': 16, 'j': 32, 'k': 32, 'l': 24, 'm': 48, 'n': 32, 'o': 32,
              'p': 32, 'q': 32, 'r': 32, 's': 32, 't': 32, 'u': 32, 'v': 32, 'w': 48, 'x': 32, 'y': 32, 'z': 32, '{': 32, '|': 16, '}': 32, '~': 32}


class Entity:
    def __init__(self, yx=(0, 0), name=None, sprite=-1):
        self.y, self.x = yx
        self.name = name
        self.sprite = sprite

    @staticmethod
    def name_list(self, *args):
        print(args)
        return [i.name for i in args]


for file in map_dir:  # Some layers need copies, and i figure having backups cant hurt
    map_file = tmx.TileMap.load('./Maps/{}'.format(file))
    file_name = file.split('.')[0]
    raw_maps[file_name] = {}
    for layer in map_file.layers:
        map_data = []
        raw_maps[file_name]['Sprite'] = np.zeros(shape=(map_file.width, map_file.height), dtype=Entity)
        raw_maps[file_name]['Sprite Copy'] = np.zeros(shape=(map_file.width, map_file.height), dtype=Entity)
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


class Actor(Entity):
    def __init__(self, yx, name, sprite, disposition, target_distance):
        Entity.__init__(self, yx, name, sprite)
        self.disposition = disposition
        self.target_distance = target_distance

    def move_me(self, goal):
        if (abs(self.y-goal[0]) + abs(self.x-goal[1])) > self.target_distance:  # i only want to calculate the path tree if need be
            path = astar((self.y, self.x), goal, raw_maps[current_map]['Collision'])
            if path:
                self.y, self.x = path[-1]
        elif self.y == goal[0] and self.x == goal[1]:  # lazy implentation of moving AI out of the way, needs to be rewritten for different dispositions
            if raw_maps[current_map]['Collision'][self.y + 1, self.x] == -1:
                self.y, self.x = self.y + 1, self.x
            elif not raw_maps[current_map]['Collision'][self.y - 1, self.x] == -1:
                self.y, self.x = self.y - 1, self.x
            elif not raw_maps[current_map]['Collision'][self.y, self.x + 1] == -1:
                self.y, self.x = self.y, self.x + 1
            else:
                self.y, self.x = self.y, self.x - 1


class Item(Entity):
    def __init__(self, name, cost, weight, sprite, flavor_text=None):
        Entity.__init__(self, name=name, sprite=sprite)
        self.cost = cost
        self.weight = weight
        self.flavor_text = flavor_text
        self.actions = ['Look', 'Drop']

    def look(self):
        return DialogItem(text=self.flavor_text, speaker=self.name)

    def get_actions(self):
        return [' {} '.format(i) for i in self.actions]


class EquipmentItem(Item):
    def __init__(self, name, cost, weight, sprite):
        Item.__init__(self, name=name, cost=cost, weight=weight, sprite=sprite)
        self.actions.append('Equip')


class Armor(EquipmentItem):
    def __init__(self, name, cost, weight, speed, asfc, armor_type, bonus, acp, max_bonus, sprite):
        EquipmentItem.__init__(self, name, cost, weight, sprite)
        self.armor_type = armor_type
        self.speed = speed
        self.asfc = asfc
        self.armor_type = armor_type
        self.bonus = bonus
        self.acp = acp
        self.cost = cost
        self.max_bonus = max_bonus

    def __repr__(self):
        return '   {} (+{})'.format(self.name, self.bonus)

    def look(self):
        return DialogItem(text='{} {} {}'.format(self.armor_type, self.asfc, self.bonus), speaker=self.name)


class Weapon(EquipmentItem):
    def __init__(self, name, dmg, dmg_style, weight, weapon_type, cost, handed, crit_mult, dmg_range, weap_id, q=0):
        self.weap_id = weap_id
        self.q = q  # 0 = Wood, 1 = Bronze, 2 = Iron, 3 = Steel, 4 = Green, 5 = Blue, 6 = Albanium
        self.texture = self.q * 57 + 2052 + weap_id
        EquipmentItem.__init__(self, name, cost, weight, self.texture)
        self.dmg = dmg
        self.dmg_style = dmg_style
        self.weapon_type = weapon_type
        self.handed = handed
        self.crit_mult = crit_mult
        self.dmg_range = dmg_range

    def __repr__(self):
        return '   {} ({})'.format(self.name, self.dmg)

    def look(self):
        return DialogItem(text='({} - {}) {} {}-Handed, crit:{}'.format(self.dmg, self.dmg_style, self.weapon_type, 'Two'*bool(self.handed-1) or 'One', self.crit_mult), speaker=self.name)


def gen_weapon(weapon, q):
    return Weapon(name=weapon.name, dmg=weapon.dmg, dmg_style=weapon.dmg_style, weight=weapon.weight,
                  weapon_type=weapon.weapon_type, cost=weapon.cost, handed=weapon.handed,
                  crit_mult=weapon.crit_mult, dmg_range=weapon.dmg_range, weap_id=weapon.weap_id, q=q)


class Gold:
    def __init__(self, cost):
        self.texture = [0, 0]
        self.cost = (cost//64, cost % 64)
        if self.cost[1] < 8:
            self.texture[1] = 614
        else:
            self.texture[1] = 671
        if self.cost[0] < 8:
            self.texture[0] = 615
        elif self.cost[0] < 64:
            self.texture[0] = 672
        elif self.cost[0] < 256:
            self.texture[0] = 668
        elif self.cost[0] < 512:
            self.texture[0] = 669
        else:
            self.texture[0] = 670

    def __repr__(self):
        return '{}g {}s'.format(self.cost[0], self.cost[1])


class DialogItem(Entity):
    def __init__(self, text=None, speaker=None, dialog_opts=None, yx=(0, 0), on_level=None, sprite=-1):
        Entity.__init__(self, yx=yx, sprite=sprite)
        self.speaker = speaker
        if type(text) is str:
            self.text = textwrap.wrap(text, 22)
        else:
            self.text = text
        if dialog_opts:
            self.dialog_opts = list(dialog_opts.keys())
        else:
            self.dialog_opts = None
        '''
        if type(dialog_opts) is dict:
            if type(dialog_opts[0]) is list:
                self.dialog_opts = [[' {} '.format(opt) for opt in lin] for lin in dialog_opts]
            else:
                self.dialog_opts = [[' {} '.format(opt)] for opt in dialog_opts]
        else:
            self.dialog_opts = dialog_opts'''

    def new_opt(self, newopt):
        pass


# BrokenDoor = DialogItem(sprite=33, text='Anime makes you gay', dialog_opts=[['Whats anime', 'Whys anime'], ['Ya', 'Nah']], speaker='Thine Momther', yx=(73, 27), on_level='Overworld')
BrokenDoor = DialogItem(sprite=33, text='asdfasdf', speaker='Thine Momther', yx=(73, 27), on_level='Overworld')
BrDo2 = DialogItem(sprite=33, text='asdfasdf',
                   dialog_opts={"What this?": BrokenDoor, "Why that?": BrokenDoor, "Who there?": BrokenDoor, "When it?": BrokenDoor},
                   speaker='Thine Momther', yx=(73, 27), on_level='Overworld')


class Player(Entity):
    def __init__(self):
        Entity.__init__(self, yx=(71, 26), name=Player, sprite=1767)
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
        self.inventory = []
        self.equipped = {'Head': None, 'Left Hand': None, 'Right Hand': None, 'Feet': None, 'Chest': None, 'Legs': None, 'Rings': [], }
        self.state = 'Walking'

    @staticmethod
    def get_bag(bag):
        return [i.name for i in bag]

    def equip_stats(self):
        return [[str(i)] for i in self.equipped]

    def get_stats(self):
        return 'Str:{Str:02d} Dex:{Dex:02d} Int:{Int:02d} Wil:{Wil:02d} Per:{Per:02d}'.format(**self.stats).split()

    def get_points(self):
        return '{HP:02d} {FP:02d}'.format(**self.stats).split()
