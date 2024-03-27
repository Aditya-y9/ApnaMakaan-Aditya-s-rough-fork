matrix = [[0, 1, 1, 1, 1, 0, 0], 
[1, 0, 0, 0, 0, 0, 0], 
[1, 0, 0, 0, 0, 0, 0], 
[1, 0, 0, 0, 0, 1, 0], 
[1, 0, 0, 0, 0, 0, 1], 
[0, 0, 0, 1, 0, 0, 0], 
[0, 0, 0, 0, 1, 0, 0]]



rooms = ["passage", "living_room", "kitchen", "bedroom1", "bedroom2", "wc1", "wc2"]

# Initialize connection lists for each room
passage_connections = []
living_room_connections = []
kitchen_connections = []
bedroom1_connections = []
bedroom2_connections = []
wc1_connections = []
wc2_connections = []

for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        if matrix[i][j] == 1:
            if i == 0:
                passage_connections.append(rooms[j])
            elif i == 1:
                living_room_connections.append(rooms[j])
            elif i == 2:
                kitchen_connections.append(rooms[j])
            elif i == 3:
                bedroom1_connections.append(rooms[j])
            elif i == 4:
                bedroom2_connections.append(rooms[j])
            elif i == 5:
                wc1_connections.append(rooms[j])
            elif i == 6:
                wc2_connections.append(rooms[j])


bedrooms_input = {"bedroom1": bedroom1_connections, "bedroom2": bedroom2_connections}


print("Passage connections: ", passage_connections)
print("Living room connections: ", living_room_connections)
print("Kitchen connections: ", kitchen_connections)
print("Bedroom1 connections: ", bedroom1_connections)
print("Bedroom2 connections: ", bedroom2_connections)
print("WC1 connections: ", wc1_connections)
print("WC2 connections: ", wc2_connections)