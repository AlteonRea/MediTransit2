from typing import List, Tuple

import numpy as np
"""
    tour_list: tour of each vehicle
    packing_position_list: for each order, there are items (meds+dus),
        each item has its position in the vehicles' box
    ep_list: current ep_list for each vehicles' box
    weight_cost_list: weight cost for each vehicle
    distance_cost_list: travelled distance cost for each vehicle

    having a duplicate of problem in each solution is expensive,
    when deepcopying, 
    what if we have the exact state of problem in the solution,
    and have the problem object replicate
    this state each time modification is done
"""
class Solution:
    def __init__(self,
                 num_vehicle:int,
                 num_order:int) -> None:
        self.num_vehicle = num_vehicle
        self.num_order = num_order
        self.tour_list: List[List[int]] = [[] for _ in range(num_vehicle)]
        self.packing_position_list: List[List[np.ndarray]] = [[] for _ in range(num_order)]
        self.ep_list: List[np.ndarray] = [[np.zeros((3,), dtype=np.int64)] for _ in range(num_vehicle)]
        self.arrival_time_list: List[List[int]] = [[] for _ in range(num_vehicle)]
        self.insertion_order_list: List[List[int]] = [[] for _ in range(num_order)]
        self.rotate_count_list: List[List[int]] = [[] for _ in range(num_order)]
        
    