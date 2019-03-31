import arcade
import numpy as np
import heapq
import tmx
import os
import timeit
import time
import io
from PIL import Image

rc = ROWS, COLS = (9, 16)
wh = WIDTH, HEIGHT = (64, 64)
sc = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)


list_maps = {}
array_maps = {}
current_map = 'test'
loc_array = {}
options_menu = ['Settings', 'Gameplay', 'Exit']

map_dir = [map_file for map_file in [map_file for map_file in os.listdir('./Maps') if os.path.isfile(os.path.join('./Maps', map_file))] if map_file.endswith('.tmx')]
img_dir = [img_file for img_file in os.listdir('./Images') if os.path.isfile(os.path.join('./Images', img_file))]

char_width = {' ': 24, '!': 16, '"': 32, '#': 48, '$': 32, '%': 32, '&': 48, "'": 16, '(': 24, ')': 24, '*': 32, '+': 32, ',': 16, '-': 32, '.': 16, '/': 32,
              '0': 32, '1': 32, '2': 32, '3': 32, '4': 32, '5': 32, '6': 32, '7': 32, '8': 32, '9': 32, ':': 16, ';': 16, '<':  32, '=': 32, '>': 32, '?': 32,
              '@': 48, 'A': 32, 'B': 32, 'C': 32, 'D': 32, 'E': 32, 'F': 32, 'G': 32, 'H': 32, 'I': 32, 'J': 32, 'K': 32, 'L': 32, 'M': 48, 'N': 32, 'O': 32,
              'P': 32, 'Q': 32, 'R': 32, 'S': 32, 'T': 32, 'U': 32, 'V': 32, 'W': 48, 'X': 32, 'Y': 32, 'Z': 32, '[': 24, '\\': 32, ']': 24, '^': 32, '_': 32,
              '`': 8,  'a': 32, 'b': 32, 'c': 32, 'd': 32, 'e': 32, 'f': 32, 'g': 32, 'h': 32, 'i': 16, 'j': 32, 'k': 32, 'l': 24, 'm': 48, 'n': 32, 'o': 32,
              'p': 32, 'q': 32, 'r': 32, 's': 32, 't': 32, 'u': 32, 'v': 32, 'w': 48, 'x': 32, 'y': 32, 'z': 32, '{': 32, '|': 16, '}': 32, '~': 32}

movement_keys = {
    'N':  (arcade.key.NUM_8, arcade.key.W, arcade.key.UP, arcade.key.NUM_UP),
    'NE': (arcade.key.NUM_9, arcade.key.NUM_PAGE_UP),
    'E':  (arcade.key.NUM_6, arcade.key.D, arcade.key.RIGHT, arcade.key.NUM_RIGHT),
    'SE': (arcade.key.NUM_3, arcade.key.NUM_PAGE_DOWN),
    'S':  (arcade.key.NUM_2, arcade.key.S, arcade.key.DOWN, arcade.key.NUM_DOWN),
    'SW': (arcade.key.NUM_1, arcade.key.NUM_END),
    'W':  (arcade.key.NUM_4, arcade.key.A, arcade.key.LEFT, arcade.key.NUM_4, arcade.key.NUM_LEFT),
    'NW': (arcade.key.NUM_7, arcade.key.NUM_HOME),
    'Inv': (arcade.key.E, arcade.key.TAB, arcade.key.NUM_ADD),
    'Context': (arcade.key.SPACE, arcade.key.NUM_ENTER),
    'Exit': (arcade.key.ESCAPE, ),
    'Map': (arcade.key.M, arcade.key.NUM_DECIMAL),
}

for img in img_dir:
    if '8x8' in img:
        small = Image.open('./Images/{}'.format(img))
        bigger = small.resize((small.size[0]*8, small.size[1]*8))
        bigger.save('./Images/64x64{}'.format(img.split('8x8')[1]), 'PNG')
    else:
        img_name = img.split('.')[0]
        cur_img = Image.open('./Images/{}'.format(img))
        loc_array[img_name] = [[j, i, WIDTH, HEIGHT] for i in range(0, cur_img.size[1], WIDTH) for j in range(0, cur_img.size[0], HEIGHT)]
        cur_img.close()

tile_set = arcade.draw_commands.load_textures('./Images/64x64Tile.png', loc_array['Tile'])
tile_set.insert(0, tile_set[-1])

font = arcade.draw_commands.load_textures('./Images/64x64Font.png', loc_array['Font'])


for map_name in map_dir:
    map_file = tmx.TileMap.load('./Maps/{}'.format(map_name))
    list_maps[map_name.split('.')[0]] = list(zip(*[[tile.gid for tile in layer.tiles] for layer in map_file.layers_list]))
    array_maps[map_name.split('.')[0]] = [np.array([tile.gid for tile in layer.tiles]).reshape(map_file.height, map_file.width) for layer in map_file.layers_list]


def astar(start, goal, array=array_map[current_map][0]):
    """implementation of astar algorithm, neighbors can be
    modified to allow for different movement sets."""

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
        for pos_n_1, pos_n_2 in neighbors:
            neighbor = current[0] + pos_n_1, current[1] + pos_n_2
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

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [pos_n_1[1] for pos_n_1 in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return False


def roll_dice(s='1d'):  # you might be thinking this has no reason to look so ugly, and you're right.
    d = list(map(int, s.split('d')))
    return sum(sorted(list(np.random.randint(1, d[1], d[0])))[d[-1] if len(d) > 2 else 0:]) if s != '1d' else np.random.randint(0, 1)


class Entity:
    def __init__(self, yx=(0, 0), name=None, sprite=-1):
        self.y, self.x = yx
        self.name = name
        self.sprite = sprite

    @staticmethod
    def name_list(in_list):
        try:
            return [list_element.name for list_element in in_list]
        except AttributeError:
            raise('{} does not have a name attribute'.format(in_list))


class Actor(Entity):
    def __init__(self, yx, name, sprite, disposition, target_distance):
        Entity.__init__(self, yx, name, sprite)
        self.disposition = disposition
        self.target_distance = target_distance

    def move_me(self, goal):
        if (abs(self.y-goal[0]) + abs(self.x-goal[1])) > self.target_distance:  # i only want to calculate the path tree if need be
            path = astar((self.y, self.x), goal, array_map[current_map][0])
            if path:
                self.y, self.x = path[-1]
        elif self.y == goal[0] and self.x == goal[1]:  # lazy implentation of moving AI out of the way, needs to be rewritten for different dispositions
            if array_map[current_map][0][self.y + 1, self.x]:
                self.y, self.x = self.y + 1, self.x
            if array_map[current_map][0][self.y - 1, self.x]:
                self.y, self.x = self.y - 1, self.x
            if array_map[current_map][0][self.y, self.x + 1]:
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
        return [' {} '.format(action_element) for action_element in self.actions]


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
        self.body_position = ['Chest']

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
        self.body_position = ['Left Hand', 'Right Hand']

    def __repr__(self):
        return '   {} ({})'.format(self.name, self.dmg)

    def look(self):
        return DialogItem(text='({} - {}) {} {}-Handed, crit:{}'.format(self.dmg, self.dmg_style, self.weapon_type, 'Two'*bool(self.handed-1) or 'One', self.crit_mult), speaker=self.name)


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
            working_text = text.split()
            len_line = 0
            out_lines = []
            line_data = 0
            counter = 0
            while counter < len(working_text) - 1:
                for char in working_text[counter]:
                    len_line += char_width[char] // 8
                len_line += 3  # spaces!
                if len_line > 116:  # width of the dialog box
                    out_lines.append(' '.join(working_text[line_data:counter]))
                    counter -= 1
                    len_line = 0
                    line_data = counter + 1
                counter += 1
            out_lines.append(' '.join(working_text[line_data:]))
            self.text = out_lines
        else:
            self.text = text
        self.dialog_opts = dialog_opts

    def new_opt(self, newopt):
        pass

    def __repr__(self):
        return 'Speaker: {}\nText: {}\nDialog Options: \n{}\n'.format(self.speaker, self.text, self.dialog_opts)


class Player(Entity):
    def __init__(self):
        Entity.__init__(self, yx=(71, 26), name=Player, sprite=1768)
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
        self.equipped = {'Floating Left': None, 'Left Arm': None, 'Left Weapon': None, 'Left Ring One': None, 'Left Ring Two': None,
                         'Helmet': None, 'Shoulders': None, 'Chest': None, 'Gloves': None, 'Boots': None,
                         'Floating Right': None, 'Right Arm': None, 'Right Weapon': None, 'Right Ring One': None, 'Right Ring Two': None}
        self.state = 'Walking'

    @staticmethod
    def get_bag(bag):
        return [bag_item.name for bag_item in bag]

    def equip_stats(self):
        return [[str(eqp_item)] for eqp_item in self.equipped]

    def get_stats(self):
        return 'Str:{Str:02d} Dex:{Dex:02d} Int:{Int:02d} Wil:{Wil:02d} Per:{Per:02d}'.format(**self.stats).split()

    def get_points(self):
        return '{HP:02d} {FP:02d}'.format(**self.stats).split()


test_dia = DialogItem(sprite=34, text='''
At last I have the privilege of making public this third book of Marx's main work,
the conclusion of the theoretical part. When I published the second volume, in 1885, 
I thought that except for a few, certainly very important, sections the third 
volume would probably offer only technical difficulties. This was indeed the case. 
But I had no idea at the time that these sections, the most important parts of the 
entire work, would give me as much trouble as they did, just as I did not anticipate 
the other obstacles, which were to retard completion of the work to such an extent.''',
                      speaker='Engels', yx=(73, 26), on_level='overworld')
other_test = DialogItem(sprite=456, text="got this far", speaker='Marie', yx=(73, 26), on_level='overworld')
BrokenDoor = DialogItem(sprite=345, text='Who is it?', dialog_opts={"Me": test_dia, "You": other_test}, speaker='Dick Allcocks from Man Island', yx=(73, 27), on_level='overworld')
BrDo2 = DialogItem(sprite=33,
                   dialog_opts={"What this?": BrokenDoor, "Why that?": BrokenDoor, "Who there?": BrokenDoor, "When it?": BrokenDoor},
                   speaker='Thine Momther', yx=(73, 27), on_level='overworld')


class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.last_input_time = 0
        self.cur_time = 0
        self.draw_time = 0
        self.processing_time = 0
        self.pressed_keys = self.pressed_keys
        self.cur_opt = [0, 0]
        self.opt_highlighted = False
        self.inventory_screen = 0
        self.cur_item = None
        self.cur_text = None
        self.p = Player()
        self.switch_state(new_state='Walking', new_map=current_map)
        self.actor1 = Actor(yx=(61, 26), name='Goast', sprite=909, disposition='Friendly', target_distance=1)
        self.actor2 = Actor(yx=(71, 26), name='Victor', sprite=1781, disposition='Aggressive', target_distance=6)
        self.actor_list = [self.actor1, self.actor2, BrDo2, test_dia]
        self.p.inventory = []
        self.game_step()
        self.cur_health = [icon for sublist in [[1746] * (self.p.stats['HP'] // 2), [1747] * (self.p.stats['HP'] % 2 == 1)] for icon in sublist]
        self.p.equipped = {'Floating Left': None, 'Left Arm': None, 'Left Weapon': None, 'Left Ring One': None, 'Left Ring Two': None,
                           'Helmet': None, 'Shoulders': None, 'Chest': None, 'Gloves': None, 'Boots': None,
                           'Floating Right': None, 'Right Arm': None, 'Right Weapon': None, 'Right Ring One': None, 'Right Ring Two': None}

    def draw_base(self):
        """draw the main level, including the four key layers: Background : 1, Midground : 2, Sprites, and Foreground : 3, in that order."""
        arcade.start_render()
        for row in range(ROWS):
            tile_width = WIDTH * row + 32
            for col in range(COLS):
                cur_tile = f_maps[current_map][(row + self.p.y - 4) * 16 + (col + self.p.x - 8)]
                tile_height = HEIGHT * col + 32
                for tile_layer in cur_tile:
                    if tile_layer:
                        arcade.draw_texture_rectangle(tile_height, tile_width, WIDTH, HEIGHT, tile_set[tile_layer])

    def add_sprites(self):
        np.copyto(array_map[current_map]['Sprite'], array_map[current_map]['Sprite Copy'])
        for actor in self.actor_list:
            array_map[current_map]['Sprite'][actor.y, actor.x] = actor
        array_map[current_map]['Sprite'][self.p.y, self.p.x] = self.p

    def on_draw(self):
        draw_start_time = timeit.default_timer()
        self.draw_base()

        if self.p.state is 'Talking':
            for row in range(ROWS):
                for col in range(COLS):
                    self.gen_tile_array(array_map['dialog'], r_c=(row, col), yx=(0, 0.5))
            self.gen_text(text=self.cur_text.text, speaker=self.cur_text.speaker, opts=self.cur_text.dialog_opts)

        if self.p.state is 'Inventory':
            for row in range(ROWS):
                for col in range(COLS):
                    self.gen_tile_array(array_map['inventory'][self.inventory_screen], r_c=(row, col))
            self.gen_inv()

        if self.p.state is 'Walking':
            for col in range(-(-self.p.stats['HP'] // 2)):  # weird ass way of getting how many heart containers to draw
                self.gen_lone_tile(self.cur_health[col], (0.5 + col, 8.5))
        fps = 1 / (self.draw_time + self.processing_time)
        if fps < 20:
            cur_color = arcade.color.RED
        elif fps < 60:
            cur_color = arcade.color.WHITE
        else:
            cur_color = arcade.color.GREEN
        arcade.draw_text('FPS: {}'.format(int(fps)), 20, SCREEN_HEIGHT - 80, cur_color, 16)
        self.draw_time = timeit.default_timer() - draw_start_time

    def switch_state(self, new_state, new_map=None):
        self.cur_opt = [0, 0]
        self.opt_highlighted = False
        if new_state is 'Talking':
            if self.cur_text.speaker:
                array_map['dialog'][3] = [cur_tile for cur_row in [[0], [1564], [1565] * ((len(self.cur_text.speaker)) // 2 + 1), [1566], [0] * 15] for cur_tile in cur_row][:16]
            else:
                array_map['dialog'][3] = [0] * 16
        if new_state is 'Walking':
            pass
        if new_state is 'Inventory':
            self.inventory_screen = 0
        self.p.state = new_state
        if new_map:
            array_map[new_map]['Sprite'] = np.zeros(shape=array_map[new_map][1].shape, dtype=Entity)
            array_map[new_map]['Sprite Copy'] = array_map[new_map]['Sprite'][:]

    def cursor(self, list_locs, yx):
        y, x = yx
        try:
            list_locs[self.cur_opt[0]]
        except IndexError:
            self.cur_opt = [0, 0]
        arcade.draw_texture_rectangle(x * WIDTH - 32, (y - list_locs[self.cur_opt[0]]) * HEIGHT, WIDTH, HEIGHT, tile_set[1481])

    def gen_text(self, text=None, speaker=None, opts=None, yx=(2.25, 1), len_display=3):
        y, x = yx
        if speaker:
            width_sum = 0
            for char_pos, char in enumerate(speaker):
                width_sum += char_width[speaker[char_pos-1]]
                arcade.draw_texture_rectangle(width_sum+40, 216, WIDTH, HEIGHT, font[ord(char)])
        if opts:
            if type(opts) is not list:
                opt_names = list(opts.keys())
            else:
                opt_names = opts
            if text:
                cursor_locs = np.arange(len(text), len(text) + len(opt_names))
            else:
                cursor_locs = np.arange(0, len(opt_names))
            for item_pos, item in enumerate(opt_names[self.cur_opt[1]:self.cur_opt[1] + len_display]):
                width_sum = 0
                for char_pos, char in enumerate(item):
                    width_sum += char_width[item[char_pos - 1]]
                    arcade.draw_texture_rectangle(width_sum + x * WIDTH, (y - item_pos - int(text is not None)) * HEIGHT, WIDTH, HEIGHT, font[ord(char)])
            self.cursor(cursor_locs, yx)
        if text:
            for line_pos, line in enumerate(text[self.cur_opt[1]:self.cur_opt[1]+len_display]):
                width_sum = 0
                for char_pos, char in enumerate(text[line_pos + self.cur_opt[1]]):
                    width_sum += char_width[text[line_pos + self.cur_opt[1]][char_pos - 1]]
                    arcade.draw_texture_rectangle(width_sum + (x * WIDTH), ((y - line_pos) * HEIGHT), WIDTH, HEIGHT, font[ord(char)])

    def gen_inv(self):
        for icon in range(4):
            self.gen_lone_tile(icon+1821, (2.5 + icon * 2, 8))  # icons for menu tabs

        if self.inventory_screen == 0:
            for cur_item in range(len(self.p.inventory[self.cur_opt[1]:self.cur_opt[1] + 6 or -1])):
                self.gen_lone_tile(self.p.inventory[cur_item + self.cur_opt[1]].sprite, yx=(2, 6.5 - cur_item))
            if not self.opt_highlighted:
                self.gen_text(opts=['  {}'.format(cur_item) for cur_item in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
            else:
                self.gen_text(text=['  {}'.format(cur_item) for cur_item in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()  # this is disgusting

        elif self.inventory_screen == 1:
            for item_pos, cur_item in enumerate(list(self.p.equipped.keys())):
                if self.p.equipped[cur_item] is not None:
                    self.gen_lone_tile(self.p.equipped[cur_item].sprite, yx=(2 + item_pos // 5, 6 - item_pos % 5))
            if not self.opt_highlighted:
                self.gen_lone_tile(1906, yx=(2 + self.cur_opt[0] // 5, 6 - self.cur_opt[0] % 5))
                if self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]] is not None:
                    self.gen_text(text=[self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]].name], yx=(6.5, 5.5))
            else:
                self.gen_text(text=self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]].actions, yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()
        elif self.inventory_screen == 2:
            self.gen_text(text=self.p.get_stats(), yx=(6.5, 1), len_display=6)
        elif self.inventory_screen == 3:
            self.gen_text(opts=options_menu, yx=(6.5, 2))

    def gen_sub_menu(self):
        '''for cur_pos, cur_tile in enumerate(f_maps['submenu']):
            self.gen_lone_tile(cur_tile, (10 + cur_pos % 4, 2.5 + cur_pos // 4))'''
        for x, row in enumerate(array_map['submenu']):
            for y, col in enumerate(row):
                self.gen_tile_array(array_map['submenu'], (x, y), yx=(10, 2.5))
        self.gen_text(opts=self.cur_item.get_actions(), yx=(6, 11))

    @staticmethod
    def gen_tile_array(in_array, r_c, yx=(0, 0)):
        row, col = r_c
        y, x = yx
        arcade.draw_texture_rectangle(HEIGHT * (y + col), WIDTH * (x + row), WIDTH, HEIGHT, tile_set[in_array[r_c]])

    @staticmethod
    def gen_lone_tile(in_tile, yx, base_img=None):
        if not base_img:
            base_img = tile_set
        y, x = yx
        arcade.draw_texture_rectangle(HEIGHT * y, WIDTH * x, WIDTH, HEIGHT, base_img[in_tile])

    def on_key_press(self, key, modifiers):
        if self.p.state is 'Inventory':
            if key in movement_keys['NW'] and self.inventory_screen > 0:
                self.cur_opt = [0, 0]
                self.inventory_screen -= 1
            if key in movement_keys['NE'] and self.inventory_screen < 3:
                self.cur_opt = [0, 0]
                self.inventory_screen += 1
            if key in movement_keys['Inv']:
                if self.opt_highlighted:
                    self.opt_highlighted = False
                else:
                    self.switch_state('Walking')

            if self.inventory_screen == 0:
                if key in movement_keys['S']:
                    if self.opt_highlighted:
                        self.cur_opt[0] += 1
                    else:
                        if self.cur_opt[0] < 5:
                            self.cur_opt[0] += 1
                        elif sum(self.cur_opt) + 1 < len(self.p.inventory):
                            self.cur_opt[1] += 1
                if key in movement_keys['N']:
                    if self.cur_opt[0] > 0:
                        self.cur_opt[0] -= 1
                    elif self.cur_opt[1] > 0:
                        self.cur_opt[1] -= 1
                if key in movement_keys['Context']:
                    if self.opt_highlighted:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[0]])
                        self.opt_highlighted = False
                    else:
                        self.cur_item = self.p.inventory[sum(self.cur_opt)]
                        self.opt_highlighted = True

            if self.inventory_screen == 1:
                if key in movement_keys['S'] and self.cur_opt[0] < 14:
                    self.cur_opt[0] += 1
                if key in movement_keys['N'] and self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1
                if key in movement_keys['E'] and self.cur_opt[0] < 10:
                    self.cur_opt[0] += 5
                if key in movement_keys['W'] and self.cur_opt[0] > 4:
                    self.cur_opt[0] -= 5
                if key in movement_keys['Context']:
                    if self.opt_highlighted:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[0]])
                        self.opt_highlighted = False
                    else:
                        self.cur_item = self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]].name
                        self.opt_highlighted = True
            if self.inventory_screen == 2:
                pass
            if self.inventory_screen == 3:
                if key in movement_keys['Context']:
                    if 'Settings' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
                    if 'Gameplay' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
                    if 'Exit' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
                if key in movement_keys['S'] and self.cur_opt[0] < 3:
                    self.cur_opt[0] += 1
                if key in movement_keys['N'] and self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1

        elif self.p.state is 'Walking':
            if key in movement_keys['Inv']:
                self.switch_state('Inventory')
            if key in movement_keys['Context']:
                if type(array_map[current_map]['Sprite'][self.p.y + 1, self.p.x]) is DialogItem:
                    self.cur_text = array_map[current_map]['Sprite'][self.p.y + 1, self.p.x]
                    self.switch_state('Talking')

        elif self.p.state is 'Talking':
            if key in movement_keys['N']:
                if self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1
                elif self.cur_opt[1] > 0:
                    self.cur_opt[1] -= 1
            if key in movement_keys['S']:
                if self.cur_opt[0] < 2:
                    self.cur_opt[0] += 1
                elif sum(self.cur_opt) < len(self.cur_text.dialog_opts) - 1:
                    self.cur_opt[1] += 1
            if key in movement_keys['Context']:
                if self.cur_text.dialog_opts:
                    array_map[current_map]['Sprite'][self.p.y + 1, self.p.x] = self.cur_text.dialog_opts[list(self.cur_text.dialog_opts)[sum(self.cur_opt)]]
                    self.whatsnextifier(choice=self.cur_text.dialog_opts[list(self.cur_text.dialog_opts)[sum(self.cur_opt)]])
                    self.switch_state('Talking')
                    print(array_map[current_map]['Sprite'][self.p.y + 1, self.p.x])
                elif len(self.cur_text.text) > 3:
                    if len(self.cur_text.text) - 2 > self.cur_opt[1]:
                        self.cur_opt[1] += 1
                    else:
                        self.switch_state('Walking')

        if key in movement_keys['Exit']:
            if self.p.state is 'Inventory' and self.opt_highlighted:
                self.opt_highlighted = False
            elif self.p.state is not 'Walking':
                self.switch_state('Walking')
            else:
                self.switch_state('Inventory')
                self.inventory_screen = 3

    def on_mouse_press(self, x: float, y: float, dx: float, dy: float):
        print(x, y)

    def update(self, delta_time: float):
        start_time = timeit.default_timer()
        if self.p.state is 'Walking' and self.pressed_keys:
            self.cur_time = time.process_time()
            if self.cur_time - self.last_input_time > 0.05:
                if any(key in movement_keys['N'] for key in self.pressed_keys):
                    # if array_map[current_map][0][self.p.y + 1, self.p.x] == 0:
                        self.p.y += 1
                        self.game_step()
                if any(key in movement_keys['S'] for key in self.pressed_keys):
                    # if array_map[current_map][0][self.p.y - 1, self.p.x] == 0:
                        self.p.y -= 1
                        self.game_step()
                if any(key in movement_keys['E'] for key in self.pressed_keys):
                    # if array_map[current_map][0][self.p.y, self.p.x + 1] == 0:
                        self.p.x += 1
                        self.game_step()
                if any(key in movement_keys['W'] for key in self.pressed_keys):
                    # if array_map[current_map][0][self.p.y, self.p.x - 1] == 0:
                        self.p.x -= 1
                        self.game_step()
                if any(key in movement_keys['NE'] for key in self.pressed_keys):
                    if array_map[current_map][0][self.p.y + 1, self.p.x + 1] == 0:
                        self.p.x += 1
                        self.p.y += 1
                        self.game_step()
                if any(key in movement_keys['NW'] for key in self.pressed_keys):
                    if array_map[current_map][0][self.p.y - 1, self.p.x + 1] == 0:
                        self.p.x -= 1
                        self.p.y += 1
                        self.game_step()
                if any(key in movement_keys['SE'] for key in self.pressed_keys):
                    if array_map[current_map][0][self.p.y + 1, self.p.x - 1] == 0:
                        self.p.x += 1
                        self.p.y -= 1
                        self.game_step()
                if any(key in movement_keys['SW'] for key in self.pressed_keys):
                    if array_map[current_map][0][self.p.y - 1, self.p.x - 1] == 0:
                        self.p.x -= 1
                        self.p.y -= 1
                        self.game_step()
                self.last_input_time = self.cur_time
        self.processing_time = timeit.default_timer() - start_time

    def interact_item(self, item, action):
        if action is 'Equip':
            if item in self.p.inventory:
                self.p.inventory.remove(item)
                for possible_pos in item.body_position:
                    if self.p.equipped[possible_pos] is None:
                        self.p.equipped[possible_pos] = item
            else:  # the item is equipped
                self.p.inventory.append(item)
        if action is 'Look':
            self.cur_text = item.look()
            self.switch_state('Talking')
        if action is 'Drop':
            self.p.inventory.remove(item)

    def whatsnextifier(self, choice):
        array_map[current_map]['Sprite'][self.p.y+1, self.p.x] = choice
        self.cur_text = array_map[current_map]['Sprite'][self.p.y + 1, self.p.x]

    def game_step(self):
            self.add_sprites()
            cur_health = [item for sublist in [[1745] * (self.p.stats['HP'] // 2), [1746] * (self.p.stats['HP'] % 2 == 1)] for item in sublist]
            actor_list = [cur_act for cur_act in self.actor_list if hasattr(cur_act, 'disposition')]
            enemy_list = [enemy for enemy in actor_list if enemy.disposition is 'Aggressive']
            for actor in actor_list:
                if actor.disposition is 'Friendly':
                    if enemy_list:
                        actor.move_me((enemy_list[0].y, enemy_list[0].x))
                    else:
                        actor.move_me((self.p.y, self.p.x))
                elif actor.disposition is 'Aggressive':
                    actor.move_me((self.p.y, self.p.x))


def main():
    Game(*sc)
    arcade.run()


if __name__ == '__main__':
    main()
