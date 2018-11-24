import arcade
import numpy as np
import heapq
import tmx
import os
from PIL import Image
import timeit


rc = ROWS, COLS = (9, 16)
wh = WIDTH, HEIGHT = (64, 64)
sc = SCREEN_WIDTH, SCREEN_HEIGHT = (WIDTH * COLS, HEIGHT * ROWS)
wait_time = 0.01

current_map = 'overworld'
raw_maps = {}
loc_array = {}
options_menu = ['Settings', 'Gameplay', 'Exit']

map_dir = [f for f in os.listdir('./Maps') if os.path.isfile(os.path.join('./Maps', f))]
img_dir = [f for f in os.listdir('./Images') if os.path.isfile(os.path.join('./Images', f))]

char_width = {' ': 24, '!': 16, '"': 32, '#': 48, '$': 32, '%': 32, '&': 48, "'": 16, '(': 24, ')': 24, '*': 32, '+': 32, ',': 16, '-': 32, '.': 16, '/': 32,
              '0': 32, '1': 32, '2': 32, '3': 32, '4': 32, '5': 32, '6': 32, '7': 32, '8': 32, '9': 32, ':': 16, ';': 16, '<':  32, '=': 32, '>': 32, '?': 32,
              '@': 48, 'A': 32, 'B': 32, 'C': 32, 'D': 32, 'E': 32, 'F': 32, 'G': 32, 'H': 32, 'I': 32, 'J': 32, 'K': 32, 'L': 32, 'M': 48, 'N': 32, 'O': 32,
              'P': 32, 'Q': 32, 'R': 32, 'S': 32, 'T': 32, 'U': 32, 'V': 32, 'W': 48, 'X': 32, 'Y': 32, 'Z': 32, '[': 24, '\\': 32, ']': 24, '^': 32, '_': 32,
              '`': 8,  'a': 32, 'b': 32, 'c': 32, 'd': 32, 'e': 32, 'f': 32, 'g': 32, 'h': 32, 'i': 16, 'j': 32, 'k': 32, 'l': 24, 'm': 48, 'n': 32, 'o': 32,
              'p': 32, 'q': 32, 'r': 32, 's': 32, 't': 32, 'u': 32, 'v': 32, 'w': 48, 'x': 32, 'y': 32, 'z': 32, '{': 32, '|': 16, '}': 32, '~': 32}

istransparent = []
for img in img_dir:
    if '8x8' in img:
        small = Image.open('./Images/{}'.format(img))
        bigger = small.resize((small.size[0]*8, small.size[1]*8))
        bigger.save('./Images/64x64{}'.format(img.split('8x8')[1]), 'PNG')
        if 'Tile' in img:
            for i in range((small.size[0]-1) // 8):
                for j in range((small.size[1]-1) // 8):
                    tile_to_check = small.crop(box=(i*8, j*8, (i+1)*8, (j+1)*8))
                    # tile_to_check.save('./Throw/{},{}_{}'.format(i, j, 00 in tile_to_check.tobytes()), 'PNG')
                    istransparent.append(00 in tile_to_check.tobytes())
    else:
        img_name = img.split('.')[0]
        cur_img = Image.open('./Images/{}'.format(img))
        loc_array[img_name] = [[j, i, WIDTH, HEIGHT] for i in range(0, cur_img.size[1], WIDTH) for j in range(0, cur_img.size[0], HEIGHT)]
        cur_img.close()

try:
    tile_set = arcade.draw_commands.load_textures('./Images/64x64Tile.png', loc_array['Tile'])
    font = arcade.draw_commands.load_textures('./Images/64x64Font.png', loc_array['Font'])
    tile_set.insert(0, tile_set[-1])
except KeyError:
    raise 'Damn it Artie you didnt fix the tile problem. \nAnyway, run this again and it should work, it was trying to grab an image before it was finished rendering.'

movement_keys = {
    'N': (arcade.key.W, arcade.key.UP, arcade.key.NUM_8, arcade.key.NUM_UP),
    'S': (arcade.key.S, arcade.key.DOWN, arcade.key.NUM_2, arcade.key.NUM_DOWN),
    'W': (arcade.key.A, arcade.key.LEFT, arcade.key.NUM_4, arcade.key.NUM_LEFT),
    'E': (arcade.key.D, arcade.key.RIGHT, arcade.key.NUM_6, arcade.key.NUM_RIGHT),
    'Inv': (arcade.key.E, arcade.key.TAB, arcade.key.NUM_ADD),
    'Context': (arcade.key.SPACE, arcade.key.NUM_ENTER),
    'Exit': (arcade.key.ESCAPE, ),
    'Map': (arcade.key.M, arcade.key.NUM_DECIMAL),
    'NE': (arcade.key.NUM_9, arcade.key.NUM_PAGE_UP),
    'NW': (arcade.key.NUM_7, arcade.key.NUM_HOME),
    'SE': (arcade.key.NUM_3, arcade.key.NUM_PAGE_DOWN),
    'SW': (arcade.key.NUM_1, arcade.key.NUM_END),
}

