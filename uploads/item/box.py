from copy import copy
import pathlib
from typing import List, Optional
from uuid import uuid1

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from item.item import Item
from item.utils import compute_supported_area
from item.utils import is_projection_valid_xy, is_projection_valid_xz, is_projection_valid_yx, is_projection_valid_yz, is_projection_valid_zx, is_projection_valid_zy
from item.utils import is_overlap_any_packed_items

import os

class Box(Item):
    def __init__(self, 
                 id: int,
                 size: np.ndarray, 
                 max_weight:int,
                 name:str,
                 support_alpha:float=0.51,
                 temperature:int= 0,
                 ):
        super(Box, self).__init__(id, size, name)
        self.max_weight = max_weight
        self.support_alpha = support_alpha
        self.packed_items: List[Item] = []
        self.weight = 0
        self.filled_volume = 0
        self.temperature = temperature
        self.ep_list: np.ndarray = None
        self.alternative_sizes = self.alternative_sizes[np.lexsort((-self.alternative_sizes[:,0], -self.alternative_sizes[:,1], -self.alternative_sizes[:,2]))]
        d_item1 = Item(uuid1(), np.asanyarray([size[0],size[1],1],dtype=np.int64),"dummy")
        d_item1.position = np.asanyarray([0,0,-1], dtype=np.int64)
        d_item2 = Item(uuid1(), np.asanyarray([size[0],1,size[2]],dtype=np.int64),"dummy")
        d_item2.position = np.asanyarray([0,-1,0], dtype=np.int64)
        d_item3 = Item(uuid1(), np.asanyarray([1,size[1],size[2]],dtype=np.int64),"dummy")
        d_item3.position = np.asanyarray([-1,0,0], dtype=np.int64)
        self.dummy_items = [d_item1, d_item2, d_item3]
        self.reset()

    # reset to initial state
    # or to a given value (say a state of a solution)
    def reset(self,
              packed_items: Optional[List[Item]] = None,
              ep_list: np.ndarray = None):
        if packed_items is None:
            self.filled_volume = 0
            self.weight = 0
            self.packed_items = []
        else:
            self.packed_items = copy(packed_items)
            self.weight = sum([p_item.weight for p_item in packed_items])
            self.filled_volume = sum([p_item.volume for p_item in packed_items])
        self.init_extreme_points(ep_list)

    def init_extreme_points(self, ep_list: np.ndarray = None):
        if ep_list is None:
            self.ep_list = np.zeros((1,3), dtype=np.int64)
        else:
            self.ep_list = np.copy(ep_list)

    """ FEASIBLE IFF
        1. placement does not cause item overflows edges
        2. it does not overlap other boxes
        3. alpha% of its bottom area are supported by other boxes or 
    """
    def is_insert_feasible(self, position:np.ndarray, item:Item) -> bool:
        # is_overflow = position[0] + item.size[0] > self.size[0] or \
        #     position[1] + item.size[1] > self.size[1] or \
        #     position[2] + item.size[2] > self.size[2]
        is_overflow = position + item.size > self.size
        is_overflow = np.any(is_overflow)
        if is_overflow:
            return False
        if is_overlap_any_packed_items(position, item.size, self.packed_items):
            return False
        # for p_item in self.packed_items:
        #     if is_overlapping_3d(position, item.size, p_item.position, p_item.size):
        #         return False

        is_item_at_bottom = position[2] == 0
        if is_item_at_bottom:
            return True
        total_supported_area = 0
        
        total_supported_area = compute_supported_area(position, item.size, self.packed_items)
        # for p_item in self.packed_items:
        #     total_supported_area += compute_supported_area(position, 
        #                                                    item.size, 
        #                                                    p_item.position,
        #                                                    p_item.size)

        supported_ratio = total_supported_area/item.face_area
        return supported_ratio >= self.support_alpha
    
    def is_item_fit(self, item: Item):  
        return self.filled_volume + item.volume <= self.volume and \
            self.weight + item.weight <= self.max_weight
    
    """
        new_eps = [
            (ep_yx),
            (ep_yz),
            (ep_xy),
            (ep_xz),
            (ep_zx),
            (ep_zy)
        ]
    """
    def insert(self, ep_i: int, item:Item):
        position = self.ep_list[ep_i,:]
        self.filled_volume += item.volume
        self.weight += item.weight
        item.position = position
        self.packed_items += [item]
        item.insertion_order = len(self.packed_items)
        # now generate extreme points
        # 1. initial extreme points
        new_eps = [
            [position[0], position[1] + item.size[1], position[2]],
            [position[0], position[1] + item.size[1], position[2]],
            [position[0] + item.size[0], position[1], position[2]],
            [position[0] + item.size[0], position[1], position[2]],
            [position[0], position[1], position[2] + item.size[2]],
            [position[0], position[1], position[2] + item.size[2]],
        ]
        new_eps = np.asanyarray(new_eps, dtype=np.int64)
        max_bound = [-1,-1,-1,-1,-1,-1]

        # 2. project these points 
        for p_item in self.dummy_items+self.packed_items:
            projx = p_item.position[0]+p_item.size[0]
            projy = p_item.position[1]+p_item.size[1]
            projz = p_item.position[2]+p_item.size[2]
            if is_projection_valid_yx(item, p_item) and projx > max_bound[0]:
                new_eps[0,:] = np.asanyarray([projx, position[1] + item.size[1], position[2]])
                max_bound[0] = projx
            if is_projection_valid_yz(item, p_item) and projz > max_bound[1]:
                new_eps[1,:] = np.asanyarray([position[1], position[1] + item.size[1], projz])
                max_bound[1] = projz
            if is_projection_valid_xy(item, p_item) and projy > max_bound[2]:
                new_eps[2,:] = np.asanyarray([position[0] + item.size[0], projy, position[2]])
                max_bound[2] = projy
            if is_projection_valid_xz(item, p_item) and projz > max_bound[3]:
                new_eps[3,:] = np.asanyarray([position[0] + item.size[0], position[1], projz])
                max_bound[3] = projz
            if is_projection_valid_zx(item, p_item) and projz > max_bound[4]:
                new_eps[4,:] = np.asanyarray([projx, position[1], position[2] + item.size[2]])
                max_bound[4] = projx
            if is_projection_valid_zy(item, p_item) and projy > max_bound[5]:
                new_eps[5,:] = np.asanyarray([position[0], projy , position[2] + item.size[2]])
                max_bound[5] = projy
        
        # add new EPs to EPlist
        self.ep_list = np.concatenate([self.ep_list, new_eps], axis=0)

        # and remove duplicate extreme points
        self.ep_list = np.unique(self.ep_list, axis=0)
        sorted_idx = np.lexsort([self.ep_list[:,0], self.ep_list[:,1], self.ep_list[:,2]], axis=0)
        self.ep_list = self.ep_list[sorted_idx]
        
        # remove inserted position from extreme points
        self.ep_list = np.delete(self.ep_list, np.all(self.ep_list ==position,axis=-1), axis=0)
        # self.visualize_packed_items()

    def plot_cube(self, ax, x, y, z, dx, dy, dz, color='red', text_annot:str=""):
        """ Auxiliary function to plot a cube. code taken somewhere from the web.  """
        xx = [x, x, x+dx, x+dx, x]
        yy = [y, y+dy, y+dy, y, y]
        kwargs = {'alpha': 1, 'color': color}
        artists = []
        # front
        # xs = [x, x,    x+dx, x+dx, x]
        # ys = [y, y,    y,    y,    y]
        # zs = [z, z+dz, z+dz, z,    z]
        # # 

        # # xs = xx*2+[x,x]*2+[x+dx,x+dx]*2
        # # ys = yy*2+[y,y]+[y+dy, y+dy]*2+[y,y]
        # # zs = [z]*5+[z+dz]*5+[z, z+dz]*4
        # # print(xs,ys,zs)
        # artists += [ax.plot3D(xs,ys,zs,**kwargs)]
        artists+= ax.plot3D(xx, yy, [z]*5, **kwargs)
        artists+= ax.plot3D(xx, yy, [z+dz]*5, **kwargs)
        artists+= ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs)
        artists+= ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs)
        artists+= ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs)
        artists+= ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs)
        if text_annot!="":
            artists+= [ax.text(x+dx/2,y,z+dz/2,text_annot,None,fontweight=1000)]
        return artists

    def visualize_packed_items(self):
        fig = plt.figure()
        axGlob = fig.add_subplot(projection='3d')
        # . plot scatola 
        self.plot_cube(axGlob,0, 0, 0, float(self.size[0]), float(self.size[1]), float(self.size[2]))
        # . plot intems in the box 
        colorList = ["black", "blue", "magenta", "orange"]
        counter = 0
        for item in self.packed_items:
            x,y,z = item.position
            color = colorList[counter % len(colorList)]
            self.plot_cube(axGlob, float(x), float(y), float(z), 
                     float(item.size[0]), float(item.size[1]), float(item.size[2]),
                     color=color,text_annot=str(item.insertion_order))
            counter = counter + 1  
        plt.show() 
    
    def generate_packing_animation(self, filename=None, chdir_in="", chdir_out=""):
        if not self.packed_items:
            return
        fig = plt.figure()
        axmax = max(float(self.alternative_sizes[0][0]), float(self.alternative_sizes[0][1]), float(self.alternative_sizes[0][2]))
        axGlob = fig.add_subplot(projection='3d')
        axGlob.axes.set_xlim3d(0, axmax) 
        axGlob.axes.set_ylim3d(0, axmax) 
        axGlob.axes.set_zlim3d(0, axmax) 
        # . plot scatola 
        self.plot_cube(axGlob,0, 0, 0, float(self.alternative_sizes[0][0]), float(self.alternative_sizes[0][1]), float(self.alternative_sizes[0][2]))
        # . plot intems in the box 
        colorList = ["black", "blue", "magenta", "orange"]
        counter = 0
        artists = []
        self.packed_items = sorted(self.packed_items, key=lambda item: item.insertion_order)
        for i, item in enumerate(self.packed_items):
            x,y,z = item.position
            color = colorList[counter % len(colorList)]
            container = self.plot_cube(axGlob, float(x), float(y), float(z), 
                     float(item.size[0]), float(item.size[1]), float(item.size[2]),
                     color=color,text_annot=str(item.insertion_order))
            if i>0:
                container += artists[i-1]
            artists += [container]
            counter = counter + 1
        ani = animation.ArtistAnimation(fig, artists, interval=1000,repeat=False)
        #filename = self.id+".html"
        if filename is None:
            filename = f"{self.id}.html"
        else:
            filename=f"{filename}.html"

        if not os.path.exists(chdir_in):
            os.makedirs(chdir_in)

        os.chdir(chdir_in)
        ani.save(filename=filename, writer="html")
        os.chdir(chdir_out)

        plt.close()
