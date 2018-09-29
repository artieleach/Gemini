from init import *


class Entity:
    def __init__(self, yx=(0, 0), name=None, sprite=-1):
        self.y, self.x = yx
        self.name = name
        self.sprite = sprite

    @staticmethod
    def name_list(in_list):
        try:
            return [i.name for i in in_list]
        except AttributeError:
            raise('{} does not have a name attribute'.format(in_list))


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
            self.text = out_lines
        else:
            self.text = text
        if dialog_opts:
            self.dialog_opts = list(dialog_opts.keys())
        else:
            self.dialog_opts = None

    def new_opt(self, newopt):
        pass


BrokenDoor = DialogItem(sprite=33, text='Who is it?', speaker='Thine Momther', yx=(73, 27), on_level='Overworld')
BrDo2 = DialogItem(sprite=33,
                   dialog_opts={"What this?": BrokenDoor, "Why that?": BrokenDoor, "Who there?": BrokenDoor, "When it?": BrokenDoor},
                   speaker='Thine Momther', yx=(73, 27), on_level='Overworld')
test_dia = DialogItem(sprite=34, text='''At last I have the privilege of making public this third book of Marx's main work, the conclusion of the theoretical part. When I published the second volume, in 1885, I thought that except for a few, certainly very important, sections the third volume would probably offer only technical difficulties. This was indeed the case. But I had no idea at the time that these sections, the most important parts of the entire work, would give me as much trouble as they did, just as I did not anticipate the other obstacles, which were to retard completion of the work to such an extent.''',
                      speaker='Marx', yx=(73, 26), on_level='Overworld')


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
        self.equipped = {'Floating Left': None, 'Left Arm': None, 'Left Weapon': None, 'Left Ring One': None, 'Left Ring Two': None,
                         'Helmet': None, 'Shoulders': None, 'Chest': None, 'Gloves': None, 'Boots': None,
                         'Floating Right': None, 'Right Arm': None, 'Right Weapon': None, 'Right Ring One': None, 'Right Ring Two': None}
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
