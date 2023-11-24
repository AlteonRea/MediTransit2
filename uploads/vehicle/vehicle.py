from typing import Tuple, List

import numpy as np

from item.box import Box
from item.utils import Temperature

WC_COMPUTATION_SHR = 0
WC_COMPUTATION_CUM = 1


class Vehicle:
    """
        temp_class: temperature class, 0-3, 
            lower temp_class can handle lower temperature
            so that 
    """
    def __init__(self,
                 vendor: str,
                 box: Box,
                 cost_per_km: int,
                 cost_per_kg: int,
                 temp_class: int,
                 max_duration: int,
                 vehicle_type: str,
                 id: int):
        self.vendor = vendor
        self.box = box 
        self.vehicle_type = vehicle_type
        self.id = id

        self.cost_per_km = cost_per_km 
        self.cost_per_kg = cost_per_kg
        self.temp_class = temp_class 
        self.max_duration = max_duration

        self.tour: List[int] = []
        self.packing_order: List[int] = []
        self.arrival_time_list: List[int] = []
        self.reset()

    def reset(self):
        self.tour = []
        self.packing_order = []
        self.arrival_time_list = []
        self.box.reset()

    # TODO: create multiple types of weight cost computation
    def compute_weight_cost(self):
        return self.box.weight*self.cost_per_kg
        # return total_weight*self.cost_per_kg


def create_vehicle(vendor: str,
                    box_size: np.ndarray, 
                    box_max_weight:int,
                    cost_per_km: int,
                    cost_per_kg: int,
                    temp_class: int,
                    max_duration: int,
                    vehicle_type: str,
                    id: int) -> Vehicle:
    box = Box(id, box_size, box_max_weight, "BoxKendaraan", temperature=temp_class)
    return  Vehicle(vendor, 
                      box, 
                      cost_per_km, 
                      cost_per_kg, 
                      temp_class, 
                      max_duration,
                      vehicle_type,
                      id)
                      