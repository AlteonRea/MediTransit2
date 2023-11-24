import numpy as np

class Item:
    def __init__(self,
                 id:int,
                 size:np.ndarray,
                 name:str):
        self.id = id
        self.original_size = size
        self.weight:float
        self.volume = np.prod(size)
        self.position = None
        self.packing_order = 0
        self.insertion_order = 0
        self.alternative_sizes = [
            [size[0], size[1], size[2]],
            [size[0], size[2], size[1]], 
            [size[1], size[0], size[2]],
            [size[1], size[2], size[0]],
            [size[2], size[0], size[1]],
            [size[2], size[1], size[0]],
        ]
        self.alternative_sizes = np.asanyarray(self.alternative_sizes, dtype=np.int64)
        # self.alternative_sizes = sorted(self.alternative_sizes, key=lambda sz: (-sz[2],-sz[0],sz[1]))
        self.rotate_count = 0
        self.name = name
    
    @property
    def size(self):
        return self.alternative_sizes[self.rotate_count%6,:]
    
    @property
    def face_area(self):
        size = self.size
        return size[0]*size[1]

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        return self.id == other.id
    
    def rotate(self):
        self.rotate_count += 1

    def set_packing_order(self, packing_order):
        self.set_packing_order = packing_order