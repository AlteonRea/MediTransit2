from typing import List, NamedTuple

from vns.greedy_init import greedy_initialization
from vrp3d.solution import Solution
from vrp3d.vrp3d import VRP3D

# class MergeAction(NamedTuple):
#     i: int
#     j: int
#     vec_idx: int
#     flip_i:bool
#     flip_j:bool
#     saving:float
    
# def generate_actions(i:int,j:int,solution:Solution,problem:VRP3D)->List[MergeAction]:
#     old_distance_cost = problem.distance_cost_list[i] + problem.distance_cost_list[j]
#     old_weight_cost = problem.weight_cost_list[i] + problem.weight_cost_list[j]
#     old_cost = old_weight_cost + old_distance_cost

#     for vec_idx in [i,j]:
#         for flip_i in range(2):
#             for flip_j in range(3):

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
def saving(problem: VRP3D) -> Solution:
    solution = greedy_initialization(problem) 
    return solution   
    is_good_merge_exist = True
    while(is_good_merge_exist):
        problem.reset(solution)
        merge_action_list = []
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
        merge_action_list = sorted(merge_action_list, key=lambda action: -action.saving)

    return solution