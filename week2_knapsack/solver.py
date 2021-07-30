#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import numpy as np
Item = namedtuple("Item", ['index', 'value', 'weight'])

def get_estimate(items, density, taken, capacity):
    #dens_tmp = [(i, j) for i, j in density if taken[i] == 1]
    dens_tmp = [j for i, j in density if taken[i] == 1]
    #dens_tmp.sort(key = lambda x: x[1], reverse=True)
    #estimate = 0
    #capacit_estim = 0
    #for i in dens_tmp:
    #    #print(capacit_estim, estimate)
    #    if (capacit_estim + items[i[0]].weight) > capacity:
    #        return round(estimate + (capacity-capacit_estim)*i[1])
    #    else:
    #        capacit_estim += items[i[0]].weight
    #        estimate += items[i[0]].value
    return round(sum(dens_tmp))  #round(estimate)
                            
def recurtion(items, density, taken, room, values, capacity, final):
    estimate = get_estimate(items, density, taken, capacity)
    node_stack = [(values, room, estimate, -1, taken)]
    solution = []
    ts = 0
    while node_stack:
        #node_stack.sort(key = lambda x: x[2])
        state = node_stack.pop()
        val, rom, est, ind, take = state
        #print ("len node_stack {}".format(len(node_stack)))
        if est < final:        
            continue
        else:
            ind += 1
            take1 = take.copy()
            take1[ind] = 0
            est1 = get_estimate(items, density, take1, capacity)
            if ind == (len(take)-1):
                solution.append((val, rom, est1, ind, take1))
                if val > final:
                    final = val
            else:
                node_stack.append((val, rom, est1, ind, take1))
            
            val += items[ind].value
            rom -= items[ind].weight
            if rom >= 0:
                if ind == (len(take)-1):
                    solution.append((val, rom, est, ind, take))
                    if val > final:
                        final = val
                else:
                    node_stack.append((val, rom, est, ind, take))
        ts += 1
        if ts >= capacity*len(taken):
            break
    return solution, final

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items_list = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items_list.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    if item_count <= 500:
        obj = np.zeros((item_count+1, capacity+1))
        
        for item in items_list:
            for j in range(1, capacity+1):
                if item.weight <= j:
                    obj[item.index+1, j] = max(obj[item.index, j], 
                                                 item.value+obj[item.index, j-item.weight])
                else:
                    obj[item.index+1, j] = obj[item.index, j]
                    
        value = obj[item_count, capacity]
        capacity_tmp = capacity
        taken = [0]*item_count
                    
        for item in items_list[::-1]:
            r = obj[item.index+1, capacity_tmp] != obj[item.index, capacity_tmp]
            taken[item.index] = r.astype(int)
            if r:
                capacity_tmp -= item.weight
    else: 
        taken_init = [1]*len(items_list)
        density = [(item.index, item.weight) for item in items_list]
        #density = [(item.index, item.value/item.weight) for item in items]
        solutions, value = recurtion(items_list, density, taken_init, capacity,
                                     0, capacity, 0)
        solutions.sort(key = lambda x: x[0], reverse=True)
        taken = solutions[0][4]
    
    # prepare the solution in the specified output format
    output_data = str(int(value)) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

