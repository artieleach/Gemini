import numpy as np
import time


class Grid:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.status_grid = np.zeros(dimensions, int)
        self.status_grid[8, 6:9] = [1, 1, 1]
        #  self.status_grid = np.random.random_integers(0, 1, dimensions)

    def getneighbors(self, cell):
        neighbors = []
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                xi = cell[0] + x
                yi = cell[1] + y
                if (x or y) and xi >= 0 and yi >= 0 and xi < self.dimensions[0] and yi < self.dimensions[1]:
                    neighbors.append((xi, yi))
        return neighbors

    def run(self):
        buffer_grid = self.status_grid[:]
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                neighbors = self.getneighbors((i, j))
                neighbor_count = 0
                for c in neighbors:
                    neighbor_count += self.status_grid[c]
        self.status_grid = buffer_grid
        print(str(self.status_grid[:]).replace('0', '.').replace('1', '#').replace('[', '').replace(']', ''))


Map = Grid((16, 16))
while __name__ == '__main__':
    Map.run()
    time.sleep(1)
