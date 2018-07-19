import numpy as np
arr = np.random.randint(0, 2, (20, 32), dtype=int)


def life_step(arr):
    nbrs_count = sum(np.roll(np.roll(arr, y, 0), x, 1) for y in (-1, 0, 1) for x in (-1, 0, 1) if (y or x))
    return (nbrs_count == 3) | (arr & (nbrs_count == 2))


for _ in range(4):
    arr = life_step(arr)
else:
    print(str(arr).replace(' ', '').replace('0', ' ').replace('1', '#').replace('[[', '[').replace(']]', ']'))
