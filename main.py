from nsga2.problem import Problem
from nsga2.evolution import Evolution
from utils import DataUtils
import matplotlib.pyplot as plt


data = DataUtils('./dataset/base_stations_min.csv', './dataset/data_min.csv')

num_of_bs = 2700
num_of_es = 100

problem = Problem(num_of_bs, num_of_es, [(0, num_of_es - 1)], data.base_stations, data.distances)
evo = Evolution(problem, mutation_param=20)
func = [i.objectives for i in evo.evolve()]

function1 = [i[0] for i in func]
function2 = [i[1] for i in func]
plt.xlabel('Latency Objective', fontsize=15)
plt.ylabel('Workload Objective', fontsize=15)
plt.scatter(function1, function2)
plt.show()
