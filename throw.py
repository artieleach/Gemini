import arcade
import numpy as np
import heapq
import tmx
import os
import timeit
from functools import lru_cache
from PIL import Image

RC = ROWS, COLS = (9, 16)
WH = WIDTH, HEIGHT = (64, 64)
SC = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)

list_maps = {}
array_maps = {}

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

tile_locs = {}
for img in img_dir:
    if '8x8' in img:
        small = Image.open('./Images/{}'.format(img))
        bigger = small.resize((small.size[0]*8, small.size[1]*8))
        bigger.save('./Images/64x64{}'.format(img.split('8x8')[1]), 'PNG')
    else:
        img_name = img.split('.')[0]
        cur_img = Image.open('./Images/{}'.format(img))
        tile_locs[img_name] = [[j, i, WIDTH, HEIGHT] for i in range(0, cur_img.size[1], WIDTH) for j in range(0, cur_img.size[0], HEIGHT)]
        cur_img.close()

tile_set = arcade.draw_commands.load_textures('./Images/64x64Tile.png', tile_locs['Tile'])
tile_set.insert(0, tile_set[-1])

font = arcade.draw_commands.load_textures('./Images/64x64Font.png', tile_locs['Font'])

for map_name in map_dir:
    map_file = tmx.TileMap.load('./Maps/{}'.format(map_name))
    raw_map = [x[::-1] for x in [[tile.gid for tile in layer.tiles] for layer in map_file.layers_list]]
    array_maps[map_name.split('.')[0]] = [np.flip(np.array(map_l, dtype=int).reshape((map_file.height, map_file.width)), 1) for map_l in raw_map]  # awway_maps['map'][layer #][x, y]
    list_maps[map_name.split('.')[0]] = list(zip(*[arr_layer.flatten() for arr_layer in array_maps[map_name.split('.')[0]]]))

def astar(start, goal, array):
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

    def name_list(self, in_list):
        return [list_element.name for list_element in in_list]

class Actor(Entity):
    def __init__(self, yx, name, sprite, disposition, target_distance):
        super().__init__(yx, name, sprite)
        self.disposition = disposition
        self.target_distance = target_distance

    def move_me(self, goal):
        if (abs(self.y-goal[0]) + abs(self.x-goal[1])) > self.target_distance:  # i only want to calculate the path tree if need be
            path = astar((self.y, self.x), goal, array_maps[Game.current_map][0])
            if path:
                self.y, self.x = path[-1]
        elif self.y == goal[0] and self.x == goal[1]:
            for pos_pos in [a for a in [(i, j) for i in [-1, 0, 1] for j in [-1, 0, 1]] if a != (0, 0)]:
                if array_maps[Game.current_map][0][pos_pos]:
                    self.y, self.x = self.y + pos_pos[0], self.x + pos_pos[1]

class Item(Entity):
    def __init__(self, name, cost, weight, sprite, flavor_text=None):
        super().__init__(name, sprite)
        self.cost = cost
        self.weight = weight
        self.flavor_text = flavor_text
        self.actions = ['Look', 'Drop']

    def look(self):
        return DialogItem(text=self.flavor_text, speaker=self.name)

    def get_actions(self):
        return [' {} '.format(action_element) for action_element in self.actions]

class EquipmentItem(Item):
    def __init__(self, name, cost, weight, sprite, body_pos):
        super().__init__(name, cost, weight, sprite)
        self.actions.append('Equip')
        self.body_pos = body_pos


class DialogItem(Entity):  # create a generator upon level creation for these
    def __init__(self, text=None, speaker=None, dialog_opts=None, yx=(0, 0), sprite=-1):
        super().__init__(yx, sprite)
        self.speaker = speaker
        self.dialog_opts = dialog_opts
        if type(text) is str:  # listen... just... just leave it.
            working_text = text.split()
            len_line = 0
            out_lines = []
            line_data = 0
            counter = 0
            while counter < len(working_text) - 1:
                for char in working_text[counter]:
                    len_line += char_width[char] // 8
                len_line += 3  # add 3 pixels of space for spaces after each word
                if 116 < len_line:  # width of the dialog box
                    out_lines.append(' '.join(working_text[line_data:counter]))
                    counter -= 1
                    len_line = 0
                    line_data = counter + 1
                counter += 1
            out_lines.append(' '.join(working_text[line_data:]))
            self.text = out_lines
        else:
            self.text = text

    def __repr__(self):
        return 'Speaker: {}\nText: {}\nDialog Options: \n{}\n'.format(self.speaker, self.text, self.dialog_opts)

class Player(Entity):
    def __init__(self):
        super().__init__(yx=(71, 26), sprite=1768)
        self.inventory = []


class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.current_map = 'test'
        self.state = 'Walking'
        self.p = Player()
        self.cur_time = 0
        self.draw_time = 0
        self.processing_time = 0

    def switch_state(self, new_state, new_map):
        self.state = new_state
        self.current_map = new_map


    def draw_command(self):
        for row in range(ROWS):
            for col in range(COLS):
                for layer in [0, 1, 2]:
                    arcade.draw_texture_rectangle(*self.draw_base(row, col, layer, self.p.x, self.p.y))

    @lru_cache(None)
    def draw_base(self, row, col, layer, px, py):
        tile_x = WIDTH * row + 32
        tile_y = HEIGHT * col + 32
        tile_layer = list_maps[self.current_map][(row + py - 4) * 200 + (col + px - 8)][1:]
        return tile_y, tile_x, WIDTH, HEIGHT, tile_set[tile_layer[layer]]


    def on_draw(self):
        draw_start_time = timeit.default_timer()
        arcade.start_render()
        self.draw_command()
        try:
            fps = 1 / (self.draw_time + self.processing_time)
        except ZeroDivisionError:
            fps = 0
        self.draw_time = timeit.default_timer() - draw_start_time
        if fps < 20:
            cur_color = arcade.color.RED
        elif fps < 60:
            cur_color = arcade.color.WHITE
        else:
            cur_color = arcade.color.GREEN
        arcade.draw_text('FPS: {}'.format(int(fps)), 20, SCREEN_HEIGHT - 80, cur_color, 16)

    def update(self, delta_time: float):
        if self.state is 'Walking' and self.pressed_keys:
            if any(key in movement_keys['N'] for key in self.pressed_keys):
                self.p.y += 1
            if any(key in movement_keys['S'] for key in self.pressed_keys):
                self.p.y -= 1
            if any(key in movement_keys['E'] for key in self.pressed_keys):
                self.p.x += 1
            if any(key in movement_keys['W'] for key in self.pressed_keys):
                self.p.x -= 1
            if any(key in movement_keys['Exit'] for key in self.pressed_keys):
                Game.close(self)


def main():
    Game(*SC)
    arcade.run()


if __name__ == '__main__':
    main()
