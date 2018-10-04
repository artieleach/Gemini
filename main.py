from items import *

class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.draw_time = 0
        self.processing_time = 0
        self.pressed_keys = self.pressed_keys
        self.cur_opt = [0, 0]
        self.opt_highlighted = False
        self.inventory_screen = 0
        self.cur_item = None
        self.cur_text = None
        self.p = Player()
        self.actor1 = Actor(yx=(61, 26), name='Goast', sprite=908, disposition='Friendly', target_distance=1)
        self.actor2 = Actor(yx=(71, 26), name='Victor', sprite=1780, disposition='Aggressive', target_distance=6)
        self.actor_list = [self.actor1, self.actor2, BrDo2, test_dia]
        self.p.inventory = [scilla, rose, violet, tigerseye, scilla, rose, violet, tigerseye]
        self.cur_health = [item for sublist in [[1745] * (self.p.stats['HP'] // 2), [1746] * (self.p.stats['HP'] % 2 == 1)] for item in sublist]
        self.p.equipped = {'Floating Left': floatingtestone, 'Left Arm': None, 'Left Weapon': greataxe, 'Left Ring One': tigerseye, 'Left Ring Two': None,
                           'Helmet': None, 'Shoulders': None, 'Chest': None, 'Gloves': None, 'Boots': None,
                           'Floating Right': floatingtestone, 'Right Arm': None, 'Right Weapon': greatclub, 'Right Ring One': None, 'Right Ring Two': rose}

    def draw_base(self):
        arcade.start_render()
        for row in range(ROWS):
            for col in range(COLS+1):
                if raw_maps[current_map]['Back'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]:
                    arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT, tile_set
                    [raw_maps[current_map]['Back'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]])
                if raw_maps[current_map]['Mid'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]:
                    arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT, tile_set
                    [raw_maps[current_map]['Mid'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]])
                if raw_maps[current_map]['Sprite'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]:
                    arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT, tile_set
                    [raw_maps[current_map]['Sprite'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2].sprite])
                if raw_maps[current_map]['Fore'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]:
                    arcade.draw_texture_rectangle(HEIGHT * col, WIDTH * row + 32, WIDTH, HEIGHT, tile_set
                    [raw_maps[current_map]['Fore'][row + self.p.y - ROWS // 2, col + self.p.x - COLS // 2]])


    def add_sprites(self):
        raw_maps[current_map]['Sprite'][:] = raw_maps[current_map]['Sprite Copy']
        for actor in self.actor_list:
            raw_maps[current_map]['Sprite'][actor.y, actor.x] = actor
        else:
            raw_maps[current_map]['Sprite'][self.p.y, self.p.x] = self.p

    def on_draw(self):
        draw_start_time = timeit.default_timer()
        self.draw_base()
        if self.p.state is 'Talking':
            for row in range(ROWS):
                for col in range(COLS):
                    self.gen_tile_array(raw_maps['dialog'], r_c=(row, col), yx=(0, 0.5))
            self.gen_text(text=self.cur_text.text, speaker=self.cur_text.speaker, opts=self.cur_text.dialog_opts)
        if self.p.state is 'Inventory':
            for row in range(ROWS):
                for col in range(COLS):
                    self.gen_tile_array(raw_maps['inventory'][self.inventory_screen], r_c=(row, col))
            self.gen_inv()
        if self.p.state is 'Walking':
            for col in range(-(-self.p.stats['HP'] // 2)):  # weird ass way of getting how many heart containers to draw
                self.gen_lone_tile(self.cur_health[col], (0.5 + col, 8.5))
        fps = 1 // (self.draw_time + self.processing_time)
        arcade.draw_text('FPS: {}'.format(fps), 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 16)
        self.draw_time = timeit.default_timer() - draw_start_time

    def switch_state(self, new_state):
        self.cur_opt = [0, 0]
        self.opt_highlighted = False
        if new_state is 'Talking':
            if self.cur_text.speaker:
                raw_maps['dialog'][3] = [i for s in [[0], [1563], [1564] * ((len(self.cur_text.speaker)) // 2 + 1), [1565], [-1] * 15] for i in s][:16]
            else:
                raw_maps['dialog'][3] = [-1] * 16
        if new_state is 'Walking':
            pass
        if new_state is 'Inventory':
            self.inventory_screen = 0
        self.p.state = new_state

    def cursor(self, list_locs, yx):
        y, x = yx
        try:
            list_locs[self.cur_opt[0]]
        except IndexError:
            self.cur_opt = [0, 0]
        arcade.draw_texture_rectangle(x * WIDTH - 32, (y - list_locs[self.cur_opt[0]]) * HEIGHT, WIDTH, HEIGHT, tile_set[1480])

    def gen_text(self, text=None, speaker=None, opts=None, yx=(2.25, 1), len_display=3):
        y, x = yx
        if speaker:
            width_sum = 0
            for char_pos, char in enumerate(speaker):
                width_sum += char_width[speaker[char_pos-1]]
                arcade.draw_texture_rectangle(width_sum+40, 216, WIDTH, HEIGHT, font[ord(char)])
        if opts:
            cursor_locs = [0] * len(opts)
            for item_pos, item in enumerate(opts[self.cur_opt[1]:self.cur_opt[1] + len_display]):
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
        for i in range(4):
            self.gen_lone_tile(i+1820, (1.5 + i * 2, 8))
        if self.inventory_screen == 0:
            try:
                for i in range(len(self.p.inventory[self.cur_opt[1]:self.cur_opt[1] + 6 or -1])):
                    self.gen_lone_tile(self.p.inventory[i + self.cur_opt[1]].sprite, yx=(2, 6.5 - i))
            except IndexError:
                pass
            if not self.opt_highlighted:
                self.gen_text(opts=['  {}'.format(i) for i in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
            else:
                self.gen_text(text=['  {}'.format(i) for i in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()  # this is disgusting
        if self.inventory_screen == 1:
            for item_pos, cur_item in enumerate(list(self.p.equipped.keys())):
                if self.p.equipped[cur_item] is not None:
                    self.gen_lone_tile(self.p.equipped[cur_item].sprite, yx=(2 + item_pos // 5, 6 - item_pos % 5))
            if not self.opt_highlighted:
                self.gen_lone_tile(1905, yx=(2 + self.cur_opt[1], 6 - self.cur_opt[0]))
                if self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[1] * 5 + self.cur_opt[0]]] is not None:
                    print(self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[1] * 5 + self.cur_opt[0]]].name)
                    self.gen_text(text=[self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[1] * 5 + self.cur_opt[0]]].name], yx=(6.5, 5.5))
            else:  # opt is selected
                self.gen_text(text=self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[1] * 5 + self.cur_opt[0]]].actions, yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()
        if self.inventory_screen == 2:
            self.gen_text(text=self.p.get_stats(), yx=(6.5, 1), len_display=6)
        if self.inventory_screen == 3:
            self.gen_text(opts=options_menu, yx=(6.5, 2))

    def gen_sub_menu(self):
        for x, row in enumerate(raw_maps['submenu']):
            for y, col in enumerate(row):
                print('got this far')
                self.gen_tile_array(raw_maps['submenu'], (x, y), yx=(10, 2.5))
        self.gen_text(opts=self.cur_item.get_actions(), yx=(6, 11))

    @staticmethod
    def gen_tile_array(in_array, r_c, yx=(0, 0)):
        row, col = r_c
        y, x = yx
        arcade.draw_texture_rectangle(HEIGHT * (y + col), WIDTH * (x + row), WIDTH, HEIGHT, tile_set[in_array[r_c]])

    @staticmethod
    def gen_lone_tile(in_tile, yx, base_img=tile_set):
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
                    else:
                        self.cur_item = self.p.inventory[sum(self.cur_opt)]

            if self.inventory_screen == 1:
                if key in movement_keys['S'] and self.cur_opt[0] < 4:
                    self.cur_opt[0] += 1
                if key in movement_keys['N'] and self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1
                if key in movement_keys['E'] and self.cur_opt[1] < 2:
                    self.cur_opt[1] += 1
                if key in movement_keys['W'] and self.cur_opt[1] > 0:
                    self.cur_opt[1] -= 1
                if key in movement_keys['Context']:
                    if self.opt_highlighted:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[0]])
                    else:
                        self.cur_item = self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]].name
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
        if self.p.state is 'Walking':
            if key in movement_keys['Inv']:
                self.switch_state('Inventory')
            if key in movement_keys['Context']:
                if type(raw_maps[current_map]['Sprite'][self.p.y + 1, self.p.x]) is DialogItem:
                    self.cur_text = raw_maps[current_map]['Sprite'][self.p.y + 1, self.p.x]
                    self.switch_state('Talking')
        if self.p.state is 'Talking':
            if self.cur_text.dialog_opts:
                if key in movement_keys['N']:
                    if self.cur_opt[0] > 0:
                        self.cur_opt[0] -= 1
                    elif self.cur_opt[1] > 0:
                        self.cur_opt[1] -=1
                if key in movement_keys['S']:
                    if self.cur_opt[0] < 2:
                        self.cur_opt[0] += 1
                    elif sum(self.cur_opt) < len(self.cur_text.dialog_opts) - 1:
                        self.cur_opt[1] += 1
                if key in movement_keys['Context']:
                    print(self.cur_text.dialog_opts[sum(self.cur_opt)])
        if key in movement_keys['Exit']:
            if self.p.state is 'Inventory' and self.opt_highlighted:
                self.opt_highlighted = False
            elif self.p.state is not 'Walking':
                self.switch_state('Walking')
            else:
                self.switch_state('Inventory')
                self.inventory_screen = 3

    def update(self, delta_time: float):
        start_time = timeit.default_timer()
        if self.p.state is 'Walking':
            if any(key in movement_keys['N'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x] == -1:
                    self.p.y += 1
                    self.game_step()
            if any(key in movement_keys['S'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x] == -1:
                    self.p.y -= 1
                    self.game_step()
            if any(key in movement_keys['E'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x + 1] == -1:
                    self.p.x += 1
                    self.game_step()
            if any(key in movement_keys['W'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y, self.p.x - 1] == -1:
                    self.p.x -= 1
                    self.game_step()
            if any(key in movement_keys['NE'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x + 1] == -1:
                    self.p.x += 1
                    self.p.y += 1
                    self.game_step()
            if any(key in movement_keys['NW'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x + 1] == -1:
                    self.p.x -= 1
                    self.p.y += 1
                    self.game_step()
            if any(key in movement_keys['SE'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y + 1, self.p.x - 1] == -1:
                    self.p.x += 1
                    self.p.y -= 1
                    self.game_step()
            if any(key in movement_keys['SW'] for key in self.pressed_keys):
                if raw_maps[current_map]['Collision'][self.p.y - 1, self.p.x - 1] == -1:
                    self.p.x -= 1
                    self.p.y -= 1
                    self.game_step()
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

    def add_sprites(self):
        raw_maps[current_map]['Sprite'][:] = raw_maps[current_map]['Sprite Copy']
        for actor in self.actor_list:
            raw_maps[current_map]['Sprite'][actor.y, actor.x] = actor
        else:
            raw_maps[current_map]['Sprite'][self.p.y, self.p.x] = self.p

    def game_step(self):
        self.add_sprites()
        cur_health = [item for sublist in [[1745] * (self.p.stats['HP'] // 2), [1746] * (self.p.stats['HP'] % 2 == 1)] for item in sublist]
        for act in self.actor_list:
            if type(act) is Actor:
                try:
                    if act.disposition is 'Friendly':
                        enemy_list = [i for i in self.actor_list if i.disposition is 'Aggressive']
                        if enemy_list:
                            act.target_distance = 1
                            act.move_me((enemy_list[0].y, enemy_list[0].x))
                        else:
                            act.target_distance = 2
                            act.move_me((self.p.y, self.p.x))
                    elif act.disposition is 'Aggressive':
                        act.move_me((self.p.y, self.p.x))
                except AttributeError:
                    pass


def main():
    Game(*sc)
    arcade.run()


if __name__ == '__main__':
    main()
