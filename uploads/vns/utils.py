from copy import copy
from typing import List,Tuple

from packing.packing import add_items_to_box
from vrp3d.vrp3d import VRP3D

def get_new_arrival_time(order_i:int, vec_i:int, prob:VRP3D, tour:List[int], arrival_time:List[int])->Tuple[float, bool]:
    vec = prob.vehicle_list[vec_i]
    dist_mat = prob.distance_matrix
    if tour:
        prev_node_idx = tour[-1]
    else:
        prev_node_idx = 0
    node_idx = order_i + 1
    velocity = prob.velocity
    dist_to_order = dist_mat[prev_node_idx, node_idx]
    duration_to_order = dist_to_order/velocity
    if arrival_time:
        prev_arrival_time = arrival_time[-1]
    else:
        prev_arrival_time = 0
    arrival_time_to_order = prev_arrival_time + duration_to_order
    dist_to_depot = dist_mat[node_idx,0]
    duration_to_depot = dist_to_depot/velocity
    arrival_time_to_depot = arrival_time_to_order + duration_to_depot
    is_fit = arrival_time_to_depot <= vec.max_duration
    return arrival_time_to_order, is_fit

def append_order(order_i:int, 
                 vec_i:int,
                 problem:VRP3D) -> bool:
    vec = problem.vehicle_list[vec_i]
    order = problem.order_list[order_i]        
    item_list = copy(order.packed_item_list)
    is_packing_feasible, position_dict, insertion_order_dict, rotate_count_dict = add_items_to_box(vec.box, item_list)
    return is_packing_feasible, position_dict, insertion_order_dict, rotate_count_dict