import numpy as np

def generate_population(adj_matrix, room_areas, room_labels):
    population = []
    num_rooms = len(adj_matrix)

    # Initialize rooms with None
    rooms = [None] * num_rooms

    # Create rooms based on adjacency matrix
    for i in range(num_rooms):
        if rooms[i] is None:
            room_name = room_labels[i]
            position = (0, 0)
            size = (np.sqrt(room_areas[room_name]), np.sqrt(room_areas[room_name]))
            rooms[i] = {'name': room_name, 'position': position, 'size': size}

            # Find connected rooms

            # Get indices of connected rooms
            # 
            connected_rooms = [j for j in range(num_rooms) if adj_matrix[i][j] == 1]
            for connected_room in connected_rooms:
                if rooms[connected_room] is None:
                    connected_room_name = room_labels[connected_room]
                    # Set position and size of connected rooms
                    if i == 0:
                        # Set position to the right of the first room
                        position = (rooms[i]['position'][0] + rooms[i]['size'][0], rooms[i]['position'])
                    else:
                        # Set position to the right of the last connected room
                        position = (rooms[i]['position'][0] + rooms[i]['size'][0], rooms[i]['position'][1])
                    size = (np.sqrt(room_areas[connected_room_name]), np.sqrt(room_areas[connected_room_name]))
                    rooms[connected_room] = {'name': connected_room_name, 'position': position, 'size': size}

    population.append(rooms)
    return population

# Test the function
adj_matrix = [[0, 1, 1, 1],
              [1, 0, 0, 0],
              [1, 0, 0, 0],
              [1, 0, 0, 0]]

room_areas = {'Living Room': 50,
              'Kitchen': 20,
              'Bedroom': 30,
              'Bathroom': 15}

room_labels = {
    0: "Living Room",
    1: "Kitchen",
    2: "Bedroom",
    3: "Bathroom",
}

population = generate_population(adj_matrix, room_areas, room_labels)
print(population)
