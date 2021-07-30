#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
import cvxpy as cp
import numpy as np
import time

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    start_time = time.time()
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))
    
    # build a trivial solution    
    init_solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    facility_index = 0
    for customer in customers:
        if capacity_remaining[facility_index] >= customer.demand:
            init_solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand
        else:
            facility_index += 1
            assert capacity_remaining[facility_index] >= customer.demand
            init_solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand

    used = np.array([0]*len(facilities))
    for facility_index in init_solution:
        used[facility_index] = 1
            
    cust_pos_init = np.zeros((facility_count, customer_count))
#    print(len(init_solution), customer_count)
    for c in range(customer_count):
        cust_pos_init[init_solution[c], c] = 1
    
    if facility_count<2000:
        cap_var = np.array([f.capacity for f in facilities])
        cost_var = np.array([f.setup_cost for f in facilities])
        demand_var = np.array([c.demand for c in customers]).reshape(-1,1)
        dist_m = np.zeros((facility_count, customer_count))
        for f in facilities:
            for c in customers:
                dist_m[f.index, c.index] = length(f.location, c.location)
        median_dist = np.quantile(dist_m, 0.8, axis=0)
    #    print(median_dist)
        
        x = cp.Variable(facility_count, boolean=True)
    #    print(cp.multiply(dist_m, cp.reshape(x,(x.shape[0],1))))
        y = cp.Variable((facility_count, customer_count), boolean=True)
        objective = cp.Minimize(cp.sum(cost_var*x)+cp.sum(cp.multiply(y,dist_m)))
        constraints = [#y*demand_var <= cp.reshape(cap_var*x, (-1,1)),
                       cp.sum(y, axis=0) == 1,
                        cp.sum(cp.multiply(y,dist_m), axis=0) <= median_dist]
    #                   0 <= x, x <= 1,
    #                   0 <= y, y <= 1]
        for i in range(facility_count):
            constraints += [
                np.sum(y[i] * demand_var) <= cap_var[i]*x[i],
                y[i] <= x[i]
            ]
        prob = cp.Problem(objective, constraints)
        x.value = used
        y.value = cust_pos_init
        obj = prob.solve(solver=cp.MOSEK, verbose=True, warm_start=True,
                         mosek_params = {#'MSK_IPAR_OPTIMIZER':'optimizertype.mixed_int',
                             'MSK_DPAR_MIO_TOL_REL_GAP': 3*1e-2,
                        'MSK_DPAR_MIO_MAX_TIME':7200})
    #    print(x.value)
    #    print(y.value)
    
        solution = [np.argmax(y.value[:,i]) for i in range(customer_count)]
    else:
        solution = init_solution
            # calculate the cost of the solution
        obj = sum([f.setup_cost*used[f.index] for f in facilities])
        for customer in customers:
            obj += length(customer.location, facilities[solution[customer.index]].location)
    print(f"duration of task: {time.time() - start_time}")

    # build a trivial solution
    # pack the facilities one by one until all the customers are served
#    solution = [-1]*len(customers)
#    capacity_remaining = [f.capacity for f in facilities]
#
#    facility_index = 0
#    for customer in customers:
#        if capacity_remaining[facility_index] >= customer.demand:
#            solution[customer.index] = facility_index
#            capacity_remaining[facility_index] -= customer.demand
#        else:
#            facility_index += 1
#            assert capacity_remaining[facility_index] >= customer.demand
#            solution[customer.index] = facility_index
#            capacity_remaining[facility_index] -= customer.demand
#
#    used = [0]*len(facilities)
#    for facility_index in solution:
#        used[facility_index] = 1
#
#    # calculate the cost of the solution
#    obj = sum([f.setup_cost*used[f.index] for f in facilities])
#    for customer in customers:
#        obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

