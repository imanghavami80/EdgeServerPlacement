from data.base_station import BaseStation
import random
import os
import pandas as pd
import pickle
from functools import wraps
from math import sqrt
from typing import List


def memorize(filename):
    
    def _memorize(func):
        @wraps(func)
        def memorized_function(*args, **kwargs):
            key = pickle.dumps(args[1:])

            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    cached = pickle.load(f)
                    f.close()
                    if isinstance(cached, dict) and cached.get('key') == key:
                        return cached['value']

            value = func(*args, **kwargs)
            with open(filename, 'wb') as f:
                cached = {'key': key, 'value': value}
                pickle.dump(cached, f)
                f.close()
            return value

        return memorized_function

    return _memorize


class DataUtils(object):
    def __init__(self, location_file, user_info_file):
        self.base_station_locations = self.base_station_reader(location_file)
        self.base_stations = self.user_info_reader(user_info_file)
        self.distances = self.distance_between_stations()

    @memorize('cache/base_stations')
    def base_station_reader(self, path: str):
        bs_data = pd.read_csv(path, header=0, index_col=0)
        base_stations = []
        for index, bs_info in bs_data.iterrows():
            base_stations.append(BaseStation(id=index, addr=bs_info['address'], lat=bs_info['latitude'], lng=bs_info['longitude']))
        return base_stations

    @memorize('cache/base_stations_with_user_info')
    def user_info_reader(self, path: str) -> List[BaseStation]:
        assert self.base_station_locations

        self.address_to_id = {bs.address: bs.id for bs in self.base_station_locations}

        req_data = pd.read_csv(path, header=0, index_col=0)
        req_data['start time'] = pd.to_datetime(req_data['start time'])
        req_data['end time'] = pd.to_datetime(req_data['end time'])
        for index, req_info in req_data.iterrows():
            service_time = (req_info['end time'] - req_info['start time']).seconds / 60
            bs_id = self.address_to_id[req_info['address']]
            self.base_station_locations[bs_id].num_users += 1
            self.base_station_locations[bs_id].workload += service_time
        return self.base_station_locations

    @staticmethod
    def _shuffle(l: List):
        random.seed(6767)
        random.shuffle(l)

    @staticmethod
    def calc_distance(lat_a, lng_a, lat_b, lng_b):
        return sqrt((lat_b - lat_a) ** 2 + (lng_b - lng_a) ** 2)

    @memorize('cache/distances')
    def distance_between_stations(self) -> List[List[float]]:
        assert self.base_stations
        base_stations = self.base_stations
        distances = []
        for i, station_a in enumerate(base_stations):
            distances.append([])
            for j, station_b in enumerate(base_stations):
                dist = DataUtils.calc_distance(station_a.latitude, station_a.longitude, station_b.latitude,
                                               station_b.longitude)
                distances[i].append(dist)
        return distances
    