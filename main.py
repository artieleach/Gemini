from items import *


class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.draw_time = 0
        self.processing_time = 0
        self.pressed_keys = self.pressed_keys
        self.cur_opt = [0, 0, False]  # Y, offset, selected
        self.inventory_screen = 0
        self.cur_text = None
        self.cur_item = None
        self.p = Player()
        self.cur_opt[2] = False
        # the definitions below are just for testing
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
            for col in range(COLS + 1):
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

    def on_draw(self):
        draw_start_time = timeit.default_timer()
        self.add_sprites()
        self.draw_base()
        for row in range(ROWS):
            for col in range(COLS):
                if self.p.state == 'Talking':
                    self.gen_tile_array(raw_maps['dialog'], r_c=(row, col), yx=(0, 0.5))
                elif self.p.state == 'Inventory':
                    self.gen_tile_array(raw_maps['inventory'][self.inventory_screen], r_c=(row, col))
        if self.p.state is 'Talking':
            self.gen_text(text=self.cur_text.text, speaker=self.cur_text.speaker, opts=self.cur_text.dialog_opts)
        elif self.p.state is 'Inventory':
            self.gen_inv()
        elif self.p.state is 'Walking':
            for col in range(-(-self.p.stats['HP'] // 2)):  # weird ass way of getting how many heart containers to draw
                self.gen_lone_tile(self.cur_health[col], (0.5 + col, 8.5))
        fps = 1 // (self.draw_time + self.processing_time)
        arcade.draw_text('FPS: {}'.format(fps), 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 16)
        self.draw_time = timeit.default_timer() - draw_start_time

    def switch_state(self, new_state):
        self.cur_opt = [0, 0, False]
        if new_state == 'Talking':
            if self.cur_text.speaker:
                raw_maps['dialog'][3] = [i for s in [[0], [1563], [1564] * ((len(self.cur_text.speaker)) // 2 + 1), [1565], [-1] * 15] for i in s][:16]
            else:
                raw_maps['dialog'][3] = [-1] * 16
        elif new_state == 'Walking':
            pass
        elif new_state == 'Inventory':
            self.inventory_screen = 0
        self.p.state = new_state

    def cursor(self, list_locs, yx):
        y, x = yx
        try:
            list_locs[self.cur_opt[0]]
        except IndexError:
            self.cur_opt = [0, 0, False]
        arcade.draw_texture_rectangle(x * WIDTH - 32, (y - list_locs[self.cur_opt[0]]) * HEIGHT, WIDTH, HEIGHT, tile_set[1480])

    def gen_text(self, text=None, speaker=None, opts=None, yx=(2.25, 1), len_display=3):
        y, x = yx
        if speaker:
            width_sum = 0
            for charpos, char in enumerate(speaker):
                width_sum += char_width[speaker[charpos - 1]]
                arcade.draw_texture_rectangle(width_sum + 40, 216, WIDTH, HEIGHT, font[ord(char)])
        if opts:
            cursor_locs = np.arange(0, len(opts))
            for itempos, item in enumerate(opts[self.cur_opt[1]:self.cur_opt[1] + len_display]):
                width_sum = 0
                for charpos, char in enumerate(item):
                    width_sum += char_width[item[charpos - 1]]
                    arcade.draw_texture_rectangle(width_sum + x * WIDTH, (y - itempos - int(text is not None)) * HEIGHT, WIDTH, HEIGHT, font[ord(char)])
            self.cursor(cursor_locs, yx)
        if text:
            for linepos, line in enumerate(text[self.cur_opt[1]:self.cur_opt[1]+len_display]):
                width_sum = 0
                for charpos, char in enumerate(text[linepos + self.cur_opt[1]]):
                    width_sum += char_width[text[linepos + self.cur_opt[1]][charpos - 1]]
                    arcade.draw_texture_rectangle(width_sum + (x * WIDTH), ((y - linepos) * HEIGHT), WIDTH, HEIGHT, font[ord(char)])

    def gen_inv(self):
        for i in range(4):  # the inventory icons
            self.gen_lone_tile(i + 1820, (1.5 + i * 2, 8))
        if self.inventory_screen == 0:
            try:
                for i in range(len(self.p.inventory[self.cur_opt[1]:self.cur_opt[1] + 6 or -1])):  # this must be zero long to recieve an error
                    self.gen_lone_tile(self.p.inventory[i + self.cur_opt[1]].sprite, yx=(2, 6.5 - i))
            except IndexError:
                pass
            if not self.cur_opt[2]:
                self.gen_text(opts=['  {}'.format(i) for i in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
            else:
                self.gen_text(text=['  {}'.format(i) for i in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()
        elif self.inventory_screen == 1:
            for item_pos, cur_item in enumerate(list(self.p.equipped.keys())):
                try:
                    self.gen_lone_tile(self.p.equipped[cur_item].sprite, yx=(2 + item_pos // 5, 6 - item_pos % 5))
                except AttributeError:
                    pass
            if not self.cur_opt[2]:
                raw_maps['inventory'][1][6 - self.cur_opt[0] % 5][self.cur_opt[0] // 5 + 2] = 1905
                try:
                    print(self.cur_opt[0])
                    self.gen_text(text=[self.p.equipped[list(self.p.equipped.keys())[self.cur_opt[0]]].name], yx=(6.5, 5.5), len_display=1)
                except AttributeError:
                    pass
            else:
                self.gen_text(text=['  {}'.format(i) for i in self.p.name_list(self.p.inventory)], yx=(6.5, 1.5), len_display=6)
                self.gen_sub_menu()
        elif self.inventory_screen == 2:
            self.gen_text(self.p.get_stats(), yx=(6.5, 1), len_display=6)
        elif self.inventory_screen == 3:
            self.gen_text(opts=options_menu, yx=(6.5, 2))

    def gen_sub_menu(self):
        for x, row in enumerate(raw_maps['submenu']):
            for y, col in enumerate(row):
                self.gen_tile_array(raw_maps['submenu'], (x, y), yx=(10, 2.5))
        self.gen_text(opts=self.cur_item.get_actions(), yx=(6, 11))

    @staticmethod
    def gen_tile_array(in_array, r_c, yx=(0, 0)):  # Row/Col = which tile is drawn, X/Y = how much each tile should be shifted over.
        row, col, = r_c
        y, x = yx
        arcade.draw_texture_rectangle(HEIGHT * (y + col), WIDTH * (x + row), WIDTH, HEIGHT, tile_set[in_array[r_c]])

    @staticmethod
    def gen_lone_tile(in_tile, yx, base_img=tile_set):
        y, x = yx
        arcade.draw_texture_rectangle(HEIGHT * y, WIDTH * x, WIDTH, HEIGHT, base_img[in_tile])

    def on_key_press(self, key, modifiers):
        if self.p.state is 'Inventory':
            if key in movement_keys['NW'] and self.inventory_screen > 0:
                self.cur_opt = [0, 0, False]
                self.inventory_screen -= 1
            if key in movement_keys['NE'] and self.inventory_screen < 3:
                self.cur_opt = [0, 0, False]
                self.inventory_screen += 1

            if self.inventory_screen == 0:
                if key in movement_keys['S']:
                    if self.cur_opt[2]:
                        self.cur_opt[0] += 1
                    else:
                        if self.cur_opt[0] < 5:
                            self.cur_opt[0] += 1
                        elif sum(self.cur_opt[:-1]) + 1 < len(self.p.inventory):
                            self.cur_opt[1] += 1
                            print(self.cur_opt, len(self.p.inventory))
                if key in movement_keys['N']:
                    if self.cur_opt[0] > 0:
                        self.cur_opt[0] -= 1
                    elif self.cur_opt[1] > 0:
                        self.cur_opt[1] -= 1
            else:
                if key in movement_keys['S']:
                    if self.cur_opt[2]:
                        self.cur_opt[0] += 1
                    else:
                        self.cur_opt[0] += 1
                if key in movement_keys['N']:
                    if self.cur_opt[0] > 0:
                        self.cur_opt[0] -= 1
            if key in movement_keys['Inv']:
                if self.cur_opt[2]:
                    self.cur_opt[2] = False
                else:
                    self.switch_state('Walking')
            if key in movement_keys['E']:
                if self.cur_opt[1] > 0:
                    self.cur_opt[1] += 1
            if key in movement_keys['W']:
                if self.cur_opt[1] < 6:
                    self.cur_opt[1] -= 1
            if key in movement_keys['Context']:
                if self.inventory_screen == 0:
                    if not self.cur_opt[2]:
                        self.cur_item = self.p.inventory[sum(self.cur_opt[:-1])]  # self.cur_opt[:-1] is the Y + the offset
                    else:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[0]])
                    self.cur_opt = [0, 0, False]
                    self.cur_opt[2] = not self.cur_opt[2]
                elif self.inventory_screen == 1:
                    if self.cur_opt[2]:
                        self.interact_item(self.cur_item, self.cur_item.actions[self.cur_opt[0]])
                    else:
                        self.cur_item = self.p.equipped[sum(self.cur_opt)]
                    self.cur_opt = [0, 0, False]
                    self.cur_opt[2] = not self.cur_opt[2]
                elif self.inventory_screen == 3:
                    if 'Settings' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
                    if 'Gameplay' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
                    if 'Exit' in options_menu[self.cur_opt[0]]:
                        Game.close(self)
        elif self.p.state is 'Walking':
            if key in movement_keys['Inv']:
                self.switch_state('Inventory')
            if key in movement_keys['Context']:
                if type(raw_maps[current_map]['Sprite'][self.p.y + 1, self.p.x]) is DialogItem:
                    self.cur_text = raw_maps[current_map]['Sprite'][self.p.y + 1, self.p.x]
                    self.switch_state('Talking')
        elif self.p.state is 'Talking':
            if self.cur_text.dialog_opts:
                if key in movement_keys['E'] and self.cur_opt[0] < len(self.cur_text.dialog_opts):
                    self.cur_opt[0] += 1
                if key in movement_keys['W'] and self.cur_opt[0] > 0:
                    self.cur_opt[0] -= 1
                if key in movement_keys['N']:
                    if self.cur_opt[0] > 0:
                        self.cur_opt[0] -= 1
                    elif self.cur_opt[1] > 0:
                        self.cur_opt[1] -=1
                if key in movement_keys['S']:
                    if self.cur_opt[0] < 2:
                        self.cur_opt[0] += 1
                    elif sum(self.cur_opt[:-1]) < len(self.cur_text.dialog_opts) - 1:
                        self.cur_opt[1] += 1
                if key in movement_keys['Context']:
                    print(self.cur_text.dialog_opts[sum(self.cur_opt[:-1])])
            if key in movement_keys['Context'] and self.cur_text.text:
                if self.cur_opt[1] < len(self.cur_text.text) - 2:
                    self.cur_opt[1] += 1
                else:
                    self.switch_state('Walking')
            if key in movement_keys['Inv']:
                self.switch_state('Walking')
        if key in movement_keys['Exit']:
            if self.p.state is 'Inventory' and self.cur_opt[2]:
                self.cur_opt[2] = False
            elif self.p.state is not 'Walking':
                self.switch_state('Walking')
            else:
                self.switch_state('Inventory')
                self.inventory_screen = 3
        if key == arcade.key.N:
            self.game_step()

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
        if action == 'Equip':
            if item in self.p.inventory:
                self.p.inventory.remove(item)
                for possible_pos in item.body_position:
                    if self.p.equipped[possible_pos] is None:
                        self.p.equipped[possible_pos] = item
                    # add some code here to account for multiple possible positions, and how to handle when all positions are taken
            else:  # since its not in the inv and equip is being called, that means it must already be equipped
                pass
                # self.p.inventory.append(item)
        elif action == 'Look':
            self.cur_text = item.look()
            self.switch_state('Talking')
        elif action == 'Drop':
            if item in self.p.inventory:
                self.p.inventory.remove(item)

    def add_sprites(self):
        raw_maps[current_map]['Sprite'][:] = raw_maps[current_map]['Sprite Copy']
        for actor in self.actor_list:
            raw_maps[current_map]['Sprite'][actor.y, actor.x] = actor
            # raw_maps[current_map]['Collision'][actor.y, actor.x] = 1
        else:
            raw_maps[current_map]['Sprite'][self.p.y, self.p.x] = self.p

    def game_step(self):
        cur_health = [item for sublist in [[1745] * (self.p.stats['HP'] // 2), [1746] * (self.p.stats['HP'] % 2 == 1)] for item in sublist]
        for act in self.actor_list:
            if type(act) is Actor:
                try:
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
                except AttributeError:
                    pass


def main():
    Game(*sc)
    arcade.run()


if __name__ == '__main__':
    main()

































