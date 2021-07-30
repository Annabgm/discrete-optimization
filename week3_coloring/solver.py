#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

def find_node_degree(edges):
    # find number of connection for every node, sorted from smallest to highest
    nodes, counts = np.unique(edges, return_counts=True)
    nodes_degree = [(n, c, 0) for n, c in zip(nodes, counts)]
    nodes_degree.sort(key = lambda x: x[1])
    return nodes_degree

def find_domain(color_list):
    thr = np.max(list(color_list.values()))
    domain = list(range(thr+2))
    return domain
    
def find_connection(edges, node):
    # find nodes connected to node from biggest to smallest
    comb_list = [i for i in edges if node in i]
    connect_nodes = sorted(list(np.unique(comb_list)), reverse=True)
    connect_nodes.remove(node)
    return connect_nodes

def find_uniq_colors(edges, node, color_list):
    l = find_connection(edges, node)
    # if neighbor has already a color, memorise the color
    l = [color_list[i] for i in l if i in color_list.keys()]
    # calculate the number of colors used by neighbors
    out = np.unique(l)
    return len(out)
    
def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
        
    # build a trivial solution
    # every node has its own color
    nodes_degree = find_node_degree(edges)
    color_list = {-1: 0}
    while nodes_degree:
        uniq_col = []
        for i in nodes_degree:
            uniq_col.append(find_uniq_colors(edges, i[0], color_list))
        # to form the list with parameters (node number, number of neighbors,
        # number of neighbors have been checked, uniq number of colors used by neighbors)
        nodes_degree = [(i[0], i[1], i[2], j) for i,j in zip(nodes_degree, uniq_col)]
        nodes_degree.sort(key = lambda x: (x[3], x[1], x[2]))
        state = nodes_degree.pop()
        last_node = state[0]
        # to find the colors could be used for node
        domain = find_domain(color_list)
        connected_nodes = find_connection(edges, last_node)
        nodes_degree = [(i,j,k+1,l) if i in connected_nodes else (i,j,k,l) for i,j,k,l in nodes_degree]
        # delete from domain colors used by neighbors
        for n in connected_nodes:
            if n in color_list.keys() and color_list[n] in domain:
                domain.remove(color_list[n])
        # choose the color from domain
        color_list[last_node] = min(domain)          
                    

    solution = [color_list[i] for i in range(node_count)]
    color_count = max(solution)+1
    # prepare the solution in the specified output format
    output_data = str(color_count) + ' ' + str(0) + '\n'
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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

