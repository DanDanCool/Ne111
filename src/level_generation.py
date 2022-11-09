
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
        X = [
            0,
            self.xMax/3 + random.randint(-self.xMax/16, self.xMax/16),
            self.xMax*2/3 + random.randint(-self.xMax/16, self.xMax/16),
            self.xMax
        ]
        Y = [
            0,
            self.yMax/3 + random.randint(-self.yMax/9, self.yMax/9),
            self.yMax*2/3 + random.randint(-self.yMax/9, self.yMax/9),
            self.yMax
        ]

        r = [[None for i in range(3)] for j in range(3)]

        for i in range(3):
            for j in range(3):
                p0 = (int(self.bias_small_rand(X[j], X[j+1]-self.xRoomMin-1)),
                      int(self.bias_small_rand(Y[i], Y[i+1]-self.yRoomMin-1)))
                d = (int(self.bias_small_rand(self.xRoomMin, min(self.xRoomMax, X[j+1] - p0[0]))),
                     int(self.bias_small_rand(self.yRoomMin, min(self.yRoomMax, Y[i+1] - p0[1]))))
                r[j][i] = (
                    (p0[0], p0[1]),
                    (p0[0] + d[0], p0[1]),
                    (p0[0], p0[1] + d[1]),
                    (p0[0] + d[0], p0[1] + d[1])
                )

        arr = [[0 for i in range(self.yMax)] for j in range(self.xMax)]
        for i in range(3):
            for j in range(3):
                for p in range(0, 4):
                    point1 = r[j][i][p]
                    arr[point1[0]][point1[1]] = 1

                    match p:
                        case 0:
                            point2 = r[j][i][1]
                            for x in range(point1[0]+1, point2[0]):
                                arr[x][point1[1]] = 2
                            
                            point2 = r[j][i][2]
                            for y in range(point1[1]+1, point2[1]):
                                arr[point1[0]][y] = 3
                        case 1:
                            point2 = r[j][i][3]
                            for y in range(point1[1]+1, point2[1]):
                                arr[point1[0]][y] = 3
                        case 2:
                            point2 = r[j][i][3]
                            for x in range(point1[0]+1, point2[0]):
                                arr[x][point1[1]] = 2
        #print("\n\n", arr)
        self.debug(arr)

    def bias_small_rand(self, min, max):
        r = random.random() * random.random()
        return min + (max - min)*r

    def debug(self, arr):
        print("~ "*(self.xMax+2))
        for i in range(self.yMax):
            print("[", end=" ")
            for j in range(self.xMax):
                if arr[j][i] == 0:
                    print(" ", end=" ")
                elif arr[j][i] == 1:
                    print("x", end=" ")
                elif arr[j][i] == 2:
                    print("-", end=" ")
                elif arr[j][i] == 3:
                    print("|", end=" ")
            print("]")
        print("~ "*(self.xMax+2))

l = level_layout_generator()
l.generate_layout()
