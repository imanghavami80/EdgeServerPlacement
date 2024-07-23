from nsga2.individual import Individual
import random


class Problem:

    def __init__(self, objectives, num_of_base_stations, num_of_edge_servers, expand=True):
        self.num_of_objectives = len(objectives)
        self.num_of_base_stations = num_of_base_stations
        self.num_of_edge_servers = num_of_edge_servers
        self.objectives = objectives
        self.expand = expand

    def generate_individual(self):
        individual = Individual()
        
        # Initialize a 2D matrix with zeros
        matrix = [[0] * self.num_of_base_stations for _ in range(self.num_of_edge_servers)]
        
        # Ensure each column has exactly one 1
        for base_station in range(self.num_of_base_stations):
            edge_server = random.randint(0, self.num_of_edge_servers - 1)
            matrix[edge_server][base_station] = 1
        
        # Encode the 2D matrix to a 1D array
        individual.features = self.encode_matrix(matrix)
        return individual
    
    def encode_matrix(self, matrix):
        encoded = []
        for base_station in range(self.num_of_base_stations):
            for edge_server in range(self.num_of_edge_servers):
                if matrix[edge_server][base_station] == 1:
                    encoded.append(edge_server)
                    break
        return encoded

    def decode_to_matrix(self, encoded):
        matrix = [[0] * self.num_of_base_stations for _ in range(self.num_of_edge_servers)]
        for base_station, edge_server in enumerate(encoded):
            matrix[edge_server][base_station] = 1
        return matrix

    def calculate_objectives(self, individual):
        if self.expand:
            individual.objectives = [f(*individual.features) for f in self.objectives]
        else:
            individual.objectives = [f(individual.features) for f in self.objectives]
