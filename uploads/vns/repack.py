from copy import deepcopy

import numpy as np

from packing.packing import add_items_to_box
from vrp3d.vrp3d import VRP3D
from vrp3d.solution import Solution

"""
    Given a solution,
    we will try to repack the items in the
    vehicle, so that it is more adherent
    to the LIFO constraint
"""

def repack(solution:Solution, problem: VRP3D)->Solution:
    order_list = problem.order_list
    for i in range(solution.num_vehicle):
        if not solution.tour_list[i]:
            continue
        new_sol = deepcopy(solution)
        tour = solution.tour_list[i]
        arrival_time = solution.arrival_time_list[i]
        # now collect all the orders first
        orders_to_repack = [order_list[j] for j in tour]
        # remove the packing position and
        # the insertion order from the solution
        for j in tour:
            new_sol.insertion_order_list[j] = []
            new_sol.packing_position_list[j] = []
        new_sol.tour_list[i] = []
        new_sol.arrival_time_list[i] = []
        new_sol.ep_list[i] = [np.zeros((3,), dtype=np.int64)]
        problem.reset(new_sol)

        # prepare items
        item_list = []
        for j in range(len(orders_to_repack)):
            for k in range(orders_to_repack[j].num_item_packed):
                orders_to_repack[j].packed_item_list[k].packing_order=-j
                item_list += [orders_to_repack[j].packed_item_list[k]]
        is_packing_feasible, position_dict, insertion_order_dict, rotate_count_dict = add_items_to_box(problem.vehicle_list[i].box, item_list)
        if is_packing_feasible:
            new_sol.ep_list[i] = problem.vehicle_list[i].box.ep_list
            for j in tour:
                position_list = []
                insertion_order_list = []
                rotate_count_list = []
                for k in range(order_list[j].num_item_packed):
                    item = order_list[j].packed_item_list[k]
                    position = position_dict[item.id]
                    insertion_order = insertion_order_dict[item.id]
                    rotate_count = rotate_count_dict[item.id]
                    position_list += [position]
                    insertion_order_list += [insertion_order]
                    rotate_count_list += [rotate_count]
                new_sol.packing_position_list[j] = position_list
                new_sol.insertion_order_list[j] = insertion_order_list
                new_sol.rotate_count_list[j] = rotate_count_list
            new_sol.tour_list[i]=tour
            new_sol.arrival_time_list[i]=arrival_time
            solution = new_sol
    return solution