from copy import copy
from typing import Tuple, List, Optional

import numpy as np

from item.box import Box
from item.item import Item
from packing.packing import pack_items_to_boxes

class Order:
    def __init__(self,
                 id:str,
                 customer_id:str,
                 item_list: List[Item],
                 coord:Tuple[float,float]):
        self.item_list: List[Item] = item_list
        self.packed_item_list: List[Item] = None
        self.num_item = len(item_list)
        self.num_item_packed = 0 
        self.coord = coord
        self.vehicle = None
        self.customer_id = customer_id
        self.id = str(id)
        self.weight = sum([item.weight for item in self.item_list])

    def pack_items_into_cardboard_boxes(self, box_list:List[Box]):
        item_list = copy(self.item_list)
        used_box, unpacked_items = pack_items_to_boxes(box_list, item_list)
        for bi, box in enumerate(used_box):
            used_box[bi].id = self.id+"-"+str(used_box[bi].id)
            # used_box[bi].visualize_packed_items()
        self.packed_item_list = used_box + unpacked_items 
        self.num_item_packed = len(self.packed_item_list)

    def reset(self, 
              position_list: Optional[List[np.ndarray]]=None, 
              insertion_order_list: Optional[List[int]]=None, 
              rotate_count_list: Optional[List[int]]=None):
        if position_list:
            for i, item in enumerate(self.packed_item_list):
                self.packed_item_list[i].position = position_list[i]
                self.packed_item_list[i].insertion_order = insertion_order_list[i]
                self.packed_item_list[i].rotate_count = rotate_count_list[i]
        else:
            for i, item in enumerate(self.packed_item_list):
                self.packed_item_list[i].position = None
                self.packed_item_list[i].insertion_order = 0
                self.packed_item_list[i].rotate_count = 0