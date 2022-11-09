
from asyncio.windows_events import NULL
import random


class level_layout_generator:
    def __init__(self, size=6):
        self.xMax = 16*size
        self.yMax = 9*size

        self.xRoomMin = 5
        self.xRoomMax = int(self.xMax/3 - self.xRoomMin)

        self.yRoomMin = 5
        self.yRoomMax = int(self.yMax/3 - self.yRoomMin)

    def generate_layout(self):
        x = [
            0,
            self.xMax/3 + random.randint(-self.xMax/16, self.xMax/16),
            self.xMax*2/3 + random.randint(-self.xMax/16, self.xMax/16),
            self.xMax
        ]
        y = [
            0,
            self.yMax/3 + random.randint(-self.yMax/9, self.yMax/9),
            self.yMax*2/3 + random.randint(-self.yMax/9, self.yMax/9),
            self.yMax
        ]

        r = [[-1]*3]*3

        for i in range(3):
            for j in range(3):
                p0 = (int(self.bias_small_rand(x[j], x[j+1]-1)),
                      int(self.bias_small_rand(y[i], y[i+1]-1)))
                d = (int(self.bias_small_rand(self.xRoomMin, min(self.xRoomMax, x[j+1] - p0[0]))),
                     int(self.bias_small_rand(self.yRoomMin, min(self.yRoomMax, y[i+1] - p0[1]))))
                r[j][i] = (
                    (p0[0], p0[1]),
                    (p0[0] + d[0], p0[1]),
                    (p0[0], p0[1] + d[1]),
                    (p0[0] + d[0], p0[1] + d[1])
                )

                print("r:", r[j][i])
                print(r)

        print()
        print()

        arr = [[0]*self.yMax]*self.xMax
        for i in range(3):
            for j in range(3):
                print(j, i, r[j][i], "--", r[0][i])
                for p in range(0, 4):
                    point = r[j][i][p]
                    print(p, ":", r[j][i][p], "-> 2")
                    arr[point[0]][point[1]] = 2

        #print("\n\n", arr)
        # self.debug(arr)
        # -------

    def bias_small_rand(self, min, max):
        r = random.random() * random.random()
        return min + (max - min)*r

    def debug(self, arr):
        for i in range(self.yMax):
            for j in range(self.xMax):
                if arr[j][i] == 0:
                    print(" ", end=" ")
                elif arr[j][i] == 2:
                    print("|", end=" ")
                elif arr[j][i] == 1:
                    print("-", end=" ")
            print("")


l = level_layout_generator()
l.generate_layout()
