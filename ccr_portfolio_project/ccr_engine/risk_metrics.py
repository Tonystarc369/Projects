import numpy as np
from scipy.integrate import trapezoid
from ccr_engine.instruments import IRSContract, FXForwardContract, CDSContract

class PortfolioRiskEngine:
    def __init__(self, r_paths, fx_paths, cs_paths, time_grid, recovery_rate=0.4):
        self.r_paths = r_paths
        self.fx_paths = fx_paths
        self.cs_paths = cs_paths
        self.time_grid = time_grid
        self.num_paths = r_paths.shape[0]
        self.steps = r_paths.shape[1] - 1
        self.recovery_rate = recovery_rate
        self.lgd = 1.0 - recovery_rate
        
        self.portfolio = [
            IRSContract(notional=50e6, maturity=5.0, fixed_rate=0.04, pay_fixed=True),
            FXForwardContract(notional_usd=30e6, strike_fx=83.0, maturity=2.0),
            CDSContract(notional=20e6, coupon=0.015, maturity=3.0)
        ]
        
    def run_exposure_simulation(self):
        mtm_matrix = np.zeros((self.num_paths, self.steps + 1))
        
        for step, t in enumerate(self.time_grid):
            for i in range(self.num_paths):
                r = self.r_paths[i, step]
                fx = self.fx_paths[i, step]
                cs = self.cs_paths[i, step]
                
                v_irs = self.portfolio[0].value(r, t)
                v_fx = self.portfolio[1].value(r, fx, t)
                v_cds = self.portfolio[2].value(r, cs, t)
                
                mtm_matrix[i, step] = v_irs + v_fx + v_cds
                
        exposure_matrix = np.maximum(0.0, mtm_matrix)
        return mtm_matrix, exposure_matrix

    def compute_metrics(self, exposure_matrix, counterparty_hazard_rate=0.03):
        ce = np.mean(exposure_matrix[:, 0])
        ee_profile = np.mean(exposure_matrix, axis=0)
        pfe_profile = np.percentile(exposure_matrix, 95, axis=0)
        epe = trapezoid(ee_profile, self.time_grid) / self.time_grid[-1]
        
        pd_density = counterparty_hazard_rate * np.exp(-counterparty_hazard_rate * self.time_grid)
        integrand = ee_profile * pd_density
        cva = self.lgd * trapezoid(integrand, self.time_grid)
        
        alpha = 1.4
        rc = np.maximum(0.0, ce)
        
        add_on_ir = 50e6 * 0.005
        add_on_fx = 30e6 * 0.04
        add_on_credit = 20e6 * 0.054
        pfe_addon = add_on_ir + add_on_fx + add_on_credit
        
        sa_ccr_ead = alpha * (rc + pfe_addon)
        
        return {
            "Current Exposure": ce,
            "Expected Positive Exposure (EPE)": epe,
            "Credit Valuation Adjustment (CVA)": cva,
            "SA-CCR EAD": sa_ccr_ead,
            "EE Profile": ee_profile,
            "PFE Profile": pfe_profile
        }