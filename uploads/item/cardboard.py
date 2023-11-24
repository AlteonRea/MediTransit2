import numpy as np

from item.box import Box

class Cardboard(Box):
    def __init__(self, 
                 id:int,
                 code:str,
                 details:str,
                 size: np.ndarray, 
                 max_weight: int, 
                 support_alpha: float = 0.51, 
                 temperature: int = 0):
        super().__init__(id, size, max_weight, code, support_alpha, temperature)
        self.code = code
        self.details = details