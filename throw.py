import tmx
import numpy as np
import timeit
import random

current_map = 'overworld'
raw_maps = {}
loc_array = {}



a = [[[1], [2], [3], [4]],
     [[5], [6], [7], [8]]]
b = [[1, 2, 3, 4], [5, 6, 7, 8]]



map_file = tmx.TileMap.load('./Maps/overworld.tmx')
file_name = 'overworld'
raw_maps[file_name] = []
for layer in map_file.layers:
    map_data = []
    for tile in layer.tiles:
        map_data.append(tile.gid)
    if len(map_file.layers) > 1:
        raw_maps[file_name].append(np.flip(np.array(map_data, dtype=int).reshape((map_file.height, map_file.width)), 0))

new_arr = []
for arr in raw_maps['overworld']:
    for lis_pos, lis in enumerate(arr):
        for item_pos, item in enumerate(lis):
            try:
                new_arr[item_pos+(lis_pos*200)].append(item)
            except:
                new_arr.append([])
                new_arr[item_pos+(lis_pos*200)].append(item)







four_array = np.array(new_arr)
four_list = new_arr
reg_arr = raw_maps[file_name]

m = timeit.Timer(lambda: random.choice(random.choice(four_array)))
n = timeit.Timer(lambda: random.choice(random.choice(four_list)))
o = timeit.Timer(lambda: random.choice(random.choice(random.choice(reg_arr))))

print('Stacked Array: {:.3}s\nStacked List: {:.3}s\nUnstacked Array: {:.3}s'.format(m.timeit(), n.timeit(), o.timeit()))






















