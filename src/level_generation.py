
import random
import math


DEFAULT_SIZE = 6

class level_layout_generator:
    def __init__(self, size=DEFAULT_SIZE, min_room_size = (5,5)):
        # dungeon is kept in a constant 16x9 aspect ratio, size controls the fidelity
        self.x_max = 16*size
        self.y_max = 9*size

        # minimum room is a 5x5 box (leaves a 3x3 floor space open,
        #   always allows for a spawn or exit to be placed)
        self.x_room_min = min_room_size[0]
        self.y_room_min = min_room_size[1]

        # maximum room that can fit in the allocated grid space
        self.xRoomMax = int(self.x_max/3)
        self.yRoomMax = int(self.y_max/3)

        # maximum and minimum number of treasure that can be spawned in a room
        self.min_treasure_spawn = 0
        self.max_treasure_spawn = 3

        # max and min of enemies that can be spawned in a room
        self.min_enemy_spawn = 0
        self.max_enemy_spawn = 3

        # TILE KEYS - Used to avoid writing tiles types as numbers
        self.EMPTY_TILE = 0
        self.CORNER_WALL_TILE = 1
        self.H_WALL_TILE = 2
        self.V_WALL_TILE = 3
        self.FLOOR_TILE = 4
        self.HALLWAY = 5
        self.DOOR = 6
        self.EXIT = 7
        self.SPAWN = 8

        self.ENEMY = 20
        self.TREASURE = 100

        self.PLAYER = 69

    def generate_layout(self, debug=False):
        """

        """
        map_data, room_bounds = self.create_room_layout(debug)
        populated_map = self.add_features(map_data, room_bounds, debug)

        return populated_map
    
    def create_room_layout(self, debug=False):
        """
        Creates a matrix of tile IDs representing a 3x3 collection
        of rooms and the hallways connecting them.
        """
        # algorithm starts by dividng given space into a 3x3 grid,
        # with non-uniform heights and widths for the rows and columns
        # one room will be placed in each grid space (for a total of 9 rooms)

        X = [ #calculate x values for the edges of the 3x3 room grid
            0,
            self.x_max/3 + random.randint(-self.x_max/16, self.x_max/16),
            self.x_max*2/3 + random.randint(-self.x_max/16, self.x_max/16),
            self.x_max
        ]
        Y = [ #calculate y values for the edges of the 3x3 room grid
            0,
            self.y_max/3 + random.randint(-self.y_max/9, self.y_max/9),
            self.y_max*2/3 + random.randint(-self.y_max/9, self.y_max/9),
            self.y_max
        ]

        # initialize room matrix. each [x][y] index stores a tuple containing the
        # coordinates of the 4 corners of room [x][y] in the grid space index
        room_bounds = [[None for i in range(3)] for j in range(3)]

        for i in range(3):
            for j in range(3):
                # looping through each grid space in the room array

                # generate a random point within the grid space to place the top left corner of the room
                # point is biased to be placed closer to the top-left of the grid (to reduce)
                p0 = (int(self.bias_small_rand(X[j], X[j+1]-self.x_room_min-1)),
                      int(self.bias_small_rand(Y[i], Y[i+1]-self.y_room_min-1)))

                # generate a random room length and width that will keep the room within the gridspace
                # dimensions of room are biased to be smaller to keep the rooms well spaceout
                d = (int(self.bias_small_rand(self.x_room_min, min(self.xRoomMax, X[j+1] - p0[0]))),
                     int(self.bias_small_rand(self.y_room_min, min(self.yRoomMax, Y[i+1] - p0[1]))))
                room_bounds[j][i] = ( # create room tuple containing coordinates for the 4 corners ordered as:
                    (p0[0], p0[1]),                 #   0 - - - 1
                    (p0[0] + d[0], p0[1]),          #   |       |
                    (p0[0], p0[1] + d[1]),          #   |       |
                    (p0[0] + d[0], p0[1] + d[1])    #   2 - - - 3
                )

        tile_data = [[0 for i in range(self.y_max)] for j in range(self.x_max)]
        # initializes a (x_max, y_max) array to store the tile type at a specified coordinate
        # place floor, wall, and corner tiles in the grid
        for i in range(3):
            for j in range(3):
                # looping through each grid space in the room array
                for a in range(room_bounds[j][i][0][0], room_bounds[j][i][1][0]+1):
                    for b in range(room_bounds[j][i][0][1], room_bounds[j][i][2][1]+1):
                        if (a == room_bounds[j][i][0][0] or a == room_bounds[j][i][1][0]):
                        # point (a, b) is on the left or right wall of the room
                            tile_data[a][b] = self.V_WALL_TILE
                        elif (b == room_bounds[j][i][0][1] or b == room_bounds[j][i][2][1]):
                        # point (a, b) is on the top or bottom wall of the room
                             tile_data[a][b] = self.H_WALL_TILE
                        else:
                        # point (a, b) is contained within the room
                            tile_data[a][b] = self.FLOOR_TILE

                for p in range(0, 4):
                # sets the coordinates of the room's 4 corners to corner tiles
                    tile_data[room_bounds[j][i][p][0]] [room_bounds[j][i][p][1]] = self.CORNER_WALL_TILE

        if debug:
            self.debug(tile_data, "Room Placement")

        # now hallways connecting the rooms must be generated
        for i in range(0, 3):
            for j in range(0, 2):
                # looping through each vertical edge in the grid space
                # looking at space between room1 (j,i) and room2 (j+1, i)

                r1 = room_bounds[j][i]
                r2 = room_bounds[j+1][i]

                # generate random co-ordinates for the doors
                d1 = (r1[1][0], random.randint(r1[1][1] + 1, r1[3][1] - 1))
                d2 = (r2[0][0], random.randint(r2[0][1] + 1, r2[2][1] - 1))

                # now generate a hallway connecting these two doors
                hallway = self.generate_hallway(d1[0]+1, d1[1], d2[0]-1, d2[1])
                
                # we now add the doors to the tile_data
                tile_data[d1[0]][d1[1]] = self.DOOR
                tile_data[d2[0]][d2[1]] = self.DOOR

                for p in hallway: # loop through hallway list adding hallway tiles
                    tile_data[p[0]][p[1]] = self.HALLWAY

                if (debug):
                #debugs a sub-section of tile_data that contains the generated hallway
                    bounds = (
                        d1[0]-1,
                        d2[0]+2,
                        min(d1[1], d2[1])-1,
                        max(d1[1], d2[1])+2)

                    slice = [tile_data[i][bounds[2]:bounds[3]] for i in range(bounds[0],bounds[1])]
                    self.debug(slice, ("Hallway b/w: (" + str(j) + "," + str(i) + ") & ("+ str(j+1) + "," + str(i) + ")"))

        # repeat previous process for horizontal edges
        for i in range(0, 2):
            for j in range(0, 3):
                # looping through each horizontal edge in the grid space
                # looking at space between room (j,i) and (j, i+1)

                r1 = room_bounds[j][i]
                r2 = room_bounds[j][i+1]

                # generate random co-ordinates for the doors
                d1 = (random.randint(r1[2][0] + 1, r1[3][0] - 1), r1[2][1])
                d2 = (random.randint(r2[0][0] + 1, r2[1][0] - 1), r2[0][1])

                # now we generate a hallway
                hallway = self.generate_hallway(d1[0], d1[1]+1, d2[0], d2[1]-1)

                # we now add doors to the tile_data
                tile_data[d1[0]][d1[1]] = self.DOOR
                tile_data[d2[0]][d2[1]] = self.DOOR

                for p in hallway: # loop through hallway list adding points
                    tile_data[p[0]][p[1]] = self.HALLWAY

                if (debug):
                #debugs a sub-section of tile_data that contains the generated hallway
                    bounds = (
                        min(d1[0], d2[0])-1,
                        max(d1[0], d2[0])+2,
                        d1[1]-1,
                        d2[1]+2)

                    slice = [tile_data[i][bounds[2]:bounds[3]] for i in range(bounds[0],bounds[1])]
                    self.debug(slice, ("Hallway b/w: (" + str(j) + "," + str(i) + ") & ("+ str(j+1) + "," + str(i) + ")"))

        if debug:
            self.debug(tile_data, "Hallway Placement")

        return (tile_data, room_bounds)

    def generate_hallway(self, start_x, start_y, end_x, end_y):
        """
        Generates a hallway connecting the two given points.
        The hallway is represented as a list of coordinates
        the hallway passes through
        """
        # create a 2-dim element storing the current coordinate
        # (initialize it as the first coordinate of the hallway)
        # add that point to the hallway list
        pointer = [start_x, start_y]
        hallway = [tuple(pointer)]
        # find the distance needed to get from the start point to the end point
        d = [end_x - start_x, end_y - start_y]

    #
        #           -1:left, 1:right                  -1:up, 1:down
        dir = [int(math.copysign(1 , d[0])), int(math.copysign(1 , d[1]))]
        # verify if the hallway is straight or not (copysign(0) does not return 0)
        if d[0] == 0:
            dir[0] = 0
        if d[1] == 0:
            dir[1] = 0
        
        # iterate the pointer towards the final position, adding each point
        # it passes through to the hallway list
        counter = 0
        while(pointer[0] != end_x or pointer[1] != end_y):
            r = random.randint(0, 1) # pick a random direction to move
            pointer[r] = pointer[r] + dir[r] # update pointer poitiion and distance to end point
            d[r] = d[r] - dir[r]
            hallway.append(tuple(pointer))
            
            if d[r] == 0:
                # if the pointer is now parallel to the door, our direction will no longer work.
                # draw a straight line to the last point
                nr = (r+1)%2
                while d[nr] != 0:
                    pointer[nr] = pointer[nr] + dir[nr]
                    d[nr] = d[nr] - dir[nr]
                    hallway.append(tuple(pointer))

            counter += 1 #if the hallway is taking too long to generate, break loop (should never trigger)
            if counter > 10000:
                print(TimeoutError, ": could not generate hallway")
                break
        
        return hallway

    def add_features(self, tile_data, room_bounds, debug=False):
        """
        Adds features to the given tile_map, including enemy spawns,
        trasure spawns, and the level exit and start points.
        """

        for i in range(3):
            for j in range(3):
                # looping through each grid space in the room array
                
                if i != 1 and j != 1: # skips the spawn room
                    # we don't want to place treasures here!
                
                    # generate a random number of treasure spawns in the room (biased to have less loot)
                    t_max = int(self.bias_small_rand(self.min_treasure_spawn, self.max_treasure_spawn))
                    if t_max > 0:
                        for t in range(t_max): # for each spawn, generate a random point for the treasure
                            item_coor = (random.randint(room_bounds[j][i][0][0]+1, room_bounds[j][i][1][0]-1),
                                random.randint(room_bounds[j][i][0][1]+1, room_bounds[j][i][2][1]-1))
                            # add that treasure point to the tile data
                            tile_data[item_coor[0]][item_coor[1]] = self.TREASURE

                # generate a random number of enemies in the room
                #   (by flipping the min and the max in the bias_small_rand function,
                #   code biases room to have more enemies)
                e_max = int(self.bias_small_rand(self.max_enemy_spawn, self.min_enemy_spawn))
                if e_max > 0:
                    for e in range(e_max): # for each of these enemies, place them randomly in the room
                        # *NOTE* these could overlap with treasure tiles, but this will just result in less loot for the player
                        enemy_coor = (random.randint(room_bounds[j][i][0][0]+1, room_bounds[j][i][1][0]-1),
                            random.randint(room_bounds[j][i][0][1]+1, room_bounds[j][i][2][1]-1))
                        tile_data[enemy_coor[0]][enemy_coor[1]] = self.ENEMY

        # finally add player spawn and level exit
        # player spawn is randomly placed in the center room
        spawn_coor = (random.randint(room_bounds[1][1][0][0]+2, room_bounds[1][1][1][0]-2),
                      random.randint(room_bounds[1][1][0][1]+2, room_bounds[1][1][2][1]-2))
        tile_data[spawn_coor[0]][spawn_coor[1]] = self.SPAWN

        # the exit is randomly placed in any room
        # *NOTE* that both are placed at least one space from the wall to avoid blocking any doors
        exit_room = room_bounds[random.randint(0,2)][random.randint(0,2)]
        exit_coor = (random.randint(exit_room[0][0]+2, exit_room[1][0]-2),
                     random.randint(exit_room[0][1]+2, exit_room[2][1]-2))
        tile_data[exit_coor[0]][exit_coor[1]] = self.EXIT

        if debug:
            self.debug(tile_data, "Final Product")

        return tile_data



    # Helper Functions

    def bias_small_rand(self, min, max):
        """ 
        Generates a random value between the given minimum and maximum.
        Distribution is biased to return values closer to the minimum
        """
        r = (random.random() * random.random() + random.random())/2 
        return min + (max - min)*r

    def debug(self, arr, title=None):
        """
        Creates an ASCII preview of the given tile matrix
        Possible characters to print with:
            ☺☻♥♦♣♠♫☼►◄↕‼¶§▬↨↑↓→∟↔▲▼
            123456789:;<=>?@
            ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`
            abcdefghijklmnopqrstuvwxyz{|}~⌂
        """

        if (title != None):
            print("Debugging Step:", title)

        X = len(arr)
        Y = len(arr[0])
        print(X, "x", Y)

        print("~ "*(X+2))
        for i in range(Y):
            print("[", end=" ")
            for j in range(X):
                match arr[j][i]:
                    # check for map tiles
                    case self.EMPTY_TILE:
                        print(" ", end=" ")
                    case self.CORNER_WALL_TILE:
                        print("x", end=" ")
                    case self.H_WALL_TILE:
                        print("—", end=" ")
                    case self.V_WALL_TILE:
                        print("|", end=" ")
                    case self.FLOOR_TILE:
                        print(".", end=" ")
                    case self.HALLWAY:
                        print("#", end=" ")

                    case self.DOOR:
                        print("D", end=" ")
                    case self.SPAWN:
                        print("S", end=" ")
                    case self.EXIT:
                        print("⌂", end=" ")

                    
                    case self.PLAYER:
                        print("\x0c", end=" ")
                    case self.ENEMY:
                        print("E", end=" ")
                    case self.TREASURE:
                        print("T", end=" ")
                       

                    case _: # displays a tile without a specified symbol as (‼)
                        print("\x13", end=" ")
                        
            print("]")
        print("~ "*(X+2))

# uncomment for testing
#l = level_layout_generator(6)
#l.generate_layout(True)