from copy import copy, deepcopy
from functools import cmp_to_key
from math import ceil
from typing import Dict, List, Tuple

import numpy as np

from item.item import Item
from item.box import Box
from item.copier import get_a_box_copy


"""
    using binary search.
    input:  1. sorted box
            2. volume to fit
    output: index of the smallest fit box
"""
def find_smallest_fit_box(low:int, 
                         high:int, 
                         target_vol: int, 
                         volume_list: List[int]) -> int:
    if low > high:
        return -1
    mid = int((low+high)/2)
    if volume_list[mid] >= target_vol:
        idx = find_smallest_fit_box(low, mid-1, target_vol, volume_list)
        if idx == -1:
            return mid
        else:
            return idx
    return find_smallest_fit_box(mid+1, high, target_vol, volume_list)


def get_j(h:int, H:int, dt:float=7.83)->int:
    j = h*100/H/dt
    j = int(ceil(j))
    return j


"""
sort item first by their packing order (LIFO),
if same order, then:
this sorting simply sort non-increasingly
by area, then height as tiebreaker also non-increasing
"""
def cmp_item_ah(item1:Item, item2:Item):
    if item1.packing_order < item2.packing_order:
        return -1
    if item1.packing_order > item2.packing_order:
        return 1
    if item1.face_area < item2.face_area:
        return 1
    if item1.face_area > item2.face_area:
        return -1
    if item1.size[2]< item2.size[2]:
        return 1
    if item1.size[2]> item2.size[2]:
        return -1
    return 0

"""
sort item first by their packing order (LIFO),
if same order, then:
this sorting simply sort non-increasingly
by height, then area as tiebreaker also non-increasing
"""
def cmp_item_ha(item1:Item, item2:Item):
    if item1.packing_order < item2.packing_order:
        return -1
    if item1.packing_order > item2.packing_order:
        return 1    
    if item1.size[2]< item2.size[2]:
        return -1
    if item1.size[2]> item2.size[2]:
        return 1
    if item1.face_area < item2.face_area:
        return 1
    if item1.face_area > item2.face_area:
        return -1
    
    
    return 0

def find_first_ep(box_list: List[Box], item:Item):
    for bi, box in enumerate(box_list):
        for ei, ep in enumerate(box.ep_list): 
            if not box.is_insert_feasible(ep, item):
                continue
            return bi, ei
    return -1, -1

def pack_items_to_box(box: Box, item_list: List[Item]) -> Tuple[Box, List[Item]]:
    dup_item_list = []
    for item in item_list:
        for r in range(6):
            new_item = deepcopy(item)
            new_item.rotate_count = r
            dup_item_list += [new_item]
    item_list = dup_item_list
    item_list = sorted(item_list, key=cmp_to_key(cmp_item_ah))
    
    unpacked_items = []
    while len(item_list) > 0:
        item = item_list[0]
        box_i, ep_i = find_first_ep([box], item)
        if ep_i == -1:
            unpacked_items += [item]
            del item_list[0]
            continue
        box.insert(ep_i, item)
        
        # remove the duplicate items, in unpacked items
        for i in reversed(range(len(unpacked_items))):
            if unpacked_items[i].id == item.id:
                del unpacked_items[i]
        
        for i in reversed(range(len(item_list))):
            if item_list[i].id == item.id:
                del item_list[i]
            
    return box, list(set(unpacked_items))

def get_items_too_big_idx(item_list:List[Item], box_type_list:List[Box]):
    item_sizes = []
    for i, item in enumerate(item_list):
        item_i_sizes = [item_list[i].alternative_sizes[r,:][np.newaxis,:] for r in range(6)]
        item_i_sizes = np.concatenate(item_i_sizes, axis=0)
        item_sizes += [item_i_sizes[np.newaxis,:,:]]
    item_sizes = np.concatenate(item_sizes,axis=0)
    box_sizes = np.concatenate([box.size[np.newaxis,:] for box in box_type_list])
    item_sizes = item_sizes[:,:,np.newaxis,:]
    box_sizes = box_sizes[np.newaxis,np.newaxis,:,:]
    is_bigger = item_sizes>box_sizes
    is_any_dim_bigger = np.any(is_bigger,axis=-1)
    is_all_rotation_bigger = np.all(is_any_dim_bigger,axis=1)
    is_gt_all_box = np.all(is_all_rotation_bigger,axis=1)
    is_gt_idx = np.nonzero(is_gt_all_box)[0]
    return is_gt_idx

def get_best_box_idx(item_list:List[Item], box_type_list:List[Box]):
    item_sizes = []
    for i, item in enumerate(item_list):
        item_i_sizes = [item_list[i].alternative_sizes[r,:][np.newaxis,:] for r in range(6)]
        item_i_sizes = np.concatenate(item_i_sizes, axis=0)
        item_sizes += [item_i_sizes[np.newaxis,:,:]]
    item_sizes = np.concatenate(item_sizes,axis=0)
    box_sizes = np.concatenate([box.size[np.newaxis,:] for box in box_type_list])
    item_sizes = item_sizes[:,:,np.newaxis,:]
    box_sizes = box_sizes[np.newaxis,np.newaxis,:,:]
    is_bigger = item_sizes>box_sizes
    is_any_dim_bigger = np.any(is_bigger,axis=-1)
    is_all_rotation_bigger = np.all(is_any_dim_bigger,axis=1)
    num_items_smaller = np.sum(np.logical_not(is_all_rotation_bigger), axis=0)
    max_num_items = np.max(num_items_smaller)
    best_box_idx = np.where(num_items_smaller==max_num_items)[0]
    return best_box_idx

"""
    input: 1. List of available boxes
           2. List of items to pack
           3. Stop boxing threshold (zeta)
           after we find the smallest box that can
           fit the remaining items (if none exist, then
           get the biggest one), check if the remaining
           items at least can fit zeta% of the box's volume.
           Otherwise, it's wasting too much of the box space,
           then do not put them in a box.
           zeta=1 means box them regardless.
           zeta=0 means items must fit exactly or more than the box's vol.
           4. this one's recursive
           a. separate the items that cannot fit any boxtype
           b. box the items into a box
"""
def pack_items_to_boxes(box_type_list: List[Box],
        item_list: List[Item],
        zeta: float=0.7) -> Tuple[List[Box], List[Item]]:
    
    # if no boxes
    if not box_type_list:
        return [], item_list
    
    # remove items too big for any box
    too_big_item_list = []
    too_big_idx = get_items_too_big_idx(item_list, box_type_list)
    too_big_idx = np.flip(too_big_idx)
    for i in too_big_idx:
        too_big_item_list += [item_list[i]]
        del item_list[i]
    
    # if all are too big, then just return
    if not item_list:
        return [], too_big_item_list
    
    # filter the box that can fit the most number of items
    # based on the shape, actually kinda similar to the above
    # process, can be more than one.
    best_box_idx = get_best_box_idx(item_list, box_type_list)
    best_box_type_list = [box_type_list[i] for i in best_box_idx]
    used_boxes: List[Box] = []
    unpacked_items = []
    while item_list:
        remaining_volume = sum([item.volume for item in item_list])
        volume_list = [box.volume for box in best_box_type_list]
        new_box_type_i = find_smallest_fit_box(0, len(volume_list)-1, remaining_volume, volume_list)
        new_box = get_a_box_copy(best_box_type_list[new_box_type_i])
        new_box, n_unpacked_items = pack_items_to_box(new_box, item_list)
        used_boxes += [new_box]
        item_list = n_unpacked_items
        if not new_box.packed_items:
            break

    # now if there are boxes not well-utilized
    # dissolve and pack to smaller boxes
    used_boxes_final = []
    for box in used_boxes:
        utilization = box.filled_volume/box.volume
        if len(box.packed_items) <= 1:
            unpacked_items += box.packed_items
        elif utilization < zeta:
            n_item_list = box.packed_items
            n_box_type_list = [n_box for n_box in box_type_list if n_box.volume<box.volume]
            n_used_boxes, n_unpacked_items = pack_items_to_boxes(n_box_type_list, n_item_list, zeta)
            used_boxes_final += n_used_boxes
            unpacked_items += n_unpacked_items
        else:
            used_boxes_final += [box]
    unpacked_items += too_big_item_list + item_list
    return used_boxes_final, unpacked_items         

def add_items_to_box(box:Box, 
                     item_list:List[Item])->Tuple[bool, Dict[str, np.ndarray], Dict[str,int], Dict[str,int]]:
    # duplicate items for each rotation
    dup_items: List[Item] = []
    for i, item in enumerate(item_list):
        item_list[i].rotate_count = 0
        for r in range(6):
            new_item = deepcopy(item)
            new_item.rotate_count = r
            dup_items += [new_item]
    item_list = dup_items
    item_list = sorted(item_list, key=cmp_to_key(cmp_item_ah))
    packed_item_list = []
    position_dict = {}
    insertion_order_dict = {}
    rotate_count_dict = {}

    unpacked_items = []
    while len(item_list) > 0:
        item = item_list[0]
        box_i, ep_i = find_first_ep([box], item)
        if ep_i == -1:
            unpacked_items += [item]
            del item_list[0]
            continue

        # succeeding in inserting
        box.insert(ep_i, item)
        packed_item_list += [item]
        position_dict[item.id] = item.position
        insertion_order_dict[item.id] = item.insertion_order
        rotate_count_dict[item.id] = item.rotate_count
        # remove the duplicate items, in unpacked items
        for i in reversed(range(len(unpacked_items))):
            if unpacked_items[i].id == item.id:
                del unpacked_items[i]
        
        for i in reversed(range(len(item_list))):
            if item_list[i].id == item.id:
                del item_list[i]
    
    if len(unpacked_items)>0:
        return False, None, None, None

    return True, position_dict, insertion_order_dict, rotate_count_dict


        
