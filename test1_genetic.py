import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
# from test import population as population_final
from input_converter import *
import random
global i1
i1 = 0

class RoomPlanner(object):
    def __init__(self, PLOT_SIZE=(50, 100), MIN_ROOM_SIZE=(10, 10), NUM_BEDROOMS=2,
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
        self.KITCHEN_SIZE = (10, 20)
        self.APPROXIMATION_FACTOR = 0.5
        self.MAX_XY_RATIO = 1.5
        self.MIN_XY_RATIO = 1
        self.MIN_LIVING_ROOM_SIZE = (20, 20)  # Ensure the living room size meets the minimum requirements



    def generate_initial_population(self):
    
        population = [] # 1st to last 


        for _ in range(self.POPULATION_SIZE):
            population.append(self.generate_random_rooms())
        return population
    
    def generate_bedrooms(self, floor_plan):
        bedrooms = []
        for i in range(self.NUM_BEDROOMS-2):
            print(f"Generating bedroom {i + 1}...")
            bedroom_name = f"Bedroom {i + 1}"
            bedrooms.append(self.generate_proper_bedroom(floor_plan, bedroom_name, bedrooms))
        return bedrooms
    
    
    def generate_proper_bedroom(self, floor_plan, bedroom_name, bedrooms):
        # take into consideration the minimum size of the bedroom
        # and the approximation factor
        bedroom = {'name': bedroom_name, 'position': (0, 0), 'size': (0, 0)}
        
        while bedroom['size'][0] < self.BEDROOM_SIZE[0] or bedroom['size'][1] < self.BEDROOM_SIZE[1]:
            bedroom['size'] = (np.random.randint(1, self.PLOT_SIZE[0]), np.random.randint(1, self.PLOT_SIZE[1]))
        corner_clear = {'top_left': True, 'top_right': True, 'bottom_left': True, 'bottom_right': True}
        existing_room_cords = {}
        corner = np.random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        if corner == 'top_left':
            bedroom['position'] = (0, 0)
            corner_clear['top_left'] = False
        elif corner == 'top_right':
            bedroom['position'] = (self.PLOT_SIZE[0] - bedroom['size'][0], 0)
            corner_clear['top_right'] = False
        elif corner == 'bottom_left':
            bedroom['position'] = (0, self.PLOT_SIZE[1] - bedroom['size'][1])
            corner_clear['bottom_left'] = False
        else:
            bedroom['position'] = (self.PLOT_SIZE[0] - bedroom['size'][0], self.PLOT_SIZE[1] - bedroom['size'][1])
            corner_clear['bottom_right'] = False
        if self.check_collision(floor_plan, bedroom['position'], bedroom['size']):
            self.resolve_collisions(floor_plan, bedroom['position'], bedroom['size'])
            return bedrooms.append(bedroom)
        return bedrooms.append(bedroom)
    
    
    def generate_narrow_kitchen(self, floor_plan, bedrooms):
    
        kitchen = {'name': 'Kitchen', 'position': (0, 0), 'size': (0, 0)}

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
    
    def generate_narrow_kitchen(self, floor_plan, bedrooms,connection,room_cords):

        connection = ["passage"]


        # default kitchen size
        kitchen = {'name': 'Kitchen', 'position': (0, 0), 'size': (15,24)}

        neigbour  =  connection[0]
        room_cords = room_cords[neigbour]
        neigbour_position = room_cords['position']
        neigbour_size = room_cords['size']

        # put kitchen next to neighbour after checking the position of the neighbour and plot boundary

        if neigbour_position[0] - kitchen['size'][0] >= 0 and neigbour_position[0] + kitchen['size'][0] <= self.PLOT_SIZE[0] and neigbour_position[1] - kitchen['size'][1] >= 0 and neigbour_position[1] + kitchen['size'][1] <= self.PLOT_SIZE[1]:
            kitchen_position = (neigbour_position[0] - kitchen['size'][0], neigbour_position[1])
        elif neigbour_position[0] - kitchen['size'][0] < 0 and neigbour_position[0] + kitchen['size'][0] <= self.PLOT_SIZE[0] and neigbour_position[1] - kitchen['size'][1] >= 0 and neigbour_position[1] + kitchen['size'][1] <= self.PLOT_SIZE[1]:
            kitchen_position = (0, neigbour_position[1])
        elif neigbour_position[0] - kitchen['size'][0] >= 0 and neigbour_position[0] + kitchen['size'][0] > self.PLOT_SIZE[0] and neigbour_position[1] - kitchen['size'][1] >= 0 and neigbour_position[1] + kitchen['size'][1] <= self.PLOT_SIZE[1]:
            kitchen_position = (neigbour_position[0] - kitchen['size'][0], neigbour_position[1])
        elif neigbour_position[0] - kitchen['size'][0] >= 0 and neigbour_position[0] + kitchen['size'][0] <= self.PLOT_SIZE[0] and neigbour_position[1] - kitchen['size'][1] < 0 and neigbour_position[1] + kitchen['size'][1] <= self.PLOT_SIZE[1]:
            kitchen_position = (neigbour_position[0], 0)
        elif neigbour_position[0] - kitchen['size'][0] >= 0 and neigbour_position[0] + kitchen['size'][0] <= self.PLOT_SIZE[0] and neigbour_position[1] - kitchen['size'][1] >= 0 and neigbour_position[1] + kitchen['size'][1] > self.PLOT_SIZE[1]:
            kitchen_position = (neigbour_position[0], neigbour_position[1] - kitchen['size'][1])
        else:
            kitchen_position = (0, 0)


        if self.check_collision(floor_plan, kitchen['position'], kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen['position'], kitchen['size'])
            return kitchen
        return None
    

    def generate_narrow_kitchen_neigbour(self, floor_plan, bedrooms, room_cords):
        connection = kitchen_connections

        # Default kitchen size
        kitchen = {'name': 'Kitchen', 'position': (0, 0), 'size': (10,16)}

        neighbor = connection[0]
        neighbor_coords = room_cords[neighbor]
        print('this room_cords' + str(room_cords))
        neighbor_position = neighbor_coords
        neighbor_size = room_cords[neighbor + '_size']

        # Determine the side of the neighbor to share the wall with
        shared_side = random.choice(['left', 'right', 'top', 'bottom'])

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

        if self.check_collision(floor_plan, kitchen_position, kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen_position, kitchen['size'])
            kitchen['position'] = kitchen_position
            return kitchen, room_cords
        return None, room_cords
    
    def generate_narrow_bedroom_neigbour(self, floor_plan, bedrooms, room_cords,i):

        connection = bedroom1_connections

        # Default kitchen size
        kitchen = {'name': 'Bedroom' + str(i), 'position': (0, 0), 'size': (20,20)}
        neighbor = connection[0]
        if room_cords.get(neighbor) == None:
            return {'name': 'Bedroom' + str(i), 'position': (0, 0), 'size': (20,20)}, room_cords
        neighbor_coords = room_cords[neighbor]
        print('this room_cords' + str(room_cords))
        neighbor_position = neighbor_coords
        neighbor_size = room_cords[neighbor + '_size']

        # Determine the side of the neighbor to share the wall with
        shared_side = random.choice(['left', 'right', 'top', 'bottom'])

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

        if self.check_collision(floor_plan, kitchen_position, kitchen['size']):
            self.resolve_collisions(floor_plan, kitchen_position, kitchen['size'])
            kitchen['position'] = kitchen_position
            # i1 = i1 + 1
            return kitchen, room_cords
        # i1 = i1 + 1
        return None, room_cords


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

        living_room,corner,room_cords = self.generate_living_room(floor_plan,corner_clear,room_cords)
        rooms['rooms'].append(living_room)

        # generate passage
        passage,room_cords,living_room_wall_clear = self.generate_passage(floor_plan, living_room,corner,room_cords,living_room_wall_clear)
        rooms['rooms'].append(passage)

        kitchen,room_cords = self.generate_narrow_kitchen_neigbour(floor_plan, rooms, room_cords)

        rooms['rooms'].append(kitchen)

        kitchen,room_cords = self.generate_narrow_bedroom_neigbour(floor_plan, rooms, room_cords,1)

        rooms['rooms'].append(kitchen)

        # bedroom,room_cords = self.generate_narrow_bedroom_neigbour(floor_plan, rooms, room_cords,2)
        # rooms['rooms'].append(bedroom)



        rooms['rooms'].append(self.generate_door(floor_plan, living_room,corner,room_cords)[0])
        for i in range(self.MIN_NUM_ROOMS):
            room_name = f"Room_{i + 1}"
            room = self.generate_random_room(floor_plan, room_name)
            if room is not None:
                rooms['rooms'].append(room)

            # fitness
            rooms['fitness'] = self.calculate_area_fitness(rooms['rooms'])
        return rooms
    
    

    def generate_living_room(self, floor_plan,corner_clear,room_cords):

        living_room = {'name': 'Living Room', 'position': (0, 0), 'size': (self.PLOT_SIZE[0], self.PLOT_SIZE[1])}


        # while living_room['size'][0] < self.MIN_LIVING_ROOM_SIZE[0] or living_room['size'][1] < self.MIN_LIVING_ROOM_SIZE[1] or living_room['size'][0] / living_room['size'][1] < self.MIN_XY_RATIO or living_room['size'][0] / living_room['size'][1] > self.MAX_XY_RATIO:
        #     living_room['size'] = (np.random.randint(0.1*self.PLOT_SIZE[0], 0.3*self.PLOT_SIZE[0]), np.random.randint(0.1*self.PLOT_SIZE[1], 0.3*self.PLOT_SIZE[1]))

        while True:
            width = np.random.randint(0.2 * self.PLOT_SIZE[0], 0.35 * self.PLOT_SIZE[0])
            height = np.random.randint(0.2 * self.PLOT_SIZE[1], 0.35 * self.PLOT_SIZE[1])
            if (self.MIN_LIVING_ROOM_SIZE[0] <= width <= self.PLOT_SIZE[0] and
                self.MIN_LIVING_ROOM_SIZE[1] <= height <= self.PLOT_SIZE[1]):
                break
            
        # Set the living room size
        living_room['size'] = (width, height)


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

        if self.check_collision(floor_plan, living_room['position'], living_room['size']):
            self.resolve_collisions(floor_plan, living_room['position'], living_room['size'])
            # add living room with its co-ordinates to the room_cords
            room_cords['living_room'] = living_room['position']
            room_cords['living_room_size'] = living_room['size']
            return living_room,corner,room_cords
        return None
    

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
    

    def generate_passage(self, floor_plan, room, corner, room_cords, living_room_wall_clear):
        
        passage_wall_clear = {'left': True, 'right': True, 'top': True, 'bottom': True}
        hall_position = room_cords['living_room']
        hall_size = room_cords['living_room_size']

        # Determine passage width and height based on plot dimensions
        if self.PLOT_SIZE[0] > self.PLOT_SIZE[1]:
            passage_width = self.PLOT_SIZE[0] // 3
            passage_height = self.PLOT_SIZE[1] // 4
        else:
            passage_width = self.PLOT_SIZE[0] // 4
            passage_height = self.PLOT_SIZE[1] // 3

        # Determine opposite connecting walls
        opposite_walls = {'left': 'right', 'right': 'left', 'top': 'bottom', 'bottom': 'top'}

        # Randomly select a wall of the hall to connect the passage to
        connecting_wall = random.choice(['left', 'right', 'top', 'bottom'])

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
        if self.check_collision(floor_plan, passage_position, (passage_width, passage_height)):
            self.resolve_collisions(floor_plan, passage_position, (passage_width, passage_height))
            # Update room_cords with passage position and size
            room_cords['passage'] = passage_position
            room_cords['passage_size'] = (passage_width, passage_height)
            # Return passage details along with updated room_cords
            return {'name': 'Passage', 'position': passage_position, 'size': (passage_width, passage_height)}, room_cords, living_room_wall_clear

        return None


    


    

        # if(self.PLOT_SIZE[0] > self.PLOT_SIZE[1]):
        #     passage_width = self.PLOT_SIZE[0] // 10
        #     passage_height = self.PLOT_SIZE[1] // 5
        # else:
        #     passage_width = self.PLOT_SIZE[0] // 5
        #     passage_height = self.PLOT_SIZE[1] // 10

        # passage = {'name': 'Passage', 'position': (self.PLOT_SIZE[0] // 2 + random.randint(-0.1,0.1)*self.PLOT_SIZE[0], self.PLOT_SIZE[1] // 2 + random.randint(-0.1,0.1)*self.PLOT_SIZE[1]), 'size': (passage_width, passage_height)}


    def generate_random_room(self, floor_plan, room_name):
        # generate bedrroms and kitchen
        bedrooms = self.generate_bedrooms(floor_plan)
        rooms = bedrooms
        for room in rooms:
            if self.check_collision(floor_plan, room['position'], room['size']):
                self.resolve_collisions(floor_plan, room['position'], room['size'])
                return room
        return None
    
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
        if self.check_collision(floor_plan, door['position'], door['size']):
            self.resolve_collisions(floor_plan, door['position'], door['size'])
            room_cords['door'] = door['position']
            return door,room_cords
        return None
    

    def calculate_area_fitness(self, floor_plan):
        total_area = 0
        if type(floor_plan) == dict:
            floor_plan = floor_plan['rooms']
        # high penalty for overlapping rooms
        # print("This FP" + str(floor_plan))
    
        for room in floor_plan:
            total_area += room['size'][0] * room['size'][1]
            colliding_rooms = self.find_colliding_rooms(room, floor_plan)
            if colliding_rooms:
                total_area -= 100 * sum(self.overlap_area(room, colliding_room) for colliding_room in colliding_rooms)
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


    def crossover(self, parent1, parent2):
        # # change the logic
        # parent1 = []
        # parent1.append(paren1)
        # parent2 = []
        # parent2.append(paren2)
        # print("This parent1" + str(parent1))
        offspring1 = {'rooms': [], 'fitness': self.calculate_area_fitness(parent1)}
        offspring2 = {'rooms': [], 'fitness': self.calculate_area_fitness(parent2)}
        for room in parent1['rooms']:
            if np.random.rand() < 0.5:
                offspring1['rooms'].append(room)
                offspring1['fitness'] = self.calculate_area_fitness(offspring1['rooms'])
            else:
                offspring2['rooms'].append(room)
                offspring2['fitness'] = self.calculate_area_fitness(offspring2['rooms'])
        for room in parent2['rooms']:
            if np.random.rand() > 0.5:
                offspring1['rooms'].append(room)
                offspring1['fitness'] = self.calculate_area_fitness(offspring1['rooms'])
            else:
                offspring2['rooms'].append(room)
                offspring2['fitness'] = self.calculate_area_fitness(offspring2['rooms'])
        

        return offspring1, offspring2

    def mutate(self, floor_plan):
        mutated_plan = floor_plan.copy()
        for room in mutated_plan['rooms']:

            # control if room has to be mutated
            if np.random.rand() < self.MUTATION_RATE:

                # if yes,
                # then by how much it has to be mutated
                # room cannot be mutated to a size less than the minimum room size and more than the plot size
                room['size'] = (min(room['size'][0] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[0]),
                                min(room['size'][1] + self.SIZE_INCREASE_FACTOR, self.PLOT_SIZE[1]))
                

        return mutated_plan
    
    def check_collision(self, floor_plan, position, size):
        x, y = position
        width, height = size
        return np.all(floor_plan[y:y + height, x:x + width] == 0)
    
    def resolve_collisions(self, floor_plan, position, size):
        # reduce the wall size till it fits
        # and till collision is resolved
        x, y = position
        width, height = size
        while not self.check_collision(floor_plan, (x, y), (width, height)):
            if width > height:
                width -= 1
            else:
                height -= 1
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

    def find_colliding_rooms(self, room, floor_plan):
        colliding_rooms = []
        for other_room in floor_plan:
            # print()
            # print(other_room)
            # print()
            if room != other_room:
                if ((room['position'][0] < other_room['position'][0] + other_room['size'][0] and
                    room['position'][0] + room['size'][0] > other_room['position'][0]) or
                    (room['position'][1] < other_room['position'][1] + other_room['size'][1] and
                    room['position'][1] + room['size'][1] > other_room['position'][1])):
                    colliding_rooms.append(other_room)
        return colliding_rooms

    
    import numpy as np

# class YourFloorPlanGenerator:
    def genetic_algorithm(self):
        print("Generating initial population...")
        population = self.generate_initial_population()
        best_floor_plan = None

        for generation in range(self.NUM_GENERATIONS):
            print(f"Generation {generation + 1}/{self.NUM_GENERATIONS}")
            for floor_plan in population:
                if best_floor_plan is None or self.calculate_area_fitness(floor_plan['rooms']) > self.calculate_area_fitness(best_floor_plan['rooms']):
                    best_floor_plan = floor_plan
                if self.calculate_area_fitness(best_floor_plan['rooms']) == np.prod(self.PLOT_SIZE):
                    return best_floor_plan

            parents = self.select_parents(population)
            offspring = []

            for i in range(0, len(parents), 2):
                if i + 1 >= len(parents):
                    break
                offspring1, offspring2 = self.crossover(parents[i], parents[i + 1])
                offspring.append(self.mutate(offspring1))
                offspring.append(self.mutate(offspring2))

            population = parents + offspring

        return best_floor_plan

    def calculate_area_fitness(self, floor_plan):
        total_area = 0
        for room in floor_plan:
            area = room['size'][0] * room['size'][1]
            total_area += area
            if (room['position'][0] + room['size'][0] > self.PLOT_SIZE[0]) or (room['position'][1] + room['size'][1] > self.PLOT_SIZE[1]):
                total_area -= 100 * area
            colliding_rooms = self.find_colliding_rooms(room, floor_plan)
            if colliding_rooms:
                total_area -= 100 * sum(self.overlap_area(room, colliding_room) for colliding_room in colliding_rooms)
        return total_area

    def crossover(self, parent1, parent2):
        offspring1 = {'rooms': [], 'fitness': 0}
        offspring2 = {'rooms': [], 'fitness': 0}

        for room in parent1['rooms']:
            if np.random.rand() < 0.5:
                block = 0
                for room_child in offspring1['rooms']:
                    if room_child['name'] == room['name']:
                        block = 1
                if block == 0:
                    offspring1['rooms'].append(room)
            else:
                block = 0
                for room_child in offspring2['rooms']:
                    if room_child['name'] == room['name']:
                        block = 1
                if block == 0:
                    offspring2['rooms'].append(room)
        for room in parent2['rooms']:
            if np.random.rand() > 0.5:
                block = 0
                for room_child in offspring1['rooms']:
                    if room_child['name'] == room['name']:
                        block = 1
                if block == 0:
                    offspring1['rooms'].append(room)
            else:
                block = 0
                for room_child in offspring2['rooms']:
                    if room_child['name'] == room['name']:
                        block = 1
                if block == 0:
                    offspring2['rooms'].append(room)

        offspring1['fitness'] = self.calculate_area_fitness(offspring1['rooms'])
        offspring2['fitness'] = self.calculate_area_fitness(offspring2['rooms'])
        return offspring1, offspring2

    def mutate(self, floor_plan):
        mutated_plan = floor_plan.copy()
        tot_area = self.PLOT_SIZE[0] * self.PLOT_SIZE[1]
        for room in mutated_plan['rooms']:
            if room['name'] != 'door':
                x_room = min(self.PLOT_SIZE[0], room['position'][0] + room['size'][0]) - room['position'][0]
                y_room = min(self.PLOT_SIZE[1], room['position'][1] + room['size'][1]) - room['position'][1]
                available_area = tot_area - x_room * y_room
                if np.random.rand() < self.MUTATION_RATE:
                    x_factor = min(room['size'][0] + self.SIZE_INCREASE_FACTOR, 0.7 * self.PLOT_SIZE[0])
                    y_factor = min(room['size'][1] + self.SIZE_INCREASE_FACTOR, 0.7 * self.PLOT_SIZE[1])
                    store_size = room['size']
                    if room['position'][0] + x_factor <= self.PLOT_SIZE[0] and room['position'][1] + y_factor <= self.PLOT_SIZE[1]:
                        room['size'] = (x_factor, y_factor)
                    col = self.find_colliding_rooms(room, mutated_plan['rooms'])
                    if col:
                        room['size'] = store_size

        mutated_plan['fitness'] = self.calculate_area_fitness(mutated_plan['rooms'])
        return mutated_plan

    def select_parents(self, population):
        population.sort(key=lambda x: x['fitness'], reverse=True)
        num_parents = max(int(0.1 * self.POPULATION_SIZE), 2)
        parents = population[:num_parents]
        return parents

    def update_plot(self, best_floor_plan, generation, ax):
        ax.clear()
        ax.set_xlim(0, self.PLOT_SIZE[0])
        ax.set_ylim(0, self.PLOT_SIZE[1])
        for room in best_floor_plan['rooms']:
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
    
    def find_colliding_rooms(self, room, floor_plan):
        colliding_rooms = []
        for other_room in floor_plan:
            # print()
            # print(other_room)
            # print()
            if room != other_room:
                if ((room['position'][0] < other_room['position'][0] + other_room['size'][0] and
                    room['position'][0] + room['size'][0] > other_room['position'][0]) or
                    (room['position'][1] < other_room['position'][1] + other_room['size'][1] and
                    room['position'][1] + room['size'][1] > other_room['position'][1])):
                    colliding_rooms.append(other_room)
        return colliding_rooms

    def overlap_area(self, room1, room2):
        x_overlap = max(0, min(room1['position'][0] + room1['size'][0], room2['position'][0] + room2['size'][0]) - max(room1['position'][0], room2['position'][0]))
        y_overlap = max(0, min(room1['position'][1] + room1['size'][1], room2['position'][1] + room2['size'][1]) - max(room1['position'][1], room2['position'][1]))
        return x_overlap * y_overlap

    
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

    def genetic_plot_rooms(self, floor_plan):
        fig, ax = plt.subplots()
        border = Rectangle((0, 0), self.PLOT_SIZE[0], self.PLOT_SIZE[1], fill=False, color='brown')
        ax.add_patch(border)
        
        rooms = floor_plan['rooms']
        for room in rooms:
            if room is None:
                continue
            position = room['position']
            size = room['size']
            color = 'black' if room.get('external', False) else 'brown'
            if room['name'] == 'door':
                # rect = Circle((position[0], position[1]), 5, color='blue', fill=True)
                pass
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

if __name__ == '__main__':
    import time
    while True:
        planner = RoomPlanner()
        population = planner.generate_initial_population()
        print(population)
        print("Initial population generated")
        print("Plotting rooms...")
        print(population)

        planner.plot_rooms(population[0]['rooms'])


        # population = planner.genetic_algorithm()
        # # print("This is " + str(population))
        # print("Plotting rooms..." + str(population))

        # planner.genetic_plot_rooms(population)

    # offspring1, offspring2 = planner.crossover(population[0], population[1])
    # planner.plot_rooms(offspring1['rooms'])
    # planner.plot_rooms(offspring2['rooms'])
    # mutated_plan = planner.mutate(population[0])
    # planner.plot_rooms(mutated_plan['rooms'])
    # best_floor_plan = planner.genetic_algorithm()
    # planner.plot_rooms(best_floor_plan['rooms'])