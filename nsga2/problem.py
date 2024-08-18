from data.base_station import BaseStation
from data.edge_server import EdgeServer
from nsga2.individual import Individual
from utils import DataUtils
import random
from typing import List
import numpy as np


class Problem:

    def __init__(self, num_of_base_stations, num_of_edge_servers, variables_range, base_stations: List[BaseStation], distances: List[List[float]]):
        self.num_of_objectives = 2
        self.num_of_variables = 1
        self.num_of_base_stations = num_of_base_stations
        self.num_of_edge_servers = num_of_edge_servers
        self.variables_range = variables_range
        self.base_stations = base_stations[:num_of_base_stations].copy()
        self.distances = distances

    def generate_individual(self):
        individual = Individual()
        
        matrix = [[0] * self.num_of_base_stations for _ in range(self.num_of_edge_servers)]        
        available_rows = list(range(self.num_of_edge_servers))
        
        for base_station in range(self.num_of_base_stations):
            if not available_rows:
                available_rows = list(range(self.num_of_edge_servers))
            row_index = random.choice(available_rows)
            matrix[row_index][base_station] = 1
            available_rows.remove(row_index)
        
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
        edge_servers = [EdgeServer(i, 0, 0, 0) for i in range(self.num_of_edge_servers)]
        for index, value in enumerate(individual.features):
            edge_servers[int(value)].assigned_base_stations.append(self.base_stations[index])
            edge_servers[int(value)].workload += self.base_stations[index].workload

        for es in edge_servers:
            min_distance = 1e10
            best_base_station = BaseStation(0, 0, 0, 0)
            for candidate_bs in es.assigned_base_stations:
                candidate_total_distance = sum(self.distances[candidate_bs.id][bs.id] for bs in es.assigned_base_stations)
                if candidate_total_distance < min_distance:
                    min_distance = candidate_total_distance
                    best_base_station = candidate_bs
            
            es.latitude = best_base_station.latitude
            es.longitude = best_base_station.longitude
            es.base_station_id = best_base_station.id

        individual.objectives = [
            self.objective_latency(edge_servers),
            self.objective_workload(edge_servers)
        ]

    def _distance_edge_server_base_station(self, edge_server: EdgeServer, base_station: BaseStation) -> float:
        if edge_server.base_station_id:
            return self.distances[edge_server.base_station_id][base_station.id]
        return DataUtils.calc_distance(edge_server.latitude, edge_server.longitude, base_station.latitude,
                                       base_station.longitude)

    def objective_latency(self, edge_servers: List[EdgeServer]):
        assert edge_servers
        total_delay = 0
        for es in edge_servers:
            for bs in es.assigned_base_stations:
                delay = self._distance_edge_server_base_station(es, bs)
                total_delay += delay
        return total_delay
    
    def objective_workload(self, edge_servers: List[EdgeServer]):
        assert edge_servers
        workloads = [e.workload for e in edge_servers]
        res = np.std(workloads)
        return res