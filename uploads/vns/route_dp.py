from typing import List
import sys

import numpy as np

from vrp3d.solution import Solution
from vrp3d.vrp3d import VRP3D
from vrp3d.utils import compute_arrival_time_list
"""
    if we have fixed routes, 
    then we can do 1 last attempt
    to optimize the route
    if the route happens to have <=32 nodes to visit
"""
def backtrack(node_idx_list: np.ndarray,
              current_node_idx:int, 
              bin_mask: int):
    global memo, distance_matrix
    num_nodes = len(node_idx_list)
    current_node = node_idx_list[current_node_idx]
    all_node_binmask = 2**(num_nodes)-1
    if all_node_binmask == bin_mask:
        return [current_node_idx]
    best_tour = []
    best_len = memo[current_node_idx, bin_mask]
    for i in range(num_nodes):
        next_node_mask = 2**i
        if next_node_mask & bin_mask > 0:
            continue
        next_node = node_idx_list[i]
        next_bin_mask = bin_mask + next_node_mask
        distance_to_next = distance_matrix[current_node, next_node]
        next_tour_len = memo[i, next_bin_mask]
        total_len = distance_to_next + next_tour_len
        if total_len > best_len:
            continue
        best_tour = backtrack(node_idx_list, i, next_bin_mask)
        break
    return [current_node_idx] + best_tour

def dp(node_idx_list: np.ndarray,
       current_node_idx:int,
       bin_mask: int):
    global memo, is_visited, distance_matrix
    num_nodes = len(node_idx_list)
    all_node_binmask = 2**(num_nodes)-1
    
    if is_visited[current_node_idx,bin_mask]:
        return memo[current_node_idx,bin_mask]
    current_node = node_idx_list[current_node_idx]
    all_node_binmask = 2**(num_nodes)-1
    if bin_mask == all_node_binmask:
        return distance_matrix[current_node,0]
    
    best_len = 999999999
    for i in range(1,num_nodes):
        next_node_mask = 2**i
        if next_node_mask & bin_mask >0:
            continue
        next_node = node_idx_list[i]
        next_bin_mask = bin_mask | next_node_mask
        distance_to_next = distance_matrix[current_node, next_node]
        # print("di dalam dp, next:", i, format(next_bin_mask,fm))
        next_tour_len = dp(node_idx_list, i, next_bin_mask)
        total_len = distance_to_next + next_tour_len
        best_len = min(best_len, total_len)
    memo[current_node_idx, bin_mask] = best_len
    is_visited[current_node_idx, bin_mask] = True
    return best_len

def get_improved_tour(tour:List[int], original_distance_cost: float, cost_per_km: float):
    old_tour = tour
    tour = [node+1 for node in tour]
    tour = [0] + tour
    tour = np.asanyarray(tour, dtype=int)
    num_nodes = len(tour)
    global memo, is_visited
    all_node_binmask = 2**(len(tour))-1
    memo = np.zeros((num_nodes,all_node_binmask+2), dtype=float)
    is_visited = np.zeros((num_nodes,all_node_binmask+2), dtype=bool)
    for bin_mask in reversed(range(1,all_node_binmask+1)):
        for i in range(1,num_nodes):
            if 2**i & bin_mask == 0:
                continue
            if 1 & bin_mask == 0:
                continue
            best_len = dp(tour,i,bin_mask)
    best_len = dp(tour,0,1)
    best_cost = best_len*cost_per_km
    if best_cost > original_distance_cost:
        return old_tour
    best_tour_idx = backtrack(tour,0,1)
    best_tour = [tour[i] for i in best_tour_idx]
    best_tour = best_tour[1:]
    best_tour = [node-1 for node in best_tour]
    return best_tour
    

def improve_tours_by_dp(solution: Solution, problem: VRP3D):
    problem.reset(solution)
    # sys.setrecursionlimit(10000)
    global distance_matrix
    distance_matrix = problem.distance_matrix
    for i in range(solution.num_vehicle):
        print(i, len(solution.tour_list[i]))
        if not solution.tour_list[i] or len(solution.tour_list[i])>24:
            continue
        original_distance_cost = problem.distance_cost_list[i]
        tour = get_improved_tour(solution.tour_list[i],  
                                 original_distance_cost, 
                                 problem.vehicle_list[i].cost_per_km)
        arrival_time_list = compute_arrival_time_list(tour, distance_matrix, problem.velocity)
        solution.tour_list[i] = tour
        solution.arrival_time_list[i] = arrival_time_list
    return solution