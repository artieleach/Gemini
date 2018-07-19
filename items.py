import textwrap


class Item:
    def __init__(self, name, cost, weight, texture, flavor_text=None):
        self.name = name
        self.cost = cost
        self.weight = weight
        self.texture = texture
        self.flavor_text = flavor_text
        self.actions = ['Look', 'Drop']

    def look(self):
        return DialogItem(text=self.flavor_text, speaker=self.name)

    def get_actions(self):
        return [[' {} '.format(i)] for i in self.actions]


class EquipmentItem(Item):
    def __init__(self, name, cost, weight, texture):
        Item.__init__(self, name, cost, weight, texture)
        self.actions.append('Equip')


class Armor(EquipmentItem):
    def __init__(self, name, cost, weight, speed, asfc, type, bonus, acp, max_bonus, texture):
        EquipmentItem.__init__(self, name, cost, weight, texture)
        self.type = type
        self.speed = speed
        self.asfc = asfc
        self.type = type
        self.bonus = bonus
        self.acp = acp
        self.cost = cost
        self.max_bonus = max_bonus

    def __repr__(self):
        return '   {} (+{})'.format(self.name, self.bonus)

    def look(self):
        return DialogItem(text='{} {} {}'.format(self.type, self.asfc, self.bonus), speaker=self.name)


class Weapon(EquipmentItem):
    def __init__(self, name, texture, damage, dmg_style, weight, style, cost, handed, crit_mult, range):
        EquipmentItem.__init__(self, name, cost, weight, texture)
        self.damage = damage
        self.damage_style = dmg_style
        self.weapon_type = style
        self.handed = handed
        self.critical_multiplier = crit_mult
        self.range = range

    def __repr__(self):
        return '   {} ({})'.format(self.name, self.damage)

    def look(self):
        return DialogItem(text='({} - {}) {} {}-Handed, crit:{}'.format(self.damage, self.damage_style, self.weapon_type, 'Two'*bool(self.handed-1) or 'One', self.critical_multiplier), speaker=self.name)


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


class DialogItem:
    def __init__(self, text=None, speaker=None, dialog_opts=None):
        self.speaker = speaker
        if type(text) is str:
            self.text = textwrap.wrap(text, 22)
        else:
            self.text = text
        if type(dialog_opts) is list:
            if type(dialog_opts[0]) is list:
                self.dialog_opts = [[' {} '.format(opt) for opt in lin] for lin in dialog_opts]
            else:
                self.dialog_opts = [[' {} '.format(opt)] for opt in dialog_opts]
        else:
            self.dialog_opts = dialog_opts


nodes = {
    2: DialogItem(text='Anime makes you gay.', speaker='Your Mother'),
    3: DialogItem(text="Steal the boat?", dialog_opts=([['Yes', 'Why?', 'Property is theft'],
                                                        ['No', 'Steal half', 'Whose boat?']])),
}


scilla = Item(name='Scilla', cost=10, weight=0, texture=541, flavor_text='A lovely blue flower.')
rose = Item(name='Scilla', cost=10, weight=0, texture=542, flavor_text='Not as red as you expected.')
violet = Item(name='Violet', cost=10, weight=0, texture=543, flavor_text='Roses are red, violets are blue, I hit my head, there once was a man from peru')
camellia = Item(name='Camellia', cost=10, weight=0, texture=544, flavor_text='Snow on mount Fuji')
sapphire = Item(name='Sapphire', cost=200, weight=1, texture=546, flavor_text='Have a bite!')
garnet = Item(name='Garnet', cost=600, weight=1, texture=547)
amber = Item(name='Amber', cost=2000, weight=1, texture=548)
tigerseye = Item(name="Tiger's Eye", cost=10000, weight=1, texture=549)
chest = Item(name='Small Chest', cost=50, weight=5, texture=550)
rmush = Item(name='Red Mushroom', cost=10, weight=1, texture=162)
lmush = Item(name='Large Red Mushroom', cost=20, weight=2, texture=219)
smush = Item(name='Spotted Mushroom', cost=40, weight=1, texture=276)
lsmush = Item(name='Large Spotted Mushroom', cost=80, weight=1, texture=333)
bmush = Item(name='Brown Mushroom', cost=5, weight=1, texture=390)
lbmush = Item(name='Large Brown Mushroom', cost=10, weight=2, texture=447)
redbottle = Item(name='Red Bottle', cost=20, weight=2, texture=682)
yellowbottle = Item(name='Yellow Bottle', cost=20, weight=2, texture=683)
bluebottle = Item(name='Blue Bottle', cost=20, weight=2, texture=738)
greenbottle = Item(name='Green Bottle', cost=20, weight=2, texture=852)
book = Item(name='Book', cost=200, weight=1, texture=901, flavor_text='Man I wish I learned how to read.')
bible = Item(name='Religious Text', cost=400, weight=1, texture=902)
novel = Item(name='Novel', cost=20, weight=2, texture=903)
oldbook = Item(name='Historical Document', cost=8000, weight=1, texture=904)
paper = Item(name='Parchment', cost=2, weight=0, texture=896)
document = Item(name='Document', cost=8, weight=0, texture=897)
scroll = Item(name='Scroll', cost=60, weight=0, texture=899)

gauntlet = Weapon(name='Gauntlet', damage='1d3', dmg_style='Bludgeoning', weight=1, style='simple', cost=2, handed=1, crit_mult='x2', range=0, texture=0)
dagger = Weapon(name='Dagger', damage='1d4', dmg_style='Piercing or slashing', weight=1, style='simple', cost=2, handed=1, crit_mult='19-20/x2', range=10, texture=2204)
spikedGauntlet = Weapon(name='Spiked Gauntlet', damage='1d4', dmg_style='Piercing', weight=1, style='simple', cost=5, handed=1, crit_mult='x2', range=0, texture=0)
lightmace = Weapon(name='Light Mace', damage='1d6', dmg_style='Bludgeoning', weight=4, style='simple', cost=5, handed=1, crit_mult='x2', range=0, texture=2301)
sickle = Weapon(name='Sickle', damage='1d6', dmg_style='Slashing', weight=2, style='simple', cost=6, handed=1, crit_mult='x2', range=0, texture=1868)
club = Weapon(name='Club', damage='1d6', dmg_style='Bludgeoning', weight=3, style='simple', cost=0, handed=1, crit_mult='x2', range=10, texture=1803)
hevaymace = Weapon(name='Heavy Mace', damage='1d8', dmg_style='Bludgeoning', weight=8, style='simple', cost=12, handed=1, crit_mult='x2', range=0, texture=1808)
morningstar = Weapon(name='Morningstar', damage='1d8', dmg_style='Bludgeoning and piercing', weight=6, style='simple', cost=8, handed=1, crit_mult='x2', range=0, texture=1809)
shortspear = Weapon(name='Short Spear', damage='1d6', dmg_style='Piercing', weight=3, style='simple', cost=1, handed=1, crit_mult='x2', range=20, texture=1806)
longspear = Weapon(name='Long Spear', damage='1d8', dmg_style='Piercing', weight=9, style='simple', cost=5, handed=2, crit_mult='x3', range=0, texture=1810)
quarterstaff = Weapon(name='Quarterstaff', damage='1d6/1d6', dmg_style='Bludgeoning', weight=4, style='simple', cost=0, handed=2, crit_mult='x2', range=0, texture=1804)
heavycrossbow = Weapon(name='Heavy Crossbow', damage='1d10', dmg_style='Piercing', weight=8, style='simple', cost=50, handed=2, crit_mult='19-20/x2', range=120, texture=1870)
lightcrossbow = Weapon(name='Light Crossbow', damage='1d8', dmg_style='Piercing', weight=4, style='simple', cost=35, handed=2, crit_mult='19-20/x2', range=80, texture=1813)
dart = Weapon(name='Dart', damage='1d4', dmg_style='Piercing', weight=1, style='simple', cost=5, handed=2, crit_mult='x2', range=20, texture=0)
javelin = Weapon(name='Javelin', damage='1d6', dmg_style='Piercing', weight=2, style='simple', cost=1, handed=2, crit_mult='x2', range=30, texture=2038)
sling = Weapon(name='Sling', damage='1d4', dmg_style='Bludgeoning', weight=0, style='simple', cost=0, handed=2, crit_mult='x2', range=50, texture=0)
throwingaxe = Weapon(name='Throwing Axe', damage='1d6', dmg_style='Slashing', weight=2, style='martial', cost=8, handed=2, crit_mult='x2', range=10, texture=1867)
lighthammer = Weapon(name='Light Hammer', damage='1d4', dmg_style='Bludgeoning', weight=2, style='martial', cost=1, handed=1, crit_mult='x2', range=20, texture=1866)
handaxe = Weapon(name='Hand Axe', damage='1d6', dmg_style='Slashing', weight=3, style='martial', cost=6, handed=1, crit_mult='x3', range=0, texture=1865)
kukri = Weapon(name='Kukri', damage='1d4', dmg_style='Slashing', weight=2, style='martial', cost=8, handed=1, crit_mult='18-20/x2', range=0, texture=2319)
lightPick = Weapon(name='Light Pick', damage='1d4', dmg_style='Piercing', weight=3, style='martial', cost=4, handed=1, crit_mult='x4', range=0, texture=0)
sap = Weapon(name='Sap', damage='1d6', dmg_style='Bludgeoning', weight=2, style='martial', cost=1, handed=1, crit_mult='x2', range=0, texture=0)
shortsword = Weapon(name='Short Sword', damage='1d6', dmg_style='Piercing', weight=2, style='martial', cost=10, handed=1, crit_mult='19-20/x2', range=0, texture=2204)
battleaxe = Weapon(name='Battle Axe', damage='1d8', dmg_style='Slashing', weight=6, style='martial', cost=10, handed=1, crit_mult='x3', range=0, texture=2039)
flail = Weapon(name='Flail', damage='1d8', dmg_style='Bludgeoning', weight=5, style='martial', cost=8, handed=1, crit_mult='x2', range=0, texture=1923)
longsword = Weapon(name='Long Sword', damage='1d8', dmg_style='Slashing', weight=4, style='martial', cost=15, handed=1, crit_mult='19-20/x2', range=0, texture=2147)
heavypick = Weapon(name='Heavy Pick', damage='1d6', dmg_style='Piercing', weight=6, style='martial', cost=8, handed=1, crit_mult='x4', range=0, texture=0)
rapier = Weapon(name='Rapier', damage='1d6', dmg_style='Piercing', weight=2, style='martial', cost=20, handed=1, crit_mult='18-20/x2', range=0, texture=2148)
scimitar = Weapon(name='Scimitar', damage='1d6', dmg_style='Slashing', weight=4, style='martial', cost=15, handed=1, crit_mult='18-20/x2', range=0, texture=2318)
trident = Weapon(name='Trident', damage='1d8', dmg_style='Piercing', weight=4, style='martial', cost=15, handed=1, crit_mult='x2', range=10, texture=0)
warhammer = Weapon(name='War Hammer', damage='1d8', dmg_style='Bludgeoning', weight=5, style='martial', cost=12, handed=1, crit_mult='3', range=0, texture=0)
falchion = Weapon(name='Falchion', damage='2d4', dmg_style='Slashing', weight=8, style='martial', cost=75, handed=2, crit_mult='18-20/x2', range=0, texture=2261)
glaive = Weapon(name='Glaive', damage='1d10', dmg_style='Slashing', weight=10, style='martial', cost=8, handed=2, crit_mult='x3', range=0, texture=0)
greataxe = Weapon(name='Great Axe', damage='1d12', dmg_style='Slashing', weight=12, style='martial', cost=20, handed=2, crit_mult='x3', range=0, texture=2325)
greatclub = Weapon(name='Great Club', damage='1d10', dmg_style='Bludgeoning', weight=8, style='martial', cost=5, handed=2, crit_mult='x2', range=0, texture=0)
heavyflail = Weapon(name='Heavy Flail', damage='1d10', dmg_style='Bludgeoning', weight=10, style='martial', cost=15, handed=2, crit_mult='19-20/x2', range=0, texture=2265)
greatsword = Weapon(name='Great Sword', damage='2d6', dmg_style='Slashing', weight=8, style='martial', cost=50, handed=2, crit_mult='19-20/x2', range=0, texture=2149)
guisarme = Weapon(name='Guisarme', damage='2d4', dmg_style='Slashing', weight=12, style='martial', cost=9, handed=2, crit_mult='x3', range=0, texture=2267)
halberd = Weapon(name='Halberd', damage='1d10', dmg_style='Piercing or slashing', weight=12, style='martial', cost=10, handed=2, crit_mult='x3', range=0, texture=2268)
lance = Weapon(name='Lance', damage='1d8', dmg_style='Piercing', weight=10, style='martial', cost=10, handed=2, crit_mult='x3', range=0, texture=0)
ranseur = Weapon(name='Ranseur', damage='2d4', dmg_style='Piercing', weight=12, style='martial', cost=10, handed=2, crit_mult='x3', range=0, texture=0)
scythe = Weapon(name='Scythe', damage='2d4', dmg_style='Piercing or slashing', weight=10, style='martial', cost=18, handed=2, crit_mult='x4', range=0, texture=0)
longbow = Weapon(name='Longbow', damage='1d8', dmg_style='Piercing', weight=3, style='martial', cost=75, handed=2, crit_mult='x3', range=100, texture=1928)
compositelongbow = Weapon(name='Composite Longbow', damage='1d8', dmg_style='Piercing', weight=3, style='martial', cost=100, handed=2, crit_mult='x3', range=110, texture=0)
shortbow = Weapon(name='Shortbow', damage='1d6', dmg_style='Piercing', weight=2, style='martial', cost=30, handed=2, crit_mult='x3', range=60, texture=1813)
compositeshortbow = Weapon(name='Composite Shortbow', damage='1d6', dmg_style='Piercing', weight=2, style='martial', cost=75, handed=2, crit_mult='x3', range=70, texture=0)
kama = Weapon(name='Kama', damage='1d6', dmg_style='Slashing', weight=2, style='exotic', cost=2, handed=1, crit_mult='x2', range=0, texture=0)
nunchaku = Weapon(name='Nunchaku', damage='1d6', dmg_style='Bludgeoning', weight=2, style='exotic', cost=2, handed=1, crit_mult='x2', range=0, texture=0)
sai = Weapon(name='Sai', damage='1d4', dmg_style='Bludgeoning', weight=1, style='exotic', cost=1, handed=1, crit_mult='x2', range=10, texture=0)
siangham = Weapon(name='Siangham', damage='1d6', dmg_style='Piercing', weight=1, style='exotic', cost=3, handed=1, crit_mult='x2', range=0, texture=0)
bastardsword = Weapon(name='Bastard Sword', damage='1d10', dmg_style='Slashing', weight=6, style='exotic', cost=35, handed=1, crit_mult='19-20/x2', range=0, texture=0)
dwarvenwaraxe = Weapon(name='Dwarven Waraxe', damage='1d10', dmg_style='Slashing', weight=8, style='exotic', cost=30, handed=1, crit_mult='x3', range=0, texture=0)
whip = Weapon(name='Whip', damage='1d3', dmg_style='Slashing', weight=2, style='exotic', cost=1, handed=1, crit_mult='x2', range=0, texture=0)
orcdoubleaxe = Weapon(name='Orc Double Axe', damage='1d8/1d8', dmg_style='Slashing', weight=15, style='exotic', cost=60, handed=2, crit_mult='x3', range=0, texture=0)
spikedchain = Weapon(name='Spiked Chain', damage='2d4', dmg_style='Piercing', weight=10, style='exotic', cost=25, handed=2, crit_mult='x2', range=0, texture=0)
direflail = Weapon(name='Dire Flail', damage='1d8/1d8', dmg_style='Bludgeoning', weight=10, style='exotic', cost=90, handed=2, crit_mult='x2', range=0, texture=0)
gnomehookedhammer = Weapon(name='Gnome Hooked Hammer', damage='1d8/1d6', dmg_style='Bludgeoning/Piercing', weight=6, style='exotic', cost=20, handed=2, crit_mult='x3/x4', range=0, texture=0)
twobladedsword = Weapon(name='Two Bladed Sword', damage='1d8/1d8', dmg_style='Slashing', weight=10, style='exotic', cost=100, handed=2, crit_mult='19-20/x2', range=0, texture=0)
dwarvenurgrosh = Weapon(name='Dwarven Urgrosh', damage='1d8/1d6', dmg_style='Slashing or piercing', weight=12, style='exotic', cost=50, handed=2, crit_mult='x3', range=0, texture=0)
bolas = Weapon(name='Bolas', damage='1d4', dmg_style='Bludgeoning', weight=2, style='exotic', cost=5, handed=2, crit_mult='x2', range=10, texture=0)
handcrossbow = Weapon(name='Hand Crossbow', damage='1d4', dmg_style='Piercing', weight=2, style='exotic', cost=100, handed=2, crit_mult='19-20/x2', range=30, texture=0)
repeatingheavycrossbow = Weapon(name='Repeating Heavy Crossbow', damage='1d10', dmg_style='Piercing', weight=12, style='exotic', cost=400, handed=2, crit_mult='19-20/x2', range=120, texture=0)
lightrepeatingcrossbow = Weapon(name='Light Repeating Crossbow', damage='1d8', dmg_style='Piercing', weight=6, style='exotic', cost=250, handed=2, crit_mult='19-20/x2', range=80, texture=0)
padded = Armor(name='Padded', weight=10, speed=30, asfc=5, type='light', bonus=1, acp=0, cost=5, max_bonus=8, texture=2289)
leather = Armor(name='Leather', weight=15, speed=30, asfc=10, type='light', bonus=2, acp=0, cost=10, max_bonus=6, texture=2000)
studdedleather = Armor(name='Studded leather', weight=20, speed=30, asfc=15, type='light', bonus=3, acp=-1, cost=25, max_bonus=5, texture=1999)
chainshirt = Armor(name='Chainshirt', weight=25, speed=30, asfc=20, type='light', bonus=4, acp=-2, cost=100, max_bonus=4, texture=2003)
hide = Armor(name='Hide', weight=25, speed=20, asfc=20, type='medium', bonus=3, acp=-3, cost=15, max_bonus=4, texture=2004)
scalemail = Armor(name='Scalemail', weight=30, speed=20, asfc=25, type='medium', bonus=4, acp=-4, cost=50, max_bonus=3, texture=2285)
chainmail = Armor(name='Chainmail', weight=40, speed=20, asfc=30, type='medium', bonus=5, acp=-5, cost=150, max_bonus=2, texture=2005)
breastplate = Armor(name='Breastplate', weight=30, speed=20, asfc=25, type='medium', bonus=5, acp=-4, cost=200, max_bonus=3, texture=0)
splintmail = Armor(name='Splintmail', weight=45, speed=20, asfc=40, type='heavy', bonus=6, acp=-7, cost=200, max_bonus=0, texture=2292)
bandedmail = Armor(name='Bandedmail', weight=35, speed=20, asfc=35, type='heavy', bonus=6, acp=-6, cost=250, max_bonus=1, texture=2008)
halfplate = Armor(name='Halfplate', weight=50, speed=20, asfc=40, type='heavy', bonus=7, acp=-7, cost=600, max_bonus=0, texture=0)
fullplate = Armor(name='Fullplate', weight=50, speed=20, asfc=35, type='heavy', bonus=8, acp=-6, cost=500, max_bonus=1, texture=0)
buckler = Armor(name='Buckler', weight=5, speed=0, asfc=5, type='shield', bonus=1, acp=-1, cost=15, max_bonus=0, texture=1795)
lightwoodenslield = Armor(name='Light Wooden Shield', weight=5, speed=0, asfc=5, type='shield', bonus=1, acp=-1, cost=3, max_bonus=0, texture=1796)
lightsteelshield = Armor(name='Light Steel Shield', weight=6, speed=0, asfc=5, type='shield', bonus=1, acp=-1, cost=9, max_bonus=0, texture=1801)
heavywoodenshield = Armor(name='Heavy Wooden Shield', weight=10, speed=0, asfc=15, type='shield', bonus=2, acp=-2, cost=7, max_bonus=0, texture=1853)
heavysteelshield = Armor(name='Heavy Steel Shield', weight=15, speed=0, asfc=15, type='shield', bonus=2, acp=-2, cost=20, max_bonus=0, texture=1914)
towershield = Armor(name='Tower Shield', weight=45, speed=0, asfc=50, type='shield', bonus=4, acp=-10, cost=30, max_bonus=2, texture=1798)
