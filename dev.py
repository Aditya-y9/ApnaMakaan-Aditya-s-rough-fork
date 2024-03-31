import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
# from test import population as population_final
from input_converter import *
import random
global i1
i1 = 0
class RoomPlanner(object):
    def __init__(self, PLOT_SIZE=(80, 120), MIN_ROOM_SIZE=(10, 10), NUM_BEDROOMS=2,
                 POPULATION_SIZE=50, NUM_GENERATIONS=500, MUTATION_RATE=2,
                 MAX_MUTATION_PERCENTAGE=0.1, SIZE_INCREASE_FACTOR=1000,
                 COLLISION_RESOLUTION_STEPS=10, MIN_NUM_ROOMS=2,
                 GRID_SIZE=(10, 10), MIN_AREA=10):
        self.PLOT_SIZE = PLOT_SIZE
        self.MIN_ROOM_SIZE = MIN_ROOM_SIZE
        self.NUM_BEDROOMS = NUM_BEDROOMS
        self.POPULATION_SIZE = POPULATION_SIZE
        self.NUM_GENERATIONS = NUM_GENERATIONS
        self.MUTATION_RATE = MUTATION_RATE
        self.MAX_MUTATION_PERCENTAGE = MAX_MUTATION_PERCENTAGE
        self.SIZE_INCREASE_FACTOR = SIZE_INCREASE_FACTOR
        self.COLLISION_RESOLUTION_STEPS = COLLISION_RESOLUTION_STEPS
        self.MIN_NUM_ROOMS = MIN_NUM_ROOMS
        self.GRID_SIZE = GRID_SIZE
        self.MIN_AREA = MIN_AREA
        self.BEDROOM_SIZE = (10, 10)
        self.MIN_KITCHEN_SIZE = (15,15*1.5)
        self.APPROXIMATION_FACTOR = 0.5
        self.MAX_XY_RATIO = 1.8
        self.MIN_XY_RATIO = 1.5
        self.MIN_LIVING_ROOM_SIZE = (20, 20)
        self.BEDROOM_FACTOR = 0.35
        self.KITCHEN_FACTOR = 0.10
        self.LIVING_ROOM_FACTOR = 0.4
        self.MIN_LIVING_ROOM_SIZE = (45,45)


    def generate_initial_population(self):
        population = [] # 1st to last 
        # for _ in range(self.POPULATION_SIZE):
        population.append(self.generate_random_rooms())
        return population

    def generate_narrow_kitchen_neighbour(self, floor_plan, bedrooms, room_cords,shared_sides_passage,shared_sides_kitchen,shared_sides_living_room):
        connection = kitchen_connections

        # Default kitchen size
        kitchen = {'name': 'Kitchen', 'position': (0, 0), 'size': (1, 1)}

        # check 
        # 1. ratio
        # 2. minimum size
        # 3. maximum size
        kitchen['size'] = (np.random.randint(self.MIN_KITCHEN_SIZE[0], 0.2 * self.PLOT_SIZE[0]), np.random.randint(self.MIN_KITCHEN_SIZE[1], 0.3 * self.PLOT_SIZE[1]))


        neighbor = connection[0]
        neighbor_coords = room_cords[neighbor]
        print('this room_cords' + str(room_cords))
        neighbor_position = neighbor_coords
        neighbor_size = room_cords[neighbor + '_size']

        # cancel out sides which are not possible to fit the kitchen

        shared_sides_passage = [side for side in shared_sides_passage if self.check_side(side, neighbor_position, neighbor_size, kitchen['size'])]

        shared_side = random.choice(shared_sides_passage)

        # Calculate kitchen position based on the shared side
        if shared_side == 'left':
            kitchen_position = (neighbor_position[0] - kitchen['size'][0], neighbor_position[1])
        elif shared_side == 'right':
            kitchen_position = (neighbor_position[0] + neighbor_size[0], neighbor_position[1])
        elif shared_side == 'top':
            kitchen_position = (neighbor_position[0], neighbor_position[1] + neighbor_size[1])
        elif shared_side == 'bottom':
            kitchen_position = (neighbor_position[0], neighbor_position[1] - kitchen['size'][1])

        # Ensure the kitchen stays within the plot size
        kitchen_position = (max(0, min(kitchen_position[0], self.PLOT_SIZE[0] - kitchen['size'][0])),
                            max(0, min(kitchen_position[1], self.PLOT_SIZE[1] - kitchen['size'][1])))

        if self.check_collision(kitchen_position, kitchen['size'],room_cords):
            self.resolve_collisions(floor_plan, kitchen_position, kitchen['size'],room_cords)
            kitchen['position'] = kitchen_position
            return kitchen, room_cords, shared_sides_passage, shared_sides_kitchen, shared_sides_living_room
        else:
            kitchen['position'] = kitchen_position
        return kitchen, room_cords , shared_sides_passage, shared_sides_kitchen, shared_sides_living_room
    
    def check_side(self, side, neighbor_position, neighbor_size, kitchen_size):
        if side == 'left':
            return neighbor_position[0] - kitchen_size[0] >= 0
        elif side == 'right':
            return neighbor_position[0] + neighbor_size[0] + kitchen_size[0] <= self.PLOT_SIZE[0]
        elif side == 'top':
            return neighbor_position[1] + neighbor_size[1] + kitchen_size[1] <= self.PLOT_SIZE[1]
        elif side == 'bottom':
            return neighbor_position[1] - kitchen_size[1] >= 0
        return False

    def generate_bedroom_neighbour(self, floor_plan, bedrooms, room_cords, i, shared_sides_passage, shared_sides_kitchen, shared_sides_living_room):
        bedroom1_connections = ["passage"]

        # Default bedroom size
        bedroom = {'name': 'Bedroom' + str(i), 'position': (0, 0), 'size': (30, 30)}

        while bedroom['size'][0] < self.BEDROOM_SIZE[0] or bedroom['size'][1] < self.BEDROOM_SIZE[1]:
            bedroom['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
            if bedroom['size'][0] > self.BEDROOM_FACTOR * self.PLOT_SIZE[0] or bedroom['size'][1] > self.BEDROOM_FACTOR * self.PLOT_SIZE[1]:
                bedroom['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))

        # Get the connection of the bedroom
        connection = bedroom1_connections

        # Get the neighbor room and its coordinates
        neighbor = connection[0]
        if room_cords.get(neighbor) is None:
            # If no neighbor room exists, return the bedroom as is
            return bedroom, room_cords
        neighbor_coords = room_cords[neighbor]
        neighbor_position = neighbor_coords
        neighbor_size = room_cords[neighbor + '_size']

        # verify the positioning does not overlap with passage, kitchen or living room
        shared_sides_passage = [side for side in shared_sides_passage if self.check_side(side, neighbor_position, neighbor_size, bedroom['size'])]
        shared_sides_kitchen = [side for side in shared_sides_kitchen if self.check_side(side, neighbor_position, neighbor_size, bedroom['size'])]
        shared_sides_living_room = [side for side in shared_sides_living_room if self.check_side(side, neighbor_position, neighbor_size, bedroom['size'])]

        shared_sides = list(set(shared_sides_passage) & set(shared_sides_kitchen) & set(shared_sides_living_room))

        if not shared_sides:
            return bedroom, {'name': 'Washroom', 'position': (0, 0), 'size': (0, 0)}, room_cords, shared_sides_passage        
        shared_side = random.choice(shared_sides)

        # Calculate bedroom position based on the shared side
        if shared_side == 'left':
            bedroom_position = (neighbor_position[0] - bedroom['size'][0], neighbor_position[1])
        elif shared_side == 'right':
            bedroom_position = (neighbor_position[0] + neighbor_size[0], neighbor_position[1])
        elif shared_side == 'top':
            bedroom_position = (neighbor_position[0], neighbor_position[1] + neighbor_size[1])
        elif shared_side == 'bottom':
            bedroom_position = (neighbor_position[0], neighbor_position[1] - bedroom['size'][1])

        # Ensure the bedroom stays within the plot size
        bedroom_position = (max(0, min(bedroom_position[0], self.PLOT_SIZE[0] - bedroom['size'][0])),
                            max(0, min(bedroom_position[1], self.PLOT_SIZE[1] - bedroom['size'][1])))

        # Check if the chosen wall is connected to any other room
        # If not connected, place the washroom outside that wall
        free_wall = None
        if shared_side == 'left':
            if 'left' not in room_cords:
                free_wall = 'left'
        elif shared_side == 'right':
            if 'right' not in room_cords:
                free_wall = 'right'
        elif shared_side == 'top':
            if 'top' not in room_cords:
                free_wall = 'top'
        elif shared_side == 'bottom':
            if 'bottom' not in room_cords:
                free_wall = 'bottom'

        # If a free wall is found, place the washroom outside that wall
        if free_wall:
            if free_wall == 'left':
                washroom_position = (bedroom_position[0] - 9, bedroom_position[1])
            elif free_wall == 'right':
                washroom_position = (bedroom_position[0] + bedroom['size'][0], bedroom_position[1])
            elif free_wall == 'top':
                washroom_position = (bedroom_position[0], bedroom_position[1] + 18)
            elif free_wall == 'bottom':
                washroom_position = (bedroom_position[0], bedroom_position[1] - 18)

            # Ensure the washroom stays within the plot size
            washroom_position = (max(0, min(washroom_position[0], self.PLOT_SIZE[0] - 9)),
                                max(0, min(washroom_position[1], self.PLOT_SIZE[1] - 18)))
            


            # Check for collision and resolve if necessary
            if self.check_collision(washroom_position, (9, 18),room_cords):
                self.resolve_collisions(floor_plan, washroom_position, (9, 18),room_cords)
                # Add washroom details to the room_cords
                room_cords[free_wall] = washroom_position
                room_cords[free_wall + '_size'] = (9, 18)
        
        washroom = None
        if free_wall:
            if free_wall == 'left':
                washroom_position = (bedroom_position[0] - 9, bedroom_position[1])
            elif free_wall == 'right':
                washroom_position = (bedroom_position[0] + bedroom['size'][0], bedroom_position[1])
            elif free_wall == 'top':
                washroom_position = (bedroom_position[0], bedroom_position[1] + 18)
            elif free_wall == 'bottom':
                washroom_position = (bedroom_position[0], bedroom_position[1] - 18)

            # Ensure the washroom stays within the plot size
            washroom_position = (max(0, min(washroom_position[0], self.PLOT_SIZE[0] - 9)),
                                max(0, min(washroom_position[1], self.PLOT_SIZE[1] - 18)))

            # Check for collision and resolve if necessary
            if self.check_collision(washroom_position, (9, 18),room_cords):
                self.resolve_collisions(floor_plan, washroom_position, (9, 18),room_cords)
                # Add washroom details to the room_cords
                room_cords[free_wall] = washroom_position
                room_cords[free_wall + '_size'] = (9, 18)
                washroom = {'name': 'Washroom', 'position': washroom_position, 'size': (9, 18)}

        # Check for collision and resolve if necessary for the bedroom
        if self.check_collision(bedroom_position, bedroom['size'],room_cords):
            self.resolve_collisions(floor_plan, bedroom_position, bedroom['size'],room_cords)
            bedroom['position'] = bedroom_position
            return bedroom, washroom, room_cords, shared_sides_passage
        else:
            bedroom['position'] = bedroom_position
        return bedroom, washroom, room_cords, shared_sides_passage
    



    # def generate_washroom_attatched(self, floor_plan, bedrooms, room_cords):

        



    
    
    
    def generate_kitchen(self, floor_plan):
        kitchen = {'position': (0, 0), 'size': (0, 0)}
        while kitchen['size'][0] < self.KITCHEN_SIZE[0] or kitchen['size'][1] < self.KITCHEN_SIZE[1]:
            kitchen['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        corner = np.random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        if corner == 'top_left':
            kitchen['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            kitchen['position'] = (0, self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_left'] = False
        else:
            kitchen['position'] = (self.PLOT_SIZE[0] - kitchen['size'][0], self.PLOT_SIZE[1] - kitchen['size'][1])
            corner_clear['bottom_right'] = False
        if self.check_collision(floor_plan, kitchen['position'], kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen['position'], kitchen['size'])
            return kitchen
        return None
    

    def generate_random_rooms(self):
        print("gen chage")

        floor_plan = np.zeros(self.PLOT_SIZE)

        rooms = {'rooms': [], 'fitness': 0}

        connections = []

        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        
        room_cords = {}

        living_room_wall_clear = {'left': True, 'right': True, 'top': True, 'bottom': True}

        shared_sides_passage = ['left', 'right', 'top', 'bottom']
        shared_sides_kitchen = ['left', 'right', 'top', 'bottom']
        shared_sides_bedroom = ['left', 'right', 'top', 'bottom']
        shared_sides_living_room = ['left', 'right', 'top', 'bottom']

        living_room,corner,room_cords,shared_sides_living_room = self.generate_living_room(floor_plan,corner_clear,room_cords,shared_sides_living_room)
        rooms['rooms'].append(living_room)

        print('this shared sides living room' + str(shared_sides_living_room))

        # generate passage
        passage,room_cords,living_room_wall_clear,shared_sides_living_room = self.generate_passage(floor_plan, living_room,corner,room_cords,living_room_wall_clear,shared_sides_living_room)
        rooms['rooms'].append(passage)

        kitchen,room_cords,shared_sides_passage,shared_sides_kitchen,shared_sides_living_room = self.generate_narrow_kitchen_neighbour(floor_plan, rooms, room_cords,shared_sides_passage,shared_sides_kitchen,shared_sides_living_room)

        print('this shared sides passage' + str(shared_sides_passage))

        rooms['rooms'].append(kitchen)

        # bedroom1,washroom,room_cords,shared_sides_passage = self.generate_bedroom_neighbour(floor_plan, rooms, room_cords,1,shared_sides_passage,shared_sides_kitchen,shared_sides_living_room)

        # rooms['rooms'].append(bedroom1)
        # rooms['rooms'].append(washroom)

        # bedroom2,washroom2,room_cords,shared_sides_passage = self.generate_bedroom_neighbour(floor_plan, rooms, room_cords,2,shared_sides_passage,shared_sides_kitchen,shared_sides_living_room)
        # rooms['rooms'].append(bedroom2)
        # rooms['rooms'].append(washroom2)



        rooms['rooms'].append(self.generate_door(floor_plan, living_room,corner,room_cords)[0])
        # for i in range(self.MIN_NUM_ROOMS):
        #     room_name = f"Room_{i + 1}"
        #     room = self.generate_random_room(floor_plan, room_name)
        #     if room is not None:
        #         rooms['rooms'].append(room)

            # fitness
        rooms['fitness'] = self.calculate_area_fitness(rooms['rooms'])
        return rooms
    
    

    def generate_living_room(self, floor_plan,corner_clear,room_cords,shared_sides_living_room):

        living_room = {'name': 'Living Room', 'position': (0, 0), 'size': (0, 1)}

        living_room['size'] = (self.PLOT_SIZE[0], np.random.randint(self.MIN_LIVING_ROOM_SIZE[1], 0.6 * self.PLOT_SIZE[1]))


        

        # while (living_room['size'][0] <= self.MIN_LIVING_ROOM_SIZE[0] or living_room['size'][1] <= self.MIN_LIVING_ROOM_SIZE[1]) and (living_room['size'][0] / living_room['size'][1] < self.MIN_XY_RATIO or living_room['size'][0] / living_room['size'][1] > self.MAX_XY_RATIO):
        #     living_room['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))

        available = []
        if corner_clear['top_left']:
            available.append('top_left')
        if corner_clear['top_right']:
            available.append('top_right')
        if corner_clear['bottom_left']:
            available.append('bottom_left')
        if corner_clear['bottom_right']:
            available.append('bottom_right')

        corner = np.random.choice(available)
        if corner == 'top_left':
            living_room['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            living_room['position'] = (self.PLOT_SIZE[0] - living_room['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            living_room['position'] = (0, self.PLOT_SIZE[1] - living_room['size'][1])
            corner_clear['bottom_left'] = False
        else:
            living_room['position'] = (self.PLOT_SIZE[0] - living_room['size'][0], self.PLOT_SIZE[1] - living_room['size'][1])
            corner_clear['bottom_right'] = False

        shared_sides_living_room = [side for side in shared_sides_living_room if self.check_side(side, living_room['position'], living_room['size'], living_room['size'])]

        if self.check_collision(living_room['position'], living_room['size'],room_cords):
            self.resolve_collisions(living_room['position'], living_room['size'],room_cords)
            # add living room with its co-ordinates to the room_cords
            room_cords['living_room'] = living_room['position']
            room_cords['living_room_size'] = living_room['size']
            return living_room,corner,room_cords,shared_sides_living_room
        else:
            room_cords['living_room'] = living_room['position']
            room_cords['living_room_size'] = living_room['size']

        return living_room,corner,room_cords,shared_sides_living_room
    

    def generate_passage1(self, floor_plan, room, corner, room_cords):
        # make passage in between the plot with a random +-5% change from center
        # passage should be at the center of the plot


        living_room_position = room_cords['living_room']
        living_room_size = room_cords['living_room_size']

        if self.PLOT_SIZE[0] > self.PLOT_SIZE[1]:
            passage_width = self.PLOT_SIZE[0] // 3
            passage_height = self.PLOT_SIZE[1] // 10
        else:
            passage_width = self.PLOT_SIZE[0] // 10
            passage_height = self.PLOT_SIZE[1] // 3


        # generate passage starting from living room's boundary

        # co-ordinate is the bottom left corner of the room
        # place the passage so that it is 1. not outside the plot
        # 2. not inside the room
            
        if living_room_position[0] - passage_width >= 0 and living_room_position[0] + passage_width <= self.PLOT_SIZE[0] and living_room_position[1] - passage_height >= 0 and living_room_position[1] + passage_height <= self.PLOT_SIZE[1]:
            passage_position = (living_room_position[0] - passage_width, living_room_position[1])
        elif living_room_position[0] - passage_width < 0 and living_room_position[0] + passage_width <= self.PLOT_SIZE[0] and living_room_position[1] - passage_height >= 0 and living_room_position[1] + passage_height <= self.PLOT_SIZE[1]:
            passage_position = (0, living_room_position[1])
        elif living_room_position[0] - passage_width >= 0 and living_room_position[0] + passage_width > self.PLOT_SIZE[0] and living_room_position[1] - passage_height >= 0 and living_room_position[1] + passage_height <= self.PLOT_SIZE[1]:
            passage_position = (living_room_position[0] - passage_width, living_room_position[1])
        elif living_room_position[0] - passage_width >= 0 and living_room_position[0] + passage_width <= self.PLOT_SIZE[0] and living_room_position[1] - passage_height < 0 and living_room_position[1] + passage_height <= self.PLOT_SIZE[1]:
            passage_position = (living_room_position[0], 0)
        elif living_room_position[0] - passage_width >= 0 and living_room_position[0] + passage_width <= self.PLOT_SIZE[0] and living_room_position[1] - passage_height >= 0 and living_room_position[1] + passage_height > self.PLOT_SIZE[1]:
            passage_position = (living_room_position[0], living_room_position[1] - passage_height)
        else:
            passage_position = (0, 0)

        if self.check_collision(floor_plan, passage_position, (passage_width, passage_height)):
            self.resolve_collisions(floor_plan, passage_position, (passage_width, passage_height))
            room_cords['passage'] = passage_position
            room_cords['passage_size'] = (passage_width, passage_height)
            return {'name': 'Passage', 'position': passage_position, 'size': (passage_width, passage_height)},room_cords
        
        return None
    

    def generate_passage(self, floor_plan, room, corner, room_cords, living_room_wall_clear, shared_sides_living_room):
        
        passage_wall_clear = {'left': True, 'right': True, 'top': True, 'bottom': True}
        hall_position = room_cords['living_room']
        hall_size = room_cords['living_room_size']

        # Determine passage width and height based on plot dimensions
        if self.PLOT_SIZE[0] > self.PLOT_SIZE[1]:
            passage_width = int(0.5 * self.PLOT_SIZE[0])
            passage_height = self.PLOT_SIZE[1] // 5
        else:
            passage_width = self.PLOT_SIZE[0] // 5
            passage_height = int(0.5 * self.PLOT_SIZE[1])

        # Determine opposite connecting walls
        opposite_walls = {'left': 'right', 'right': 'left', 'top': 'bottom', 'bottom': 'top'}

        # Determine the connecting wall based on the corner 
        if corner == 'top_left':
            connecting_wall = 'top'
        elif corner == 'top_right':
            connecting_wall = 'top'
        elif corner == 'bottom_left':
            connecting_wall = 'bottom'
        else:
            connecting_wall = 'bottom'

        print('this corner' + str(corner))

        print('this connecting wall' + str(connecting_wall))

        # Calculate the position of the passage based on the connecting wall
        if connecting_wall in ['left', 'right']:
            opposite_wall = opposite_walls[connecting_wall]
            if not living_room_wall_clear[opposite_wall]:
                connecting_wall = opposite_wall

        if connecting_wall == 'left':
            living_room_wall_clear['left'] = False 
            passage_position = (hall_position[0] - passage_width, hall_position[1])
        elif connecting_wall == 'right':
            living_room_wall_clear['right'] = False
            passage_position = (hall_position[0] + hall_size[0], hall_position[1])
        elif connecting_wall == 'top':
            living_room_wall_clear['top'] = False
            passage_position = (hall_position[0], hall_position[1] + hall_size[1])
        elif connecting_wall == 'bottom':
            living_room_wall_clear['bottom'] = False
            passage_position = (hall_position[0], hall_position[1] - passage_height)

        # Ensure the passage stays within the plot boundaries
        passage_position = (
            max(0, min(passage_position[0], self.PLOT_SIZE[0] - passage_width)),
            max(0, min(passage_position[1], self.PLOT_SIZE[1] - passage_height))
        )

        # Check for collision and resolve if necessary
        if self.check_collision(passage_position, (passage_width, passage_height), room_cords):
            self.resolve_collisions(floor_plan,passage_position, (passage_width, passage_height), room_cords)
            # Update room_cords with passage position and size
            room_cords['passage'] = passage_position
            room_cords['passage_size'] = (passage_width, passage_height)
            # Return passage details along with updated room_cords
            return {'name': 'Passage', 'position': passage_position, 'size': (passage_width, passage_height)}, room_cords, living_room_wall_clear, shared_sides_living_room
        else:
            room_cords['passage'] = passage_position
            room_cords['passage_size'] = (passage_width, passage_height)
        return {'name': 'Passage', 'position': passage_position, 'size': (passage_width, passage_height)}, room_cords, living_room_wall_clear, shared_sides_living_room



    


    

        # if(self.PLOT_SIZE[0] > self.PLOT_SIZE[1]):
        #     passage_width = self.PLOT_SIZE[0] // 10
        #     passage_height = self.PLOT_SIZE[1] // 5
        # else:
        #     passage_width = self.PLOT_SIZE[0] // 5
        #     passage_height = self.PLOT_SIZE[1] // 10

        # passage = {'name': 'Passage', 'position': (self.PLOT_SIZE[0] // 2 + random.randint(-0.1,0.1)*self.PLOT_SIZE[0], self.PLOT_SIZE[1] // 2 + random.randint(-0.1,0.1)*self.PLOT_SIZE[1]), 'size': (passage_width, passage_height)}


    # def generate_random_room(self, floor_plan, room_name):
    #     # generate bedrroms and kitchen
    #     # bedrooms = self.generate_bedrooms(floor_plan)
    #     rooms = bedrooms
    #     for room in rooms:
    #         if self.check_collision(floor_plan, room['position'], room['size']):
    #             self.resolve_collisions(floor_plan, room['position'], room['size'])
    #             return room
    #     return None
    
    def generate_door(self, floor_plan, room,corner,room_cords):
        # a quarter circle at one of the corners
        if corner == 'top_left':
            door_position = (room['position'][0], room['position'][1])
        elif corner == 'top_right':
            door_position = (room['position'][0] + room['size'][0], room['position'][1])

        elif corner == 'bottom_left':
            door_position = (room['position'][0], room['position'][1] + room['size'][1])

        else:
            door_position = (room['position'][0] + room['size'][0], room['position'][1] + room['size'][1])
 

        if corner == 'top_left':
            door = {'name':'door','position': (room['position'][0], room['position'][1]), 'size': (5, 5)}
        elif corner == 'top_right':
            door = {'name':'door','position': (room['position'][0] + room['size'][0], room['position'][1]), 'size': (-5, 5)}
        elif corner == 'bottom_left':
            door = {'name':'door','position': (room['position'][0], room['position'][1] + room['size'][1]), 'size': (5, -5)}
        else:
            door = {'name':'door','position': (room['position'][0] + room['size'][0], room['position'][1] + room['size'][1]), 'size': (-5,-5)}
        if self.check_collision(door['position'], door['size'],room_cords):
            self.resolve_collisions(floor_plan, door['position'], door['size'],room_cords)
            room_cords['door'] = door['position']
            return door,room_cords
        else:
            room_cords['door'] = door['position']
        return door,room_cords
    

    def calculate_area_fitness(self, floor_plan):
        total_area = 0
        if type(floor_plan) == dict:
            floor_plan = floor_plan['rooms']
        # high penalty for overlapping rooms
        # print("This FP" + str(floor_plan))
    
        for room in floor_plan:
            # if room['size'][0]<20 or room['size'][1]<20:
            #     # total_area -= 100 * room['size'][0] * room['size'][1]
            #     total_area=0
            #     break 
            # else:
            if room is None:
                continue
            total_area += room['size'][0] * room['size'][1]
            colliding_rooms = self.find_colliding_rooms(room, floor_plan)
            if colliding_rooms:
                # total_area -= 100 * sum(self.overlap_area(room, colliding_room) for colliding_room in colliding_rooms)
                total_area = 0
        return total_area

    def overlap_area(self, room1, room2):
        x_overlap = max(0, min(room1['position'][0] + room1['size'][0], room2['position'][0] + room2['size'][0]) - max(room1['position'][0], room2['position'][0]))
        y_overlap = max(0, min(room1['position'][1] + room1['size'][1], room2['position'][1] + room2['size'][1]) - max(room1['position'][1], room2['position'][1]))
        return x_overlap * y_overlap
    
    def calculate_area_fitness_for_crossover(self, floor_plan):
        total_area = 0
        # floor_plan  = {'rooms': [{'name': 'Living Room', 'position': (5, 61), 'size': (45, 39)}, {'name': 'Passage', 'position': (0, 61), 'size': (5, 33)}, {'name': 'door', 'position': (50, 100), 'size': (-5, -5)}], 'fitness': 1945}
        # print("This FP" + str(floor_plan))
        # print("This FP" + str(floor_plan['rooms']))

        for room in floor_plan['rooms']:
            # print("This room" + str(room))
            total_area += room['size'][0] * room['size'][1]

        # print("This total area" + str(total_area))
        return total_area


    def crossover(self, parent1, parent2, ax):
        # # change the logic
        # parent1 = []
        # parent1.append(paren1)
        # parent2 = []
        # parent2.append(paren2)
        # print("This parent1" + str(parent1))
        offspring1 = {'rooms': [], 'fitness': self.calculate_area_fitness(parent1)}
        offspring2 = {'rooms': [], 'fitness': self.calculate_area_fitness(parent2)}
        # for room in parent1['rooms']:
        #     if np.random.rand() < 0.5:
        #         offspring1['rooms'].append(room)
        #         offspring1['fitness'] = self.calculate_area_fitness(offspring1['rooms'])
        #     else:
        #         offspring2['rooms'].append(room)
        #         offspring2['fitness'] = self.calculate_area_fitness(offspring2['rooms'])
        # for room in parent2['rooms']:
        #     if np.random.rand() > 0.5:
        #         offspring1['rooms'].append(room)
        #         offspring1['fitness'] = self.calculate_area_fitness(offspring1['rooms'])
        #     else:
        #         offspring2['rooms'].append(room)
        #         offspring2['fitness'] = self.calculate_area_fitness(offspring2['rooms'])
        all_rooms=['Living room', 'Bedroom', 'Passage', 'Kitchen', 'Washroom', 'door']
        # for room in parent1['rooms']:
        #     if np.random.rand() < 0.5:
        #         block=0
        #         for room_child in offspring1['rooms']:
        #             if room_child['name']==room['name']:
        #                 block=1
        #         if block==0:
        #             offspring1['rooms'].append(room)
        #     else:
        #         block=0
        #         for room_child in offspring2['rooms']:
        #             if room_child['name']==room['name']:
        #                 block=1
        #         if block==0:
        #             offspring2['rooms'].append(room)
        # for room in parent2['rooms']:
        #     if np.random.rand() > 0.5:
        #         block=0
        #         for room_child in offspring1['rooms']:
        #             if room_child['name']==room['name']:
        #                 block=1
        #         if block==0:
        #             offspring1['rooms'].append(room)
        #     else:
        #         block=0
        #         for room_child in offspring2['rooms']:
        #             if room_child['name']==room['name']:
        #                 block=1
        #         if block==0:
        #             offspring2['rooms'].append(room)
        for room_name in all_rooms:
            if np.random.rand() < 0.5:
                for room in parent1['rooms']:
                    if room is None:
                        continue
                    if(room['name'][0:7]==room_name[0:7]):
                        offspring1['rooms'].append(room)
            else:
                for room in parent2['rooms']:
                    if room is None:
                        continue
                    if(room['name'][0:7]==room_name[0:7]):
                        offspring1['rooms'].append(room)
        for room_name in all_rooms:
            if np.random.rand() < 0.5:
                for room in parent1['rooms']:
                    if room is None:
                        continue
                    if(room['name'][0:7]==room_name[0:7]):

                        offspring2['rooms'].append(room)
            else:
                for room in parent2['rooms']:
                    if room is None:
                        continue
                    if(room['name'][0:7]==room_name[0:7]):
                        offspring2['rooms'].append(room)
        # if len(offspring1['rooms']) != len(parent1['rooms']) or len(offspring2['rooms']) != len(parent2['rooms']):
        #     self.crossover(parent1, parent2, ax)
        offspring1['fitness']=self.calculate_area_fitness(offspring1['rooms'])
        offspring2['fitness']=self.calculate_area_fitness(offspring2['rooms'])

        # self.update_plot(offspring1, ax, 699999999)
        # plt.pause(0.1)
        # plt.draw()
        

        return offspring1, offspring2

    def get_factor(self, name):
        # print(name)
        if(name[0:7]=="Living "):
            return 0.5
        elif(name[0:7]=="Bedroom"):
            return 0.5
        elif(name[0:7]=="Kitchen"):
            return 0.4
        elif name[0:7]=="Passage":
            return 0.2
        elif(name[0:7]=="Washroo"):
            return 0.2

    # @jit(nopython=True)   
    def resolving(self, room1, room2):
        x_diff = min(room1['position'][0]+room1['size'][0], room2['position'][0]+room2['size'][0])-max(room1['position'][0], room2['position'][0])
        y_diff = min(room1['position'][1]+room1['size'][1], room2['position'][1]+room2['size'][1])-max(room1['position'][1], room2['position'][1])
        print(room1)
        print(x_diff)
        print(y_diff)
        print(room2)

        # if x_diff==room1['size'][0]:
        #     room1['position']= (np.random.randint(0, self.PLOT_SIZE[0]-room1['size'][0]), room1['position'][1])
        #     return room1, room2
        # elif x_diff==room2['size'][0]:
        #     room2['position'] = (np.random.randint(0, self.PLOT_SIZE[0]-room2['size'][0]), room2['position'][1])
        #     return room1, room2
        # if y_diff==room1['size'][1]:
        #     room1['position']= (room1['position'][0], np.random.randint(0, self.PLOT_SIZE[0]-room1['size'][1]))
        #     return room1, room2
        # elif x_diff==room2['size'][1]:
        #     room2['position'] = (room2['position'][0],np.random.randint(0, self.PLOT_SIZE[0]-room2['size'][1]))
        #     return room1, room2

        # if room2['position'][0]<room1['position'][0]:
        #     room2['size']=(room2['size'][0]-x_diff, room2['size'][1])
        # elif room2['position'][0]>room1['position'][0]:
        #     room1['size']=(room1['size'][0]-x_diff, room1['size'][1])
        # if room2['position'][1]<room1['position'][1]:
        #     room2['size']=(room2['size'][0], room2['size'][1]-y_diff)
        # elif room2['position'][1]>room1['position'][1]:
        #     room1['size']=(room1['size'][0], room1['size'][1]-y_diff)

        while x_diff>0:
            print("a")
            if room2['position'][0]<room1['position'][0]:
                room2['size']=(room2['size'][0]-1, room2['size'][1])
                x_diff=x_diff-1
                if x_diff:
                    room1['position']=(room1['position'][0]+1, room1['position'][1])
                    room1['size'] = (room1['size'][0]-1, room1['size'][1])
                    x_diff=x_diff-1
            elif room2['position'][0]>=room1['position'][0]:
                room1['size']=(room1['size'][0]-1, room1['size'][1])
                x_diff=x_diff-1
                if x_diff:
                    room2['position']=(room2['position'][0]+1, room2['position'][1])
                    room2['size'] = (room2['size'][0]-1, room2['size'][1])
                    x_diff=x_diff-1
            # else:
            #     print(room1)
            #     print(room2)
            # x_diff=x_diff-1
        while y_diff>0:
            print("b")
            if room2['position'][1]<room1['position'][1]:
                room2['size']=(room2['size'][0], room2['size'][1]-1)
                y_diff=y_diff-1
                if y_diff:
                    room1['position']=(room1['position'][1],room1['position'][1]+1)
                    room1['size'] = (room1['size'][0], room1['size'][1]-1)
                    y_diff=y_diff-1
            elif room2['position'][1]>=room1['position'][1]:
                room1['size']=( room1['size'][0], room1['size'][1]-1)
                y_diff=y_diff-1
                if y_diff:
                    room2['position']=(room2['position'][1], room2['position'][1]+1)
                    room2['size'] = (room2['size'][0], room2['size'][1]-1)
                    y_diff=y_diff-1
            # else:
            # y_diff=y_diff-1

        # first_room_x_overlap = x_diff/room1['size'][0]
        # second_room_x_overlap = x_diff/room2['size'][0]
        # first_room_y_overlap = y_diff/room1['size'][1]
        # second_room_y_overlap = y_diff/room2['size'][1]
        # if second_room_x_overlap<first_room_x_overlap:
        #     room2['size']=(room2['size'][0]-x_diff, room2['size'][1])
        # elif second_room_x_overlap>=first_room_x_overlap:
        #     room1['size']=(room1['size'][0]-x_diff, room1['size'][1])
        # if second_room_y_overlap<first_room_y_overlap:
        #     room2['size']=(room2['size'][0], room2['size'][1]-y_diff)
        # elif second_room_y_overlap>=first_room_y_overlap:
        #     room1['size']=(room1['size'][0], room1['size'][1]-y_diff)

        # if room2['position'][0]<room1['position'][0]:
        #     if (room2['size'][0]-x_diff)/room2['size'][1]<=1.5 and room2['size'][0]-x_diff>self.MIN_ROOM_SIZE[0]:
        #         room2['size']=(room2['size'][0]-x_diff, room2['size'][1])
        #     elif room1['size'][0]-x_diff>self.MIN_ROOM_SIZE[0]:
        #         room1['size']=(room1['size'][0]-x_diff, room1['size'][1])
        # elif room2['position'][0]>room1['position'][0]:
        #     if (room1['size'][0]-x_diff)/room1['size'][1]<=1.5 and room1['size'][0]-x_diff>self.MIN_ROOM_SIZE[0]:
        #         room1['size']=(room1['size'][0]-x_diff, room1['size'][1])
        #     elif room2['size'][0]-x_diff>self.MIN_ROOM_SIZE[0]:
        #         room2['size']=(room2['size'][0]-x_diff, room2['size'][1])
        # if room2['position'][1]<room1['position'][1]:
        #     if room2['size'][0]/(room2['size'][1]-y_diff)<=1.5 and room2['size'][1]-y_diff>self.MIN_ROOM_SIZE[1]:
        #         room2['size']=(room2['size'][0], room2['size'][1]-y_diff)
        #     elif room1['size'][1]-y_diff>self.MIN_ROOM_SIZE[1]:
        #         room1['size']=(room1['size'][0], room1['size'][1]-y_diff)
        # elif room2['position'][1]>room1['position'][1]:
        #     if room1['size'][0]/(room1['size'][1]-y_diff)<=1.5 and room1['size'][1]-y_diff>self.MIN_ROOM_SIZE[1]:
        #         room1['size']=(room1['size'][0], room1['size'][1]-y_diff)
        #     elif room2['size'][1]-y_diff>self.MIN_ROOM_SIZE[1]:
        #         room2['size']=(room2['size'][0], room2['size'][1]-y_diff)

        # if room2['position'][0]<room1['position'][0]:
        #     room2['size']=(room2['size'][0]-(x_diff/2), room2['size'][1])
        #     room1['position']=(room1['position'][0]+(x_diff/2), room1['position'][1])
        #     room1['size']=(room1['size'][0]-(x_diff/2), room1['size'][1])
        # elif room2['position'][0]>room1['position'][0]:
        #     room1['size']=(room1['size'][0]-(x_diff/2), room1['size'][1])
        #     room2['position']=(room2['position'][0]+(x_diff/2), room2['position'][1])
        #     room2['size']=(room2['size'][0]-(x_diff/2), room2['size'][1])
        # if room2['position'][1]<room1['position'][1]:
        #     room2['size']=(room2['size'][0], room2['size'][1]-(y_diff/2))
        #     room1['position']=(room1['position'][0], room1['position'][1]+(y_diff/2))
        #     room1['size']=(room1['size'][0], room1['position'][1]-(y_diff/2))
        # elif room2['position'][1]>room1['position'][1]:
        #     room1['size']=(room1['size'][0], room1['size'][1]-(y_diff/2))
        #     room2['position']=(room2['position'][0], room2['position'][1]+(y_diff/2))
        #     room2['size']=(room2['size'][0], room2['position'][1]-(y_diff/2))

        return room1, room2

    def mutate(self, floor_plan):
        mutated_plan = floor_plan.copy()
        # for room in mutated_plan['rooms']:

        #     # control if room has to be mutated
        #     if np.random.rand() < self.MUTATION_RATE:

        #         # if yes,
        #         # then by how much it has to be mutated
        #         # room cannot be mutated to a size less than the minimum room size and more than the plot size
        #         room['size'] = (min(room['size'][0] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[0]),
        #                         min(room['size'][1] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[1]))

        for room in mutated_plan['rooms']:
            if room and room['name'] != 'door':
                # control if room has to be mutated
                if np.random.rand() < self.MUTATION_RATE:
                    # print("a")
                    # print(room)
                    f = self.get_factor(room['name'])
                    # print(f)
                    x_factor = min(room['size'][0] + self.SIZE_INCREASE_FACTOR, f*self.PLOT_SIZE[0])
                    y_factor = min(room['size'][1] + self.SIZE_INCREASE_FACTOR, f*self.PLOT_SIZE[1])
                    store_size=room['size']
                    store_fit=mutated_plan['fitness']
                    # mutated_plan_store = mutated_plan.copy()
                    if room['position'][0]+x_factor<=self.PLOT_SIZE[0] and room['position'][1]+room['size'][1]<=self.PLOT_SIZE[1]:
                        room['size'] = (x_factor,room['size'][1])

                    col=self.find_colliding_rooms(room, mutated_plan['rooms'])
                    for i in range(0, len(col)):
                        room1, room2=self.resolving(room, col[i])
                        mutated_plan['rooms'][mutated_plan['rooms'].index(room)]=room1
                        mutated_plan['rooms'][mutated_plan['rooms'].index(col[i])]=room2

                    # fit1=self.calculate_area_fitness(mutated_plan['rooms'])
                    # if fit1<store_fit:
                    #     mutated_plan=mutated_plan_store

                    # first_mutation = mutated_plan.copy()
                    if room['position'][0]+room['size'][0]<=self.PLOT_SIZE[0] and room['position'][1]+y_factor<=self.PLOT_SIZE[1]:
                        room['size'] = (room['size'][0], y_factor)
                    col=self.find_colliding_rooms(room, mutated_plan['rooms'])
                    for i in range(0, len(col)):
                        # self.update_plot(mutated_plan, 699999999, ax)
                        # plt.pause(0.1)
                        # plt.draw()
                        room1, room2=self.resolving(room, col[i])
                        mutated_plan['rooms'][mutated_plan['rooms'].index(room)]=room1
                        mutated_plan['rooms'][mutated_plan['rooms'].index(col[i])]=room2

                        # self.update_plot(mutated_plan, 70000000, ax)
                        # plt.pause(0.1)
                        # plt.draw()
                    # fit2=self.calculate_area_fitness(mutated_plan['rooms'])
                    # if fit2<fit1:
                    #     mutated_plan=first_mutation
                    
                    # second_mutation = mutated_plan.copy()
                    if room['position'][0]+room['size'][0]-x_factor>=0:
                        room['position']=(room['position'][0]+room['size'][0]-x_factor, room['position'][1])
                    col=self.find_colliding_rooms(room, mutated_plan['rooms'])
                    for i in range(0, len(col)):
                        room1, room2=self.resolving(room, col[i])
                        mutated_plan['rooms'][mutated_plan['rooms'].index(room)]=room1
                        mutated_plan['rooms'][mutated_plan['rooms'].index(col[i])]=room2
                    # fit3=self.calculate_area_fitness(mutated_plan['rooms'])
                    # if fit3<fit2:
                    #     mutated_plan=second_mutation

                    # third_mutation = mutated_plan.copy()
                    if room['position'][1]+room['size'][1]-y_factor>=0:
                        room['position']=(room['position'][0], room['position'][1]+room['size'][1]-y_factor)
                    col=self.find_colliding_rooms(room, mutated_plan['rooms'])
                    for i in range(0, len(col)):
                        room1, room2=self.resolving(room, col[i])
                        mutated_plan['rooms'][mutated_plan['rooms'].index(room)]=room1
                        mutated_plan['rooms'][mutated_plan['rooms'].index(col[i])]=room2

                
        mutated_plan['fitness']=self.calculate_area_fitness(mutated_plan['rooms'])
        return mutated_plan
    
    def check_collision(self,position, size,room_cords):
        # use room_cords to check collision
        print("This room cords" + str(position))
        x, y = position
        width, height = size
        for room in room_cords:
            print(room)
            room_x = room_cords[room][0]
            room_y = room_cords[room][1]
            room_width = room_cords[room][0]
            room_height = room_cords[room][1]
            if (x < room_x + room_width and x + width > room_x and
                y < room_y + room_height and y + height > room_y):
                return True
        return False
    
    def resolve_collisions(self, floor_plan, position, size,room_cords):
        x, y = position
        width, height = size
        # Reduce the size of the structure until collision is resolved
        while self.check_collision((x, y), (width, height),room_cords):
            if width > height:
                width -= 1
            else:
                height -= 1
            # If width or height becomes zero, break the loop to prevent infinite loop
            if width == 0 or height == 0:
                break
        return (x, y), (width, height)
    
    def plot_rooms(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        for room in rooms:
            print(room)
            # if(room['name'] == 'Door'):
            #     # plot circles for doors
            #     print("done")
            #     position = room['position']
            #     size = room['size']
            #     ax.add_patch(plt.Circle((position[0], position[1]), 5, color='blue'))
            #     continue
            if(room==None):
                continue
            position = room['position']
            size = room['size']
            color = 'black' if room.get('external', False) else 'brown'
            if room['name'] == 'Door':
                rect = plt.Circle((position[0], position[1]), 5, color='blue', fill=True)
            else:
                rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=color, facecolor='none')
            ax.add_patch(rect)

            room_name = room['name']
            room_center = (position[0] + size[0] / 2, position[1] + size[1] / 2)
            ax.text(room_center[0], room_center[1], room_name, fontsize=12, ha='center', va='center')

        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        ax.set_aspect('equal', adjustable='box')
        plt.show()
        # plt.pause(0.5)
        # plt.close(fig)



    def plot_room_boundaries(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        for room in rooms:
            position = room['position']
            size = room['size']
            ax.add_patch(Rectangle(position, size[0], size[1], fill=False, color='brown'))
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        plt.show()

    
    def genetic_plot_rooms(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        # rooms = [{'rooms':[{'name':'Living Room','position':(0,0),'size':(40,40)},{'name':'door','position':(0,0),'size':(5,5)}],'fitness':1600}]
        rooms1 = rooms['rooms']
        for room in rooms1:
                if(room==None):
                    continue
                position = room['position']
                size = room['size']
                color = 'black' if room.get('external', False) else 'brown'
                if room['name'] == 'Door':
                    rect = plt.Circle((position[0], position[1]), 5, color='blue', fill=True)
                else:
                    rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=color, facecolor='none')
                ax.add_patch(rect)

                room_name = room['name']
                room_center = (position[0] + size[0] / 2, position[1] + size[1] / 2)
                ax.text(room_center[0], room_center[1], room_name, fontsize=12, ha='center', va='center')

        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        ax.set_aspect('equal', adjustable='box')
        plt.show()

        # for room in rooms:
        #     # print("meri room")
        #     # print(room)
        #     # if(room['name'] == 'Door'):
        #     #     # plot circles for doors
        #     #     print("done")
        #     #     position = room['position']
        #     #     size = room['size']
        #     #     ax.add_patch(plt.Circle((position[0], position[1]), 5, color='blue'))
        #     #     continue
        #     rooms1 = room['rooms']
        #     for room in rooms1:
        #         if(room==None):
        #             continue
        #         position = room['position']
        #         size = room['size']
        #         color = 'black' if room.get('external', False) else 'brown'
        #         if room['name'] == 'Door':
        #             rect = plt.Circle((position[0], position[1]), 5, color='blue', fill=True)
        #         else:
        #             rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=color, facecolor='none')
        #         ax.add_patch(rect)

        #         room_name = room['name']
        #         room_center = (position[0] + size[0] / 2, position[1] + size[1] / 2)
        #         ax.text(room_center[0], room_center[1], room_name, fontsize=12, ha='center', va='center')

        #     ax.set_xlim(0, self.PLOT_SIZE[0])
        #     ax.set_ylim(0, self.PLOT_SIZE[1])
        #     ax.set_aspect('equal', adjustable='box')
        #     plt.show()


    def plot_room_boundaries(self, rooms):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        for room in rooms:
            position = room['position']
            size = room['size']
            ax.add_patch(Rectangle(position, size[0], size[1], fill=False, color='brown'))
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        plt.show()


    def find_colliding_rooms(self, room, floor_plan):
        colliding_rooms = []
        for other_room in floor_plan:
            if other_room is None:
                continue
            if  room != other_room and other_room['name']!='door':
                if ((room['position'][0] < other_room['position'][0] + other_room['size'][0] and
                    room['position'][0] + room['size'][0] > other_room['position'][0]) and
                    (room['position'][1] < other_room['position'][1] + other_room['size'][1] and
                    room['position'][1] + room['size'][1] > other_room['position'][1])):
                    # or ((room['position'][0] <= other_room['position'][0]+other_room['size'][0]) and (other_room['position'][0] <= room['position'][0]+room['size'][0]) and (room['position'][1] <= other_room['position'][1]+other_room['size'][1]) and (other_room['position'][1] <= room['position'][1]+room['size'][1]))
                    colliding_rooms.append(other_room)
        return colliding_rooms
    
    def resolve_collision(self, room1, room2, expand_walls=True):
        x1, y1, w1, h1 = room1['position'][0], room1['position'][1], room1['size'][0], room1['size'][1]
        x2, y2, w2, h2 = room2['position'][0], room2['position'][1], room2['size'][0], room2['size'][1]
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        if x_overlap < y_overlap:
            room1['size'] = (w1 - x_overlap, h1)
        else:
            room1['size'] = (w1, h1 - y_overlap)
        if expand_walls:
            room1['size'] = self.increase_room_size(room1, self.PLOT_SIZE[0], self.PLOT_SIZE[1])['size']
        return room1
    
    def increase_room_size(self, room, max_width, max_height):
        position = room['position']
        size = room['size']
        available_width = max_width - position[0] - size[0]
        available_height = max_height - position[1] - size[1]
        if available_width > 0 and available_height > 0:
            size = (min(size[0] + available_width, max_width), min(size[1] + available_height, max_height))
        return {'position': position, 'size': size}
    
    def genetic_algorithm(self):

        print("Generating initial population...")

        population = self.generate_initial_population()
        # print(population)
        # return
        # self.plot_rooms(population)

        # -----------------  Genetic Algorithm -----------------

        best_floor_plan = None


        fig, ax = plt.subplots()
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])


        for generation in range(self.NUM_GENERATIONS):
            print(f"Generation {generation + 1}/{self.NUM_GENERATIONS}")


            for floor_plan in population:

                # plan to add fitness to the floor plan
                if best_floor_plan is None or floor_plan['fitness'] > best_floor_plan['fitness']:
                    best_floor_plan = floor_plan
                else:
                    best_floor_plan = best_floor_plan

                if best_floor_plan['fitness'] == np.prod(self.PLOT_SIZE):
                    return best_floor_plan
                
                # if generation % 10 == 0:
                    # self.update_plot(best_floor_plan, ax)
                    # plt.pause(0.1)
                    # plt.draw()

                # if generation % 100 == 0:
                #     print(f"Generation {generation + 1}/{self.NUM_GENERATIONS}, Fitness: {best_floor_plan['fitness']}")
            print('b')
            print(best_floor_plan)
            self.update_plot(best_floor_plan, ax, generation)
            plt.pause(0.1)
            plt.draw()
            parents = self.select_parents(population)
            offspring = []
            for i in range(0, len(parents), 2):
                if(i+1 >= len(parents)):
                    break
                offspring1, offspring2 = self.crossover(parents[i], parents[i + 1], ax)
                offspring.append(self.mutate(offspring1))
                offspring.append(self.mutate(offspring2))

            # now population is the parents and the offspring
            population = parents + offspring


            # back to loop
            # population will keep on increasing


        return best_floor_plan
    
    def select_parents(self, population):

        fitnesses = [floor_plan['fitness'] for floor_plan in population]
        # sort the population based on fitness
        population = [x for _, x in sorted(zip(fitnesses, population), key=lambda pair: pair[0], reverse=True)]

        # choose only the top 10% or 2 parents whichever is greater
        num_parents = max(int(0.1 * self.POPULATION_SIZE), 2)
        parents = population[:num_parents]
        return parents
    
    def update_plot(self, best_floor_plan, ax, generation):
        ax.clear()
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        for room in best_floor_plan['rooms']:
            if room is None:
                continue
            position = room['position']
            size = room['size']
            edge_color = 'BLACK' if room.get('external', False) else 'BROWN'
            rect = Rectangle((position[0], position[1]), size[0], size[1], linewidth=5, edgecolor=edge_color, facecolor='none')
            ax.add_patch(rect)
        plt.title(f'Generation {generation}, Fitness: {best_floor_plan["fitness"]}')
        plt.draw()
        return ax
    
   
    def remove_narrow_rooms(self, rooms):
        for room in rooms:
            if room['size'][0] < self.MIN_ROOM_SIZE[0] or room['size'][1] < self.MIN_ROOM_SIZE[1]:
                rooms.remove(room)
        return rooms
    
    def main(self):
        best_floor_plan = self.genetic_algorithm()
        return best_floor_plan['rooms']
    
    def draw_rooms_pygame(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def boundary_for_walls(self, rooms):
        for room in rooms:
            if room['position'][0] == 0 or room['position'][1] == 0:
                room['external'] = True
        return rooms
    
    def draw_rooms(self, rooms, screen):
        for room in rooms:
            position = room['position']
            size = room['size']
            color = (0, 0, 0) if room.get('external', False) else (0, 0, 0)
            pygame.draw.rect(screen, color, (position[0], position[1], size[0], size[1]), 5)
        return screen
    
    def draw_room_boundaries(self, rooms, screen):
        # draw lines for each room
        # blue lines for external walls
        # black lines for internal walls

        for room in rooms:
            position = room['position']
            size = room['size']
            if room.get('external', False):
                color = (0, 0, 255)
            else:
                color = (0, 0, 0)
            pygame.draw.line(screen, color, (position[0], position[1]), (position[0] + size[0], position[1]), 5)
            pygame.draw.line(screen, color, (position[0], position[1]), (position[0], position[1] + size[1]), 5)
            pygame.draw.line(screen, color, (position[0] + size[0], position[1]), (position[0] + size[0], position[1] + size[1]), 5)
            pygame.draw.line(screen, color, (position[0], position[1] + size[1]), (position[0] + size[0], position[1] + size[1]), 5)

    def get_index(name):
        if name[0:7] == 'Living ':
            return 1
        if name[0:7] == 'Bedroom':
            return 2
        if name[0:7] == 'Washrom':
            return 2
        if name[0:7] == 'Kitchen':
            return 3
        if name[0:7] == 'Passage':
            return 4
        

    def post_processing(self, rooms):
        arr = np.zeros(self.PLOT_SIZE)
        for room in rooms:
            arr[room['position'][0]:room['position'][0]+room['size'][0], room['position'][1]:room['position'][1]+room['size'][1]]= get_index(room['name'])

if __name__ == '__main__':
    import time
    while True:
        planner = RoomPlanner()
        population = planner.generate_initial_population()
        # population = planner.genetic_algorithm()
        # print(population)
        # print("Initial population generated")
        # print("Plotting rooms...")
        # print(population)

        planner.plot_rooms(population[0]['rooms'])



        # population = planner.genetic_algorithm()
        # print("This is " + str(population))

        # planner.genetic_plot_rooms(population)

    # offspring1, offspring2 = planner.crossover(population[0], population[1])
    # planner.plot_rooms(offspring1['rooms'])
    # planner.plot_rooms(offspring2['rooms'])
    # mutated_plan = planner.mutate(population[0])
    # planner.plot_rooms(mutated_plan['rooms'])
    # best_floor_plan = planner.genetic_algorithm()
    # planner.plot_rooms(best_floor_plan['rooms'])