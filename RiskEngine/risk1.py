import os
import pandas as pd
import numpy as np

class yieldcurve:
    def __init__(self,tenors: np.ndarray, yields: np.ndarray):
        self.tenors = tenors
        self.yields = yields
    
    def get_zero_rate(self, t: float) ->float:
        pass

    def get_discount_factor(self, t:float) -> float:
        pass    

class portfolio:
    def __init__(self, positions: pd.DataFrame):
        self.positions = positions
    
    def get_portfolio_value(self, yield_curve: yieldcurve) -> float:
        pass 
    def load_from_excel(self, file_path: str) -> None:
        pass