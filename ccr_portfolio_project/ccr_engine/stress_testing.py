import numpy as np

class StressTestEngine:
    @staticmethod
    def compute_wrong_way_cva(exposure_matrix, time_grid, base_hazard=0.03, wwr_sensitivity=0.5, lgd=0.6):
        num_paths, total_time_points = exposure_matrix.shape
        steps = total_time_points - 1  # This will be 100
        dt = time_grid[1] - time_grid[0]
        
        path_cva = np.zeros(num_paths)
        
        for i in range(num_paths):
            # Dynamic hazard rate: higher exposure = higher default probability
            mean_exposure_factor = exposure_matrix[i, :] / (np.mean(exposure_matrix) + 1e-9)
            dynamic_hazard = base_hazard * (1.0 + wwr_sensitivity * mean_exposure_factor)
            
            # Cumulative default probability along the path
            cum_hazard = np.cumsum(dynamic_hazard * dt)
            survival_prob = np.exp(-cum_hazard)
            
            # dPD(t) step-wise approximation matching the 100 steps
            dpd = np.zeros(steps)
            dpd[0] = 1.0 - survival_prob[0]
            for t in range(1, steps):
                dpd[t] = survival_prob[t-1] - survival_prob[t]
                
            # Both arrays are now exactly shape (100,)
            path_cva[i] = lgd * np.sum(exposure_matrix[i, 1:] * dpd)
            
        return np.mean(path_cva)