from copy import copy,deepcopy
from typing import NamedTuple, List

from vns.utils import append_order, get_new_arrival_time
from vrp3d.solution import Solution
from vrp3d.vrp3d import VRP3D


class InsertionAction(NamedTuple):
    order_i: int
    vec_i: int
    cost: float


"""
    very easy greedy heuristic
    from the first order (no particular ordering),
        append it to the vehicle that results in the
        cheapest additional cost
    we apply the trick in the paper.
        feasibility checking is the most expensive,
        then we just sort them first based on the cost of insertion (if feasible)
        and retrieve from the cheapest one, then check feasibility
        the first feasible (must also be cheapest) is chosen, then continue
        to the next order
"""
def greedy_initialization(problem: VRP3D) -> Solution:
    solution = Solution(problem.num_vehicle, problem.num_order)
    order_list = problem.order_list
    vehicle_list = problem.vehicle_list
    dist_mat = problem.distance_matrix
    for i, order in enumerate(order_list):
        print(i)
        node_idx = i+1
        action_list: List[InsertionAction] = []        
        for j in range(problem.num_vehicle):    
            add_dist_cost = 0
            if len(solution.tour_list[j])==0:
                prev_node_idx = 0
            else:
                prev_node_idx = solution.tour_list[j][-1] + 1
            add_dist = dist_mat[prev_node_idx, node_idx] + dist_mat[node_idx,0] - dist_mat[prev_node_idx,0]
            add_dist_cost = add_dist*vehicle_list[j].cost_per_km
            add_weight_cost = order.weight*vehicle_list[j].cost_per_kg
            add_cost = add_dist_cost + add_weight_cost
            action_list += [InsertionAction(i,j,add_cost)] 
        action_list = sorted(action_list, key=lambda action: action.cost)

        # check feasibility
        for action in action_list:
            new_sol = deepcopy(solution)
            problem.reset(new_sol)
            arrival_time_to_order, is_fit_duration = get_new_arrival_time(action.order_i, action.vec_i, problem, solution.tour_list[action.vec_i], solution.arrival_time_list[action.vec_i])
            if not is_fit_duration:
                continue
            is_insertion_feasible, position_dict, insertion_order_dict, rotate_count_dict = append_order(action.order_i, action.vec_i, problem)
            if is_insertion_feasible:
                new_sol.tour_list[action.vec_i] += [action.order_i]
                new_sol.arrival_time_list[action.vec_i] += [arrival_time_to_order]
                order = problem.order_list[action.order_i]
                for j in range(order.num_item_packed):
                    item = order.packed_item_list[j]
                    item.position = position_dict[item.id]
                    item.insertion_order = insertion_order_dict[item.id]
                    item.rotate_count =rotate_count_dict[item.id]
                order_packing_position = [order.packed_item_list[j].position for j in range(order.num_item_packed)]
                insertion_order = [order.packed_item_list[j].insertion_order for j in range(order.num_item_packed)]
                rotate_count = [order.packed_item_list[j].rotate_count for j in range(order.num_item_packed)]
                new_sol.packing_position_list[action.order_i] = order_packing_position
                new_sol.insertion_order_list[action.order_i] = insertion_order
                new_sol.rotate_count_list[action.order_i] = rotate_count
                new_sol.ep_list[action.vec_i] = copy(problem.vehicle_list[action.vec_i].box.ep_list)
                solution = new_sol
                break
    return solution