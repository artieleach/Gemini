import numpy as np
from PIL import Image
import math

MAP_Y, MAP_X = MAP_SIZE = (102, 202)

vals = np.array([4, 8, 16,
                 2, 0, 32,
                 1,128, 64]).reshape(3, 3)

def perlin_noise():
    octaves = int(math.log(max(MAP_X, MAP_Y), 2.0))  # 7
    persistence = .9  # perfer higher?
    img_arr = np.zeros(MAP_SIZE)
    rgb_arr = np.zeros((MAP_SIZE[0], MAP_SIZE[1], 3), dtype=np.uint8)
    total_amp = 0.0
    for k in range(octaves):
        freq = 2 ** k
        amp = persistence ** k
        total_amp += amp
        n = freq + 1
        ar = np.random.random(size=(n, n)) * amp
        nx = MAP_X / (n - 1.0)
        ny = MAP_Y / (n - 1.0)
        for ky in range(MAP_Y):
            for kx in range(MAP_X):
                i = int(kx / nx)
                j = int(ky / ny)
                dx0 = kx - i * nx
                dx1 = nx - dx0
                dy0 = ky - j * ny
                dy1 = ny - dy0
                z = ar[j][i] * dx1 * dy1
                z += ar[j][i + 1] * dx0 * dy1
                z += ar[j + 1][i] * dx1 * dy0
                z += ar[j + 1][i + 1] * dx0 * dy0
                z /= nx * ny
                img_arr[ky, kx] += z


    for ky in range(MAP_Y):
        for kx in range(MAP_X):
            rgb_arr[ky, kx] = [int(img_arr[ky, kx] / total_amp * 255)]*3

    return rgb_arr




def play_life(a, iter_num):
    xmax, ymax = a.shape
    b = a.copy()
    for x in range(xmax):
        for y in range(ymax):
            neighbor_count = np.sum(a[max(x - 1, 0):min(x + 2, xmax), max(y - 1, 0):min(y + 2, ymax)]) - a[x, y]
            local_area = a[max(x - 1, 0):min(x + 2, xmax), max(y - 1, 0):min(y + 2, ymax)]

            if 4 <= neighbor_count and a[x, y] or (neighbor_count <= 0 and iter_num < 4):
                b[x, y] = 1
            elif 5 <= neighbor_count or (neighbor_count <= 0 and iter_num < 4):
                b[x, y] = 1
            else:
                b[x, y] = 0
    return b

def reshape_life(a):
    xmax, ymax = a.shape
    b = a.copy()
    for x in range(xmax):
        for y in range(ymax):
            try:
                n = a[x-1:x+2, y-1:y+2]
                if 0 < np.sum(np.multiply(n, vals)) < 128 and a[x, y]:
                    b[x, y] = 2
                elif a[x, y] and np.sum(np.multiply(n, vals)) != 255:
                    b[x, y] = 3
            except ValueError:
                pass
    return b


def gen(density):
    life = np.random.binomial(1, .45, MAP_SIZE)
    for i in range(14):
        life = play_life(life, i)
    life = reshape_life(life)

    G = np.zeros((MAP_SIZE[0], MAP_SIZE[1], 3), dtype=np.uint8)
    G[life==1] = [60,120,30]  # grass
    G[life==3] = [224, 200, 100]  # sand
    G[life==2] = [184, 164, 82]  # sand
    G[life==0] = [32,32,112]  # water

    img = Image.fromarray(G[1:-1, 1:-1], 'RGB')
    img.save('my.png')
    img.resize((MAP_SIZE[1]*5, MAP_SIZE[0]*5)).show()


if __name__ == '__main__':

    img = Image.fromarray(perlin_noise()[1:-1, 1:-1], 'RGB')
    img.save('my.png')
    img.resize((MAP_SIZE[1]*5, MAP_SIZE[0]*5)).show()
    gen(0)
