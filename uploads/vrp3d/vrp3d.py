from itertools import chain
from typing import List, Tuple, Optional, Dict

import numpy as np
from sklearn.metrics.pairwise import haversine_distances

from item.item import Item
from order.order import Order
from vehicle.vehicle import Vehicle
from vrp3d.solution import Solution
from vrp3d.utils import compute_tour_list_length


class VRP3D:
    def __init__(self,
                vehicle_list: List[Vehicle],
                order_list: List[Order],
                depot_coord: Tuple[float,float],
                distance_matrix: Optional[List[List[float]]] = None,
                velocity:int=40):
        self.vehicle_list: List[Vehicle] = vehicle_list
        # we sort vehicle based on their worthiness.
        # no idea what it actually is, now its just 
        # average of cost per kg and cost per km
        self.vehicle_list = sorted(vehicle_list, key=lambda vhc: (vhc.cost_per_kg+vhc.cost_per_km)/2)

        self.order_list: List[Order] = order_list
        self.num_vehicle = len(vehicle_list)
        self.num_order = len(order_list)
        self.coords = [depot_coord]
        self.coords += [order.coord for order in order_list]
        self.coords = np.asanyarray(self.coords, dtype=float)
        if distance_matrix is not None:
            self.distance_matrix = np.asanyarray(distance_matrix,dtype=float)
        else:
            self.distance_matrix = haversine_distances(np.radians(self.coords)).astype(float) * 6371000/1000 #earth's radius in KM
        self.velocity = velocity
        self.driving_duration_matrix = self.distance_matrix/velocity
        self.weight_cost_list: List[float] = [0]*self.num_vehicle
        self.distance_cost_list: List[float] = [0]*self.num_vehicle

    """
        reset the objects to its initial state,
        or to the state of a solution
    """
    def reset(self, solution:Optional[Solution]=None):
        if solution is None:
            self.weight_cost_list: List[float] = [0]*self.num_vehicle
            self.distance_cost_list: List[float] = [0]*self.num_vehicle
            for i, vec in enumerate(self.vehicle_list):
                self.vehicle_list[i].box.reset()
            for i, order in enumerate(self.order_list):
                self.order_list[i].reset()
            return
        
        for i, order in enumerate(self.order_list):
            self.order_list[i].reset(solution.packing_position_list[i], solution.insertion_order_list[i], solution.rotate_count_list[i])
        dist_mat = self.distance_matrix
        for i, vec in enumerate(self.vehicle_list):
            packed_items = [self.order_list[oi].packed_item_list for oi in solution.tour_list[i]]
            packed_items = list(chain.from_iterable(packed_items))
            self.vehicle_list[i].box.reset(packed_items, solution.ep_list[i])

            self.weight_cost_list[i] = self.vehicle_list[i].compute_weight_cost()
            self.distance_cost_list = compute_tour_list_length(self.distance_matrix, solution.tour_list)

        