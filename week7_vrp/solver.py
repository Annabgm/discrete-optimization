#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
import random
import time

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])

def length(customer1, customer2):
    return math.sqrt((customer1.x - customer2.x)**2 + (customer1.y - customer2.y)**2)

def closest_neighbor(remaining_customers, cur_cust, capac_remain, depot, 
                     dist='orig', sort_by='dist'):
    points_to_choose = [cust for cust in remaining_customers if cust.demand <= capac_remain]
    points_length = [length(i, cur_cust)for i in points_to_choose]
    points_length_norm = [0 if i/max(points_length)<=0.33 else (
                          2 if i/max(points_length)>0.66 else 1) for i in points_length]
    points_length_depot = [length(i, depot) for i in points_to_choose]
#    points_length_depot_norm = [0 if i/max(points_length_depot)<=0.33 else (
#                          2 if i/max(points_length_depot)>0.66 else 1) for i in points_length_depot]
    if dist == 'orig':
        points_sort = [(i, -k, j) for i, j, k in zip(points_length, points_to_choose, 
                                                 points_length_depot)]
    else:
        points_sort = [(i, -k, j) for i, j, k in zip(points_length_norm, points_to_choose, 
                                                 points_length_depot)]
    if sort_by == 'dist':
        points_sort.sort(key = lambda x: (x[0], x[1], -x[2].demand))
    else:
        points_sort.sort(key = lambda x: (x[0], -x[2].demand, x[1]))
    return points_sort

def find_obj(vehicle_tours, depot):
    obj = 0
    for v in range(0, len(vehicle_tours)):
        vehicle_tour = vehicle_tours[v]
        if len(vehicle_tour) > 0:
            obj += length(depot,vehicle_tour[0])
            for i in range(0, len(vehicle_tour)-1):
                obj += length(vehicle_tour[i],vehicle_tour[i+1])
            obj += length(vehicle_tour[-1],depot)
    return obj

def next_connect(node, points, prev_node):
    dist_list = [(j, length(node, 
                            points[j])) for j in range(len(points)) if (j!=0)]
    dist_list.sort(key=lambda x: x[1])
    nodes_by_dist = [n for (n,d) in dist_list]
    nodes_by_dist.remove(points.index(prev_node))
    if (random.random() > 0.1) or (len(nodes_by_dist)<2): # 0.6
        return nodes_by_dist[0]
    else:
        return nodes_by_dist[random.randint(1, len(nodes_by_dist)-1)]

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])
    
    customers = []
    for i in range(1, customer_count+1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i-1, int(parts[0]), float(parts[1]), float(parts[2])))

    #the depot is always the first customer in the input
    depot = customers[0] 
    
    # build a trivial solution
    # assign customers to vehicles starting by the largest customer demands
    best_tours = []
    remaining_customers = set(customers)
    remaining_customers.remove(depot)
    
    for v in range(0, vehicle_count):
        # print "Start Vehicle: ",v
        best_tours.append([])
        capacity_remaining = vehicle_capacity
        while sum([capacity_remaining >= customer.demand for customer in remaining_customers]) > 0:
            used = set()
            order = sorted(remaining_customers, key=lambda customer: -customer.demand*customer_count + customer.index)
            for customer in order:
                if capacity_remaining >= customer.demand:
                    capacity_remaining -= customer.demand
                    best_tours[v].append(customer)
                    # print '   add', ci, capacity_remaining
                    used.add(customer)                   
            remaining_customers -= used
    
    best_obj = find_obj(best_tours, depot)

    comb_list = [(i,j) for i in ['orig', 'norm'] for j in ['dist', 'demand']]
    print(f"combination {comb_list}")
    for c in comb_list:
        vehicle_tours = []
        remaining_customers = set(customers)
        remaining_customers.remove(depot)
        
        # solution based on constrain programming
        for v in range(0, vehicle_count):
            # print "Start Vehicle: ",v
            vehicle_tours.append([])
            capacity_remaining = vehicle_capacity
            if len(remaining_customers)>0:
                cust_to_choose = closest_neighbor(remaining_customers, depot, 
                                                  capacity_remaining, depot,
                                                  dist=c[0], sort_by=c[1])[0][2]
                capacity_remaining -= cust_to_choose.demand
                vehicle_tours[v].append(cust_to_choose)
                remaining_customers.remove(cust_to_choose)
                while sum([capacity_remaining >= customer.demand for customer in remaining_customers]) > 0:
                    order = closest_neighbor(remaining_customers, cust_to_choose, 
                                             capacity_remaining, depot,
                                             dist=c[0], sort_by=c[1])
#                    print(f"order {order}")
                    cust_to_choose = order[0][2]
                    capacity_remaining -= cust_to_choose.demand
                    vehicle_tours[v].append(cust_to_choose)
                    remaining_customers.remove(cust_to_choose)
#            print(f"--------------------------------")
                    
        obj_tmp = find_obj(vehicle_tours, depot)
        covered_customers = sum([len(v) for v in vehicle_tours])
        print(f"objective tmp {obj_tmp}, covered cust {covered_customers}")
        if covered_customers == (customer_count-1):
            best_tour2 = []
            tabu_list = []
            for v in range(0, vehicle_count):
                best_tour_unit = vehicle_tours[v]
                track_new = [depot] + best_tour_unit
                obj_tmp  = find_obj([best_tour_unit], depot)
                if len(track_new) > 2:
                    ind = 0
                    tabu_list = []
                    while ind < 5*1e5:
                        start_time = time.time()
                        cust_tmp = random.randint(0, len(track_new)-1)
                        dep1= track_new[cust_tmp]
                        prev = track_new[cust_tmp-1]
                        if track_new[cust_tmp] in tabu_list:
                            pass
                        else:
                            tabu_list.append(track_new[cust_tmp])
                            # revert the list to start with new point
                            track_new = track_new[cust_tmp:]+track_new[:cust_tmp]
                            next_cust = next_connect(dep1, track_new, prev)
                            # n-opt logic, but no more than 5-opt, be sure to stop for big problems
                            if next_cust > 1:
                                track_new = track_new[:1] + track_new[1:next_cust+1][::-1] + track_new[next_cust+1:]
                                track_new = track_new[track_new.index(depot):]+track_new[:track_new.index(depot)]
                                obj_tmp2 = find_obj([track_new[1:]], depot)
                                if obj_tmp2 < obj_tmp:
                                    obj_tmp = obj_tmp2
                                    best_tour_unit = track_new[1:]
                        # tabu list options
                        if len(tabu_list) > len(track_new)*2//3:
                            tabu_list = tabu_list[1:]
                        ind += 1
                        if (time.time() - start_time) >= 120:
                            break
                best_tour2.append(best_tour_unit)
            obj_tmp = find_obj(best_tour2, depot)
        print(f"objective tmp {obj_tmp}, covered cust {covered_customers}")
        if (obj_tmp < best_obj) and (covered_customers == (customer_count-1)):
            best_obj = obj_tmp
            best_tour = best_tour2
    
                
    # checks that the number of customers served is correct
    assert sum([len(v) for v in vehicle_tours]) == len(customers) - 1

    # prepare the solution in the specified output format
    outputData = '%.2f' % best_obj + ' ' + str(0) + '\n'
    for v in range(0, vehicle_count):
        outputData += str(depot.index) + ' ' + ' '.join([str(customer.index) for customer in best_tour[v]]) + ' ' + str(depot.index) + '\n'

    return outputData


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:

        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')

