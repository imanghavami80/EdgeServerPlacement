import logging
from nsga2.problem import Problem
from nsga2.evolution import Evolution
import matplotlib.pyplot as plt
from utils import DataUtils


logging.basicConfig(level=logging.INFO)
data = DataUtils('./dataset/base_stations_min.csv', './dataset/data_min.csv')

problem = Problem(1, [(0, 99)], 2700, 100, data.base_stations, data.distances)
evo = Evolution(problem, mutation_param=20)
func = [i.objectives for i in evo.evolve()]

function1 = [i[0] for i in func]
function2 = [i[1] for i in func]
plt.xlabel('Function 1', fontsize=15)
plt.ylabel('Function 2', fontsize=15)
plt.scatter(function1, function2)
plt.show()