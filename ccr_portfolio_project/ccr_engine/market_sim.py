import numpy as np

class MarketSimulator:
    """
    Simulates correlated paths for risk factors: Interest Rates (IR), 
    Foreign Exchange (FX), and Credit Spreads (CS) using GBM/Vasicek-like behaviors.
    """
    def __init__(self, T=5.0, steps=100, num_paths=1000):
        self.T = T
        self.steps = steps
        self.dt = T / steps
        self.num_paths = num_paths
        self.time_grid = np.linspace(0, T, steps + 1)
        
    def simulate_paths(self):
        r0, fx0, cs0 = 0.04, 83.0, 0.0150 # 4% IR, USD/INR 83, 150 bps Credit Spread
        
        corr_matrix = np.array([
            [1.0,  0.2, -0.3],
            [0.2,  1.0,  0.1],
            [-0.3, 0.1,  1.0]
        ])
        L = np.linalg.cholesky(corr_matrix)
        
        r_paths = np.zeros((self.num_paths, self.steps + 1))
        fx_paths = np.zeros((self.num_paths, self.steps + 1))
        cs_paths = np.zeros((self.num_paths, self.steps + 1))
        
        r_paths[:, 0] = r0
        fx_paths[:, 0] = fx0
        cs_paths[:, 0] = cs0
        
        vol_r, vol_fx, vol_cs = 0.015, 0.12, 0.35
        
        for t in range(1, self.steps + 1):
            z_raw = np.random.normal(0, 1, (3, self.num_paths))
            z = L @ z_raw
            
            speed_r, mean_r = 0.5, 0.04
            dr = speed_r * (mean_r - r_paths[:, t-1]) * self.dt + vol_r * np.sqrt(self.dt) * z[0]
            r_paths[:, t] = np.maximum(0.001, r_paths[:, t-1] + dr)
            
            dfx = fx_paths[:, t-1] * (0.02 * self.dt + vol_fx * np.sqrt(self.dt) * z[1])
            fx_paths[:, t] = fx_paths[:, t-1] + dfx
            
            dcs = cs_paths[:, t-1] * (0.01 * self.dt + vol_cs * np.sqrt(self.dt) * z[2])
            cs_paths[:, t] = np.maximum(0.001, cs_paths[:, t-1] + dcs)
            
        return r_paths, fx_paths, cs_paths