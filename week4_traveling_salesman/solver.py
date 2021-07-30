#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import random
from collections import namedtuple
import numpy as np
import time

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def length_path(solution, points):
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, len(solution)-1):
        obj += length(points[solution[index]], points[solution[index+1]])
    return obj

def next_connect(node, points, node_last):
    dist_list = [(j, length(points[node], 
                                points[j])) for j in range(len(points)) if j!=node]
    dist_list.sort(key=lambda x: x[1])
    nodes_by_dist = [n for (n,d) in dist_list]
    nodes_by_dist.remove(node_last)
    if random.random() > 0.75: # 0.6
#        return nodes_by_dist[random.randint(0, len(nodes_by_dist)//2)]
        return nodes_by_dist[0]
    else:
#        return nodes_by_dist[random.randint(len(nodes_by_dist)//2, 
#                                            len(nodes_by_dist)-1)]
        return nodes_by_dist[random.randint(1, len(nodes_by_dist)-1)]

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
#    solution = list(reversed(range(nodeCount)))
    solution = [0]
    dist_list = [(j, length(points[0], 
                             points[j])) for j in range(1, nodeCount)]
    dist_list.sort(key=lambda x: x[1], reverse=True)
    while dist_list:
        next_node = dist_list.pop()
        solution.append(next_node[0])
        nodes_new = [n for (n,d) in dist_list]
        dist_list = [(j, length(points[next_node[0]], 
                             points[j])) for j in nodes_new]
        dist_list.sort(key=lambda x: x[1], reverse=True)

    
    best_obj = length_path(solution, points)
    start_time = time.time()
    
    ind = 0
    ind2 = 0
    tabu_list = []
    while True:
        # choose the random point to start
        node_tmp = random.randint(0, nodeCount-1)
        if node_tmp in tabu_list:
            pass
        else:
            tabu_list.append(node_tmp)
            # revert the list to start with new point
            solution_new = solution[solution.index(node_tmp):]+solution[:solution.index(node_tmp)]
            solution_sets = []
            next_node = next_connect(node_tmp, points, solution_new[-1])
            i_1 = solution_new.index(node_tmp)
            i_2 = solution_new.index(next_node)
            k = 0
            # n-opt logic, but no more than 5-opt, be sure to stop for big problems
            while (i_2 > i_1+1) and (k < 6):
                solution_new = solution_new[:i_1+1] + solution_new[i_1+1:i_2+1][::-1] + solution_new[i_2+1:]
                obj_tmp = length_path(solution_new, points)
                solution_sets.append((obj_tmp, solution_new))
                i_1 = i_2
                next_node = next_connect(solution_new[i_1], points, solution_new[i_1-1])
                i_2 = solution_new.index(next_node)
                k += 1
            solution_sets.sort(key=lambda x: x[0])
            if (len(solution_sets)>0) and (solution_sets[0][0] < best_obj):
                best_obj = solution_sets[0][0]
                solution = solution_sets[0][1]
                ind2 = 0
        # tabu list options
        if len(tabu_list) > nodeCount*2//3:
            tabu_list = tabu_list[1:]
        ind += 1
        ind2 += 1
        if ind%20 == 0:
            solution = solution[::-1]
#        if ind2 == 10**4:
#            solution = best_solution
        # criterion to stop
        if ind2 == 1*10**7: # 5e6
            break
        if (time.time() - start_time) >= 3*60*60:
            break

    # prepare the solution in the specified output format
    output_data = '%.2f' % best_obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

