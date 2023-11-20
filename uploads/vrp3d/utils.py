from typing import List, Tuple

from numba import float64, int32
import numpy as np
import numba as nb

from item.item import Item
from order.order import Order
from packing.packing import pack_items_to_boxes
from vehicle.vehicle import Vehicle

@nb.njit(float64(float64[:,:],int32[:]), cache=True)
def compute_tour_length(distance_matrix:np.ndarray, tour:np.ndarray):
    tour_length = 0
    for i in range(1,len(tour)):
        node_idx = tour[i] + 1
        prev_node_idx = tour[i-1] + 1
        distance = distance_matrix[prev_node_idx, node_idx]
        tour_length += distance
    tour_length += distance_matrix[0, tour[0] + 1] + distance_matrix[tour[-1] + 1,0]
    return tour_length

# @nb.njit(float64[:](float64[:,:],int32[:,:]), cache=True)
def compute_tour_list_length(distance_matrix:np.ndarray, tour_list:List[List[int]])->List[float]:
    tour_list_length = [compute_tour_length(distance_matrix, np.asanyarray(tour_list[i], dtype=int)) if tour_list[i] else 0. for i in range(len(tour_list))]
    return tour_list_length

def compute_arrival_time_list(tour, distance_matrix, velocity):
    tour_distance_list = [distance_matrix[tour[i]+1,tour[i-1]+1] for i in range(1,len(tour))]
    tour_distance_list = [distance_matrix[0,tour[0]+1]] + tour_distance_list + [distance_matrix[tour[-1]+1,0]]
    arrival_time_list = [tour_distance_list[i]/velocity for i in range(len(tour_distance_list))]
    for i in range(1,len(arrival_time_list)):
        arrival_time_list[i] += arrival_time_list[i-1]
    return arrival_time_list

# check if a tour is feasible
# if the items can be packed inside the vehicle
# if the vehicle tour length not exceeding its max length
# def is_tour_feasible(tour: List[int], vehicle:Vehicle, order_list: List[Order], dist_mat: np.ndarray):
#     vehicle.box.reset()
#     # set packing order for the orders in the tour
#     item_list: List[Item] = []
#     for i, node_idx in enumerate(tour):
#         for j, item in enumerate(order_list[node_idx].packed_item_list):
#             order_list[node_idx].packed_item_list[j].packing_order = i
#         item_list += order_list[node_idx].packed_item_list
#     used_box, unpacked_items = pack_items_to_boxes([vehicle.box], item_list, is_best_fit=False)
#     if len(unpacked_items)>0:
#         return False

#     tour_length = 0
#     for i, node_idx in enumerate(tour):
        
    