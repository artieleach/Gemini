import numpy as np


def generate_perlin_noise_2d(shape, res):
    def f(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


land_masses = {0: 1,
               1: 1,
               2: 1,
               3: 8,
               4: 5,
               5: 66,
               6: 7,
               7: 7}


def num_to_land(arr):
    world_map = np.zeros(shape=arr.shape)
    for cur_line, line in enumerate(arr):
        for cur_pos, spot in enumerate(line):
            world_map[cur_line, cur_pos] = land_masses[arr[cur_line, cur_pos]]
    return world_map


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    np.random.seed(2)
    base_land = generate_perlin_noise_2d((1024, 1024), (8, 8))
    tree_pos = generate_perlin_noise_2d((1024, 1024), (32, 32))
    out_tree = np.array([y * 10 for y in np.around([x * 0.4 + 0.4 for x in tree_pos], decimals=1)])
    out_noise = np.array([y * 10 for y in np.around([x * 0.4 + 0.4 for x in base_land], decimals=1)])
    x = num_to_land(out_noise)
    plt.imshow(out_noise)
    plt.imshow(out_tree)
    plt.show()
