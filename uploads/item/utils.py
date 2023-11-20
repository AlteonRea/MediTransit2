from enum import Enum
from typing import List, Union

from numba import int64, boolean
import numba as nb
import numpy as np

from item.item import Item
class Temperature(Enum):
    COLD = 0
    CHILL_LOW = 1
    CHILL_HIGH = 2
    ROOM = 3


# @nb.njit(boolean(int64,int64,int64,int64),cache=True)
def is_overlapping_1d(x1:int,dx1:int,x2:int,dx2:int):
    return x1 + dx1 >= x2 and x1 < x2 + dx2

@nb.njit(boolean(int64[:],int64[:],int64[:],int64[:]), cache=True, parallel=True)
def is_overlapping_3d(pos1:np.ndarray, 
                     size1:np.ndarray, 
                     pos2:np.ndarray, 
                     size2:np.ndarray):
    cond1 = pos1 + size1 >= pos2
    cond2 = pos1 < pos2 + size2
    return np.all(np.logical_and(cond1,cond2))
    # ans:bool = True
    # for i in range(3):
    #     ans = ans and is_overlapping_1d(pos1[i], size1[i], pos2[i], size2[i])
    # return ans
    # return is_overlapping_1d(pos1[0], size1[0], pos2[0], size2[0]) and \
    #     is_overlapping_1d(pos1[1], size1[1], pos2[1], size2[1]) and \
    #     is_overlapping_1d(pos1[2], size1[2], pos2[2], size2[2])

@nb.njit(int64(int64,int64,int64,int64),cache=True)
def compute_overlap_1d(x1:int,dx1:int,x2:int,dx2:int):
    a = max(x1,x2)
    b = min(x1+dx1,x2+dx2)
    return max(b-a,0)

@nb.njit(int64(int64[:],int64[:],int64[:,:],int64[:,:],int64),cache=True)
def nb_compute_supported_area(top_pos:np.ndarray, 
                           top_size:np.ndarray, 
                           bot_pos_list:np.ndarray, 
                           bot_size_list:np.ndarray,
                           num_bot_items:int):
    supported_area = 0
    for i in range(num_bot_items):
        is_bot_touch_top = bot_pos_list[i,2] + bot_size_list[i,2] == top_pos[2]
        if not is_bot_touch_top:
            supported_area += 0
        else:
            w = compute_overlap_1d(top_pos[0], top_size[0], bot_pos_list[i,0], bot_size_list[i,0])
            l = compute_overlap_1d(top_pos[1], top_size[1], bot_pos_list[i,1], bot_size_list[i,1])
            supported_area += w*l
    return supported_area


def compute_supported_area(item_pos:np.ndarray, 
                           item_size:np.ndarray, 
                           item_list:List[Item]):
    num_items = len(item_list)
    bot_pos_list = [item_list[i].position[np.newaxis,:] for i in range(num_items)]
    bot_size_list = [item_list[i].size[np.newaxis,:] for i in range(num_items)]
    bot_pos_list = np.concatenate(bot_pos_list, axis=0)
    bot_size_list = np.concatenate(bot_size_list, axis=0)
    supported_area = nb_compute_supported_area(item_pos, item_size, bot_pos_list, bot_size_list, num_items)
    return supported_area

def is_projection_valid_yx(item:Item, p_item:Item):
    return item.position[0] >= p_item.position[0] + p_item.size[0] and item.position[1] + item.size[1] < p_item.position[1] + p_item.size[1] and item.position[2] < p_item.position[2] + p_item.size[2]
    
def is_projection_valid_yz(item:Item, p_item:Item):
    return item.position[2] >= p_item.position[2] + p_item.size[2] and item.position[1] + item.size[1] < p_item.position[1] + p_item.size[1] and item.position[0] < p_item.position[0] + p_item.size[0]
    
def is_projection_valid_xy(item:Item, p_item:Item):
    return item.position[1] >= p_item.position[1] + p_item.size[1] and item.position[0] + item.size[0] < p_item.position[0] + p_item.size[0] and item.position[2] < p_item.position[2] + p_item.size[2]
    
def is_projection_valid_xz(item:Item, p_item:Item):
    return item.position[2] >= p_item.position[2] + p_item.size[2] and item.position[0] + item.size[0] < p_item.position[0] + p_item.size[0] and item.position[1] < p_item.position[1] + p_item.size[1]
    
def is_projection_valid_zx(item:Item, p_item:Item):
    return item.position[0] >= p_item.position[0] + p_item.size[0] and item.position[2] + item.size[2] < p_item.position[2] + p_item.size[2] and item.position[1] < p_item.position[1] + p_item.size[1]

def is_projection_valid_zy(item:Item, p_item:Item):
    return item.position[1] >= p_item.position[1] + p_item.size[1] and item.position[2] + item.size[2] < p_item.position[2] + p_item.size[2] and item.position[0] < p_item.position[0] + p_item.size[0]

# @nb.njit(boolean(int64[:],int64[:],int64[:,:],int64[:,:]), cache=True)
def nb_is_overlap_any_packed_items(item_pos: np.ndarray, item_size: np.ndarray, p_item_pos_list:np.ndarray, p_item_size_list: np.ndarray):
    num_packed_items = len(p_item_pos_list)
    for i in range(num_packed_items):
        if is_overlapping_3d(item_pos, item_size, p_item_pos_list[i,:], p_item_size_list[i,:]):
            return True
    return False

def is_overlap_any_packed_items(item_pos: np.ndarray, item_size: np.ndarray, packed_items: List[Item]):
    if not packed_items:
        return False
    # num_packed_items = len(packed_items)
    # p_item_pos = np.zeros((num_packed_items, 3), dtype=int)
    # p_item_size = np.zeros((num_packed_items,3), dtype=int)
    # for i in range(num_packed_items):
    #     p_item_pos[i,:] = packed_items[i].position
    #     p_item_size[i,:] = packed_items[i].size
    p_item_pos = [p_item.position for p_item in packed_items]
    p_item_size = [p_item.size for p_item in packed_items]
    p_item_pos = np.stack(p_item_pos, axis=0)
    p_item_size = np.stack(p_item_size, axis=0)

    # is_overlap_any = nb_is_overlap_any_packed_items(item_pos, item_size, p_item_pos, p_item_size)
    item_pos = item_pos[np.newaxis,:]
    item_size = item_size[np.newaxis, :]
    cond1 = item_pos + item_size >= p_item_pos
    cond2 = item_pos < p_item_pos + p_item_size
    is_overlap = np.all(np.logical_and(cond1,cond2), axis=1)
    is_overlap_any_ = np.any(is_overlap)
    # assert is_overlap_any == is_overlap_any_
    return is_overlap_any_
