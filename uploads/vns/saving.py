from copy import deepcopy
from itertools import chain
from typing import List, NamedTuple

import numpy as np

from packing.packing import add_items_to_box
from vns.greedy_init import greedy_initialization
from vrp3d.solution import Solution
from vrp3d.vrp3d import VRP3D
from vrp3d.utils import compute_tour_length

class MergeAction(NamedTuple):
    i: int
    j: int
    vec_idx: int
    tour: List[int]
    flip_i:bool
    flip_j:bool
    cost_saving:float
    
def generate_actions(i:int,j:int,solution:Solution,problem:VRP3D)->List[MergeAction]:
    old_distance_cost = problem.distance_cost_list[i] + problem.distance_cost_list[j]
    old_weight_cost = problem.weight_cost_list[i] + problem.weight_cost_list[j]
    old_cost = old_weight_cost + old_distance_cost

    actions = []
    tour_i = solution.tour_list[i]
    tour_j = solution.tour_list[j]
    for flip_i in range(2):
        for flip_j in range(2):
            new_tour = []
            if flip_i:
                new_tour += reversed(tour_i)
            else:
                new_tour += tour_i
            if flip_j:
                new_tour += reversed(tour_j)
            else:
                new_tour += tour_j
            new_tour_ = np.asanyarray(new_tour, dtype=np.int32)
            new_tour_length = compute_tour_length(problem.distance_matrix, new_tour_)
            new_total_weight = sum([problem.order_list[node].weight for node in new_tour])
            new_duration = new_tour_length/problem.velocity
            for vec_idx in [i,j]:
                if new_duration > problem.vehicle_list[vec_idx].max_duration:
                    continue
                if new_total_weight>problem.vehicle_list[vec_idx].box.max_weight:
                    continue
                new_distance_cost = new_tour_length*problem.vehicle_list[vec_idx].cost_per_km
                new_weight_cost = problem.vehicle_list[vec_idx].cost_per_kg*new_total_weight
                new_cost = new_distance_cost+new_weight_cost
                if new_cost>old_cost:
                    continue
                cost_saving = old_cost-new_cost
                action = MergeAction(i,j,vec_idx,new_tour,flip_i,flip_j,cost_saving)
                actions += [action]
    return actions
"""
    This algorithm is the method to generate initial solutions
    1. Start by greedily assigning orders to vehicles.
    2. Then try to combine each route with four options
        a. merge A + B
        b. merge A + reverse(B)
        c. merge reverse(A) + B
        d. merge reverse(A) + reverse(B)
    3. after two routes are merged, select the cheapest and
    feasible vehicle out of the two original vehicles.
    4. repeat this until no feasible merging is improving.
"""
def saving(problem: VRP3D, max_iteration=100) -> Solution:
    solution = greedy_initialization(problem)
    return solution
    is_good_merge_exist = True
    it = 0
    while is_good_merge_exist and it<100:
        it+=1
        is_good_merge_exist = False
        problem.reset(solution)
        merge_action_list: List[MergeAction] = []
        for i in range(problem.num_vehicle):
            if not solution.tour_list[i]:
                continue
            for j in range(problem.num_vehicle):
                if i==j:
                    continue
                if not solution.tour_list[j]:
                    continue
                n_merge_action_list = generate_actions(i,j,solution,problem)
                merge_action_list += n_merge_action_list
        merge_action_list = sorted(merge_action_list, key=lambda action: -action.cost_saving)
        # now check for the new tour feasibility
        for action in merge_action_list:
            problem.reset()
            tour = action.tour
            item_list = []
            for i,node in enumerate(tour):
                for j in range(problem.order_list[node].num_item_packed):
                    problem.order_list[node].packed_item_list[j].packing_order=-i
                    item_list += [problem.order_list[node].packed_item_list[j]]
            box = problem.vehicle_list[action.vec_idx].box
            packing_result= add_items_to_box(box, item_list)
            is_packing_feasible, position_dict, insertion_order_dict, rotate_count_dict = packing_result
            if not is_packing_feasible:
                continue
            is_good_merge_exist=True
            new_solution = deepcopy(solution)
            # new_solution.tour_list[action.i] = []
            # new_solution.tour_list[action.j] = []
            # new_solution.tour_list[action.vec_idx] = action.tour
            # for node in action.tour:
            #     for j, item in enumerate()

    return solution