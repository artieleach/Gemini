from custom_classes import *


class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pressed_keys = self.pressed_keys  # i don't know why i need this, but pycharm wants it
        self.selected = False  # true if an item/option is selected
        self.cur_opt = [0, 0, 0]  # X, Y, starting Index
        self.inventory_screen = 0  # 0=inv, 1=eqp, 2=stats, 3=opt
        self.cur_text = None
        self.cur_item = None
        self.p = Player()
        self.actor1 = Actor(yx=(61, 26), sprite=908, disposition='Friendly', target_distance=1)
        self.actor2 = Actor(yx=(71, 26), sprite=1780, disposition='Aggressive', target_distance=1)
        self.actor_list = [self.actor1]

    def draw_base(self):
        arcade.start_render()
        for row in range(ROWS):
            for col in range(COLS+1):
                self.draw_map(raw_maps[current_map]['Back'], row, col)
                self.draw_map(raw_maps[current_map]['Mid'], row, col)
                self.draw_p()
                if raw_maps[current_map]['Sprite'][row, col]:
                    self.draw_map(raw_maps[current_map]['Sprite'], row, col)
                self.draw_map(raw_maps[current_map]['Fore'], row, col)

    def on_draw(self):
        arcade.start_render()
        self.draw_base()
        if self.p.state is 'Talking':
            if self.cur_text.speaker:
                raw_maps['dialog'][3] = [i for s in [[0], [1563], [1564] * ((len(self.cur_text.speaker)) // 2 + 1), [1565], [-1] * 15] for i in s][:16]
            else:
                raw_maps['dialog'][3] = [-1] * 16
        for row in range(ROWS):
            for col in range(COLS + 1):
                if self.p.state == 'Talking':
                    self.gen_tile(raw_maps['dialog'], r_c=(row, col-1), yx=(0, 0.5))
                if self.p.state is 'Inventory':
                    self.gen_tile(raw_maps['inventory'][self.inventory_screen], r_c=(row, col - 1))
        if self.p.state is 'Talking':
            self.gen_text(txt=self.cur_text.text, speaker=self.cur_text.speaker, opts=self.cur_text.dialog_opts)
        if self.p.state is 'Inventory':
            self.gen_inv()
        if self.p.state is 'Walking':
            cur_health = [item for sublist in [[1745]*(self.p.stats['HP'] // 2), [1746]*(self.p.stats['HP'] % 2 == 1)] for item in sublist]
            for row in range(-(-self.p.stats['HP'] // 2)):
                self.gen_tile([cur_health[row]], r_c=(0.5+row, 8.5))

    def cursor(self, list_locs):
        try:
            list_locs[self.cur_opt[1], self.cur_opt[0]]
        except IndexError:
            self.cur_opt = [0, 0, 0]
        highlight = list_locs[self.cur_opt[1], self.cur_opt[0]]
        arcade.draw_texture_rectangle(highlight[0]*32, highlight[1]*HEIGHT+32, WIDTH, HEIGHT, tile_set[1480])

    def gen_text(self, txt=None, speaker=None, opts=None, yx=(2.25, 1)):
        y, x = yx
        if speaker:
            width_sum = 0
            for charpos, char in enumerate(speaker):
                width_sum += char_width[speaker[charpos-1]]
                arcade.draw_texture_rectangle(width_sum+40, 216, WIDTH, HEIGHT, font[ord(char)])
        if opts:
            cursor_locs = np.zeros((len(opts), len(opts[0]), 2), dtype=int)
            for itempos, item in enumerate(opts):
                for optpos, sub in enumerate(item):
                    cursor_locs[itempos, optpos] = [x + len(''.join(opts[itempos][:optpos])), y - itempos - int(txt is not None)]
                    out = ''.join(opts[itempos])
                    width_sum = 0
                    for charpos, char in enumerate(out):
                        width_sum += char_width[out[charpos-1]]
                        arcade.draw_texture_rectangle(width_sum + x * WIDTH, (y - itempos - int(txt is not None)) * HEIGHT, WIDTH, HEIGHT, font[ord(char)])
            self.cursor(cursor_locs)
        if txt:
            for linepos, line in enumerate(txt[self.cur_opt[2]:self.cur_opt[2] + 3]):
                width_sum = 0
                for charpos, char in enumerate(txt[linepos + self.cur_opt[2]]):
                    width_sum += char_width[txt[linepos + self.cur_opt[2]][charpos-1]]
                    arcade.draw_texture_rectangle(width_sum + (x * WIDTH), ((y - linepos) * HEIGHT), WIDTH, HEIGHT, font[ord(char)])

    def gen_inv(self):
        if self.inventory_screen == 0:
            for i in range(len(self.p.inventory[self.cur_opt[2]:self.cur_opt[2] + 6 or -1])):
                self.gen_tile([self.p.inventory[i + self.cur_opt[2]].texture], yx=(6 - i, 3))
            if not self.selected:
                self.gen_text(opts=self.p.get_bag(self.p.inventory)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6, 2))
            else:
                self.gen_text(txt=self.p.get_bag(self.p.inventory, False)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6, 2))
                self.gen_sub_menu()
        elif self.inventory_screen == 1:
            for i in range(len(self.p.equipped[self.cur_opt[2]:self.cur_opt[2] + 6 or -1])):
                self.gen_tile([self.p.equipped[i + self.cur_opt[2]].texture], yx=(6.5 - i, 2))
            if not self.selected:
                self.gen_text(opts=self.p.equip_stats()[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6, 1))
            else:
                self.gen_text(txt=self.p.get_bag(self.p.equipped, False)[self.cur_opt[2]:self.cur_opt[2] + 6 or -1], yx=(6, 1))
                self.gen_sub_menu()
        elif self.inventory_screen == 2:
            self.gen_text(self.p.get_stats(), yx=(6.5, 1))
        else:
            self.gen_text(opts=options_menu, yx=(6.5, 2))

    def gen_sub_menu(self):
        for x, row in enumerate(raw_maps['submenu']):
            for y, col in enumerate(row):
                self.gen_tile(raw_maps['submenu'], (x, y), yx=(10, 2.5))
        self.gen_text(opts=self.cur_item.get_actions(), yx=(6, 11))

    def draw_map(self, inmap, row, col):
        arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT,
                                      tile_set[inmap[row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]])

    @staticmethod
    def gen_tile(in_array=None, r_c=(0, 0), yx=(0, 0)):  # Row/Col correspond to which tile is drawn, X/Y correspond to how much each tile should be shifted over.
        row, col = r_c
        y, x = yx
        if len(in_array) > 1:
            arcade.draw_texture_rectangle(HEIGHT * (y + col), WIDTH * (x + row), WIDTH, HEIGHT, tile_set[in_array[r_c]])
        else:
            arcade.draw_texture_rectangle(WIDTH * (x + row), (HEIGHT * (y + col)), WIDTH, HEIGHT, tile_set[in_array[0]])

    def on_key_press(self, key, modifiers):
        if self.p.state is 'Inventory':
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
                    self.p.state = 'Walking'
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
                elif self.inventory_screen == 3:
                    if 'Exit' in options_menu[self.cur_opt[1]][0]:
                        Game.close(self)
        elif self.p.state is 'Walking':
            if key in movemnet_keys['Inv']:
                self.cur_opt = [0, 0, 0]
                self.p.state = 'Inventory'
                self.inventory_screen = 0
            if key in movemnet_keys['Context']:
                if raw_maps[current_map]['Collision'][self.p.y+1, self.p.x] in nodes:
                    self.cur_opt = [0, 0, 0]
                    self.cur_text = nodes[raw_maps[current_map]['Collision'][self.p.y+1, self.p.x]]
                    self.p.state = 'Talking'
                # elif floor_map[self.p.y, self.p.x]:
                    # self.p.inventory.append(floor_map[self.p.y, self.p.x])
        elif self.p.state is 'Talking':
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
                    self.p.state = 'Walking'
            if key in movemnet_keys['Inv']:
                self.p.state = 'Walking'
        if key in movemnet_keys['Exit']:
            if self.p.state is 'Inventory' and self.selected:
                self.selected = False
            elif self.p.state is not 'Walking':
                self.p.state = 'Walking'
            else:
                self.p.state = 'Inventory'
                self.inventory_screen = 3
        if key == arcade.key.H:
            self.p.stats['HP'] += 1
        if key == arcade.key.N:
            self.p.stats['HP'] -= 1
        if key == arcade.key.M:
            print(raw_maps[current_map]['Collision'][self.p.y-2:self.p.y+3, self.p.x-2:self.p.x+3])

    def update(self, delta_time: float):
        if self.p.state is 'Walking':
            if any(key in movemnet_keys['Up'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x] == -1:
                    self.p.y += 1
                    self.game_step()
            if any(key in movemnet_keys['Down'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x] == -1:
                    self.p.y -= 1
                    self.game_step()
            if any(key in movemnet_keys['Right'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x + 1] == -1:
                    self.p.x += 1
                    self.game_step()
            if any(key in movemnet_keys['Left'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x - 1] == -1:
                    self.p.x -= 1
                    self.game_step()

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
            self.cur_text = item.look()
            self.p.state = 'Talking'
        elif action == 'Drop':
            if item in self.p.inventory:
                self.p.inventory.remove(item)

    def draw_p(self):
        raw_maps[current_map]['Sprite'][self.p.y, self.p.x] = self.p.appearance

    def game_step(self):
        for act in self.actor_list:
            if act.disposition == 'Friendly':
                enemy_list = [i for i in self.actor_list if i.disposition == 'Aggressive']
                if enemy_list:
                    act.target_distance = 1
                    act.move_me((enemy_list[0].y, enemy_list[0].x))
                else:
                    act.target_distance = 2
                    act.move_me((self.p.y, self.p.x))
            elif act.disposition == 'Aggressive':
                act.move_me((self.p.y, self.p.x))
        time.sleep(wait_time)


def main():
    Game(*sc)
    arcade.run()


if __name__ == '__main__':
    main()
