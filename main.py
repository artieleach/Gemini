import time
from custom_classes import *


class GameTest(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.grid = np.zeros(wh, dtype=int)
        self.pressed_keys = self.pressed_keys  # i don't know why i need this, but pycharm wants it.
        self.state = 'Walking'  # walking, talking, and inventory.
        self.selected = False  # true if an item/option is selected
        self.cur_opt = [0, 0, 0]  # X, Y, starting Index
        self.inventory_screen = 0  # 0=inv, 1=eqp, 2=stats, 3=opt
        self.cur_text = None
        self.cur_item = None
        self.p = Player()
        self.actor1 = Actor(yx=(26, 70), sprite=908, disposition=2, target=(self.p.y, self.p.x))
        self.actor_list = []
        self.actor_list.append(self.actor1)

    def on_draw(self):
        arcade.start_render()
        for row in range(ROWS):
            for col in range(COLS + 1):
                self.draw_map(raw_maps[current_map]['Back'], row, col)
                self.draw_map(raw_maps[current_map]['Mid'], row, col)
                if col == 8 and row == 4:
                    self.draw_p((16, 9))
                self.draw_map(raw_maps[current_map]['Fore'], row, col)
                if self.state == 'Talking':
                    if self.cur_text.speaker:
                        raw_maps['dialog'][3] = [i for s in [[0], [1563], [1564] * ((len(self.cur_text.speaker)) // 2 - 1), [1565], [-1] * 15] for i in s][:16]
                    else:
                        raw_maps['dialog'][3] = [0] * 16
                if self.state is 'Inventory':
                    self.gen_tile(raw_maps['inventory'][self.inventory_screen], r_c=(row, col - 1), yx=(0.5, 0.5))
        if self.state is 'Talking':
            for row in range(4):
                for col in range(16):
                    self.gen_tile(raw_maps['dialog'], (row, col), yx=(0, 0.5))
            self.gen_text(txt=self.cur_text.text, speaker=self.cur_text.speaker, opts=self.cur_text.dialog_opts)
        if self.state is 'Inventory':
            self.gen_inv()
        cur_health = [item for sublist in [[1745]*(self.p.stats['HP'] // 2), [1746]*(self.p.stats['HP'] % 2 == 1)] for item in sublist]
        for row in range(-(-self.p.stats['HP'] // 2)):
            self.gen_tile([cur_health[row]], (0.5+row, 8.5))

    def cursor(self, list_locs):
        try:
            list_locs[self.cur_opt[1], self.cur_opt[0]]
        except IndexError:
            self.cur_opt = [0, 0, 0]
        highlight = list_locs[self.cur_opt[1], self.cur_opt[0]]
        arcade.draw_texture_rectangle(highlight[0] * FONT_WIDTH, highlight[1]*64+32, 64, 64, font[ord('>')])

    def gen_text(self, txt=None, speaker=None, opts=None, yx=(2.5, 2)):
        y, x = yx
        if speaker:
            for my_pos, char in enumerate(speaker):
                arcade.draw_texture_rectangle((my_pos+3) * FONT_WIDTH, 224, 64, 64, font[ord(char)])
        if opts:
            cursor_locs = np.zeros((len(opts), len(opts[0]), 2), dtype=int)
            for itempos, item in enumerate(opts):
                for optpos, sub in enumerate(item):
                    cursor_locs[itempos, optpos] = [x + len(''.join(opts[itempos][:optpos])), y - itempos - int(txt is not None)]
                    out = ''.join(opts[itempos])
                    for charpos, char in enumerate(out):
                        arcade.draw_texture_rectangle((charpos + x) * FONT_WIDTH, (y - itempos - int(txt is not None)) * 64, 64, 64, font[ord(char)])
            self.cursor(cursor_locs)
        if txt:
            for linepos, line in enumerate(txt[self.cur_opt[2]:self.cur_opt[2] + 3]):
                for charpos, char in enumerate(txt[linepos + self.cur_opt[2]]):
                    arcade.draw_texture_rectangle((charpos + x) * FONT_WIDTH, ((y - linepos) * 64), 64, 64, font[ord(char)])

    def gen_inv(self):
        self.draw_p((5, 13))
        self.gen_text([['Wares Eqp Lvl Opt', 'Wrs Eqpd Lvl Opt',
                        'Wrs Eqp Lvls Opt', 'Wrs Eqp Lvl Optn'][self.inventory_screen]], yx=(7.5, 9))
        self.gen_text(txt=self.p.get_points(), yx=(3, 2))
        self.gen_text(txt=['{:03d}'.format(self.p.stats['XP'])], yx=(5.5, 2.5))
        if self.inventory_screen == 0:
            for i in range(len(self.p.inventory[self.cur_opt[2]:self.cur_opt[2] + 6 or -1])):
                try:
                    self.gen_tile([self.p.inventory[i + self.cur_opt[2]].texture], yx=(6.5 - i, 6))
                except IndexError:
                    pass
            if not self.selected:
                self.gen_text(opts=self.p.get_bag(self.p.inventory)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6.5, 9))
            else:
                self.gen_text(txt=self.p.get_bag(self.p.inventory, False)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6.5, 11))
                self.gen_sub_menu()
        elif self.inventory_screen == 1:
            for i in range(len(self.p.equipped[self.cur_opt[2]:self.cur_opt[2] + 6 or -1])):
                self.gen_tile([self.p.equipped[i + self.cur_opt[2]].texture], yx=(6.5 - i, 6))
            if not self.selected:
                self.gen_text(opts=self.p.equip_stats()[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6.5, 13))
            else:
                self.gen_text(txt=self.p.get_bag(self.p.equipped, False)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6.5, 16))
                self.gen_sub_menu()
        elif self.inventory_screen == 2:
            self.gen_text(self.p.get_stats(), yx=(6.5, 13))
        else:
            self.gen_text(opts=([' Options'], [' Settings'], [' Exit']), yx=(6.5, 13))

    def gen_sub_menu(self):
        for x, row in enumerate(raw_maps['submenu']):
            for y, col in enumerate(row):
                self.gen_tile(raw_maps['submenu'], (x, y), yx=(11, 2.5))
        self.gen_text(opts=self.cur_item.get_actions(), yx=(5.5, 18))
    
    def draw_map(self, inmap, row, col):
        arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT,
                                      tile_set[inmap[row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]])

    def gen_tile(self, in_array=None, r_c=(0, 0), yx=(0, 0)):
        row, col = r_c
        y, x = yx
        if len(in_array) > 1:
            arcade.draw_texture_rectangle(HEIGHT * (y + col), WIDTH * (x + row), WIDTH, HEIGHT, tile_set[in_array[r_c]])
        else:
            arcade.draw_texture_rectangle(WIDTH * (x + row), (HEIGHT * (y + col)), WIDTH, HEIGHT, tile_set[in_array[0]])

    def on_key_press(self, key, modifiers):
        if self.state is 'Inventory':
            if key in movemnet_keys['Left'] and self.inventory_screen > 0:
                self.cur_opt = [0, 0, 0]
                self.inventory_screen -= 1
            if key in movemnet_keys['Right'] and self.inventory_screen < 3:
                self.cur_opt = [0, 0, 0]
                self.inventory_screen += 1
            if key in movemnet_keys['Down']:
                if self.selected:
                    self.cur_opt[1] += 1
                else:
                    if self.cur_opt[1] < 5:
                        self.cur_opt[1] += 1
                    elif sum(self.cur_opt) + 1 < len(self.p.inventory):
                        self.cur_opt[2] += 1
            if key in movemnet_keys['Up']:
                if self.cur_opt[1] > 0:
                    self.cur_opt[1] -= 1
                elif self.cur_opt[2] > 0:
                    self.cur_opt[2] -= 1
            if key in movemnet_keys['Inv']:
                if self.selected:
                    self.selected = False
                else:
                    self.state = 'Walking'
            if key in movemnet_keys['Context']:
                if self.inventory_screen == 0:
                    if not self.selected:
                        self.cur_item = self.p.inventory[sum(self.cur_opt)]
                    else:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[1]])
                    self.cur_opt = [0, 0, 0]
                    self.selected = not self.selected
                elif self.inventory_screen == 1:
                    if self.selected:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[1]])
                    else:
                        self.cur_item = self.p.equipped[sum(self.cur_opt)]
                    self.cur_opt = [0, 0, 0]
                    self.selected = not self.selected
        elif self.state is 'Walking':
            if key in movemnet_keys['Inv']:
                self.cur_opt = [0, 0, 0]
                self.state = 'Inventory'
                self.inventory_screen = 0
            if key in movemnet_keys['Context']:
                if raw_maps[current_map]['Collision'][self.p.y+1, self.p.x] in nodes:
                    self.cur_opt = [0, 0, 0]
                    self.cur_text = nodes[raw_maps[current_map]['Collision'][self.p.y+1, self.p.x]]
                    self.state = 'Talking'
                # elif floor_map[self.p.y, self.p.x]:
                    # self.p.inventory.append(floor_map[self.p.y, self.p.x])
        elif self.state is 'Talking':
            if self.cur_text.dialog_opts:
                if key in movemnet_keys['Right'] and self.cur_opt[0] < len(self.cur_text.dialog_opts):
                    self.cur_opt[0] += 1
                if key in movemnet_keys['Left'] and self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1
                if key in movemnet_keys['Up'] and self.cur_opt[1] > 0:
                    self.cur_opt[1] -= 1
                if key in movemnet_keys['Down'] and self.cur_opt[1] < len(self.cur_text.dialog_opts)-1:
                    self.cur_opt[1] += 1
                if key in movemnet_keys['Context']:
                    print(self.cur_text.dialog_opts[self.cur_opt[1]][self.cur_opt[0]])
            if key in movemnet_keys['Context']:
                if self.cur_opt[2] < len(self.cur_text.text) - 2:
                    self.cur_opt[2] += 1
                else:
                    self.state = 'Walking'
            if key in movemnet_keys['Inv']:
                self.state = 'Walking'
        if key in movemnet_keys['Exit']:
            if self.state is 'Inventory' and self.selected:
                self.selected = False
            elif self.state is not 'Walking':
                self.state = 'Walking'
            else:
                self.close()
        if key in movemnet_keys['Map']:
            for act in self.actor_list:
                act.move_me((self.p.y, self.p.x))
        if key == arcade.key.H:
            self.p.stats['HP'] += 1
        if key == arcade.key.N:
            self.p.stats['HP'] -= 1

    def update(self, delta_time: float):
        if self.state is 'Walking':
            if any(key in movemnet_keys['Up'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x] == 0:
                    self.p.y += 1
                    for act in self.actor_list:
                        act.move_me((self.p.y, self.p.x))
                elif raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x] < 0:
                    self.p.y += 1
                    for act in self.actor_list:
                        if act.x == self.p.x and act.y == self.p.y:
                            act.move_me((act.y-1, act.x), False)
            if any(key in movemnet_keys['Down'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x] == 0:
                    self.p.y -= 1
                    for act in self.actor_list:
                        act.move_me((self.p.y, self.p.x))
                    time.sleep(wait_time)
                elif raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x] < 0:
                    self.p.y -= 1
                    for act in self.actor_list:
                        if act.x == self.p.x and act.y == self.p.y:
                            act.move_me((act.y+1, act.x), False)
                            time.sleep(wait_time)
            if any(key in movemnet_keys['Right'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x + 1] == 0:
                    self.p.x += 1
                    for act in self.actor_list:
                        act.move_me((self.p.y, self.p.x))
                    time.sleep(wait_time)
                elif raw_maps[current_map]['Collision'][self.p.y, self.p.x + 1] < 0:
                    self.p.x += 1
                    for act in self.actor_list:
                        if act.x == self.p.x and act.y == self.p.y:
                            act.move_me((act.y, act.x-1), False)
                            time.sleep(wait_time)
            if any(key in movemnet_keys['Left'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x - 1] == 0:
                    self.p.x -= 1
                    for act in self.actor_list:
                        act.move_me((self.p.y, self.p.x))
                    time.sleep(wait_time)
                elif raw_maps[current_map]['Collision'][self.p.y, self.p.x - 1] < 0:
                    self.p.x -= 1
                    for act in self.actor_list:
                        if act.x == self.p.x and act.y == self.p.y:
                            act.move_me((act.y, act.x+1), False)
                            time.sleep(wait_time)

    def interact_item(self, item, action):
        if action == 'Equip':
            if item in self.p.inventory:
                self.p.inventory.remove(item)
                if type(item) is Armor:
                    self.p.equipped.insert(0, item)
                else:
                    self.p.equipped.insert(-1, item)
            else:
                self.p.equipped.remove(item)
                self.p.inventory.append(item)
        elif action == 'Look':
            self.cur_text = DialogItem(item.look())
            self.state = 'Talking'
        elif action == 'Drop':
            if item in self.p.inventory:
                self.p.inventory.remove(item)
            else:
                self.p.equipped.remove(item)
            # floor_map[self.p.y, self.p.x] = item

    def draw_p(self, yx=(0, 0)):
        y, x = yx
        arcade.draw_texture_rectangle(y * 32, x * 32, WIDTH, HEIGHT, self.p.appearance)


def main():
    GameTest(*sc)
    arcade.run()


if __name__ == '__main__':
    main()
