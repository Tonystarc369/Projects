import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# =====================================================================
# 1. TRADE DATA LAYER
# =====================================================================
# Simulating a basic book of FX Forward contracts for a specific counterparty
# A positive position means we buy the asset (Long), negative means sell (Short)
portfolio_data = {
    'Trade_ID': ['T001', 'T002', 'T003'],
    'Asset': ['EURUSD', 'EURUSD', 'EURUSD'],
    'Strike': [1.08, 1.12, 1.05],
    'Notional': [10_000_000, -5_000_000, 8_000_000],  # Long, Short, Long
    'Maturity_Years': [1.0, 1.5, 2.0]
}
df_portfolio = pd.DataFrame(portfolio_data)
print("--- Portfolio Book ---")
print(df_portfolio)


# =====================================================================
# 2. MARKET SIMULATION ENGINE
# =====================================================================
# We use Geometric Brownian Motion (GBM) to simulate the path of EURUSD.
# dS = r*S*dt + sigma*S*dW
S0 = 1.10          # Current spot price of EURUSD
r = 0.03           # Risk-free domestic rate (3%)
sigma = 0.12       # Annualized volatility (12%)

N_paths = 5000     # Number of Monte Carlo simulations
N_steps = 24       # Monthly time steps over a 2-year horizon (24 months)
T = 2.0            # Total time horizon in years

dt = T / N_steps
time_grid = np.linspace(0, T, N_steps + 1)

# Generate paths: Matrix shape (N_steps + 1, N_paths)
S = np.zeros((N_steps + 1, N_paths))
S[0] = S0

for t in range(1, N_steps + 1):
    Z = np.random.standard_normal(N_paths)
    S[t] = S[t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)


# =====================================================================
# 3. PRICING & AGGREGATION KERNEL
# =====================================================================
# Matrix to hold MtM value of the entire portfolio: Shape (N_steps + 1, N_paths)
portfolio_mtm = np.zeros((N_steps + 1, N_paths))

# Loop through each trade to calculate its MtM across all paths and time steps
for idx, trade in df_portfolio.iterrows():
    notional = trade['Notional']
    strike = trade['Strike']
    maturity = trade['Maturity_Years']
    
    for t_idx, t in enumerate(time_grid):
        # If the trade has already matured, its future replacement risk is 0
        if t > maturity:
            continue
            
        # Simplified FX Forward pricing: Present Value of (Spot - Strike)
        # Discount factor: e^(-r * time_to_maturity)
        time_to_mat = maturity - t
        df = np.exp(-r * time_to_mat)
        
        # MtM for this specific trade across all 5,000 paths at time step 't'
        trade_mtm = notional * (S[t_idx] - strike) * df
        
        # Aggregate the trade MtM into the total portfolio netting set
        portfolio_mtm[t_idx] += trade_mtm

# =====================================================================
# 4. CCR EXPOSURE ENGINE (Applying Netting & Floored Exposure)
# =====================================================================
# Under a Netting Agreement, we can offset positive and negative trades.
# Current Exposure = Max(Portfolio_MtM, 0)
exposures = np.maximum(portfolio_mtm, 0)

# Calculate Risk Metrics across the paths for each time step
expected_exposure = np.mean(exposures, axis=1)                  # EE (Mean)
pfe_95 = np.percentile(exposures, 95, axis=1)                   # 95% PFE
max_pfe = np.max(pfe_95)

# Wrap results in a structured summary table
exposure_profile = pd.DataFrame({
    'Time_Years': time_grid,
    'Expected_Exposure': expected_exposure,
    'PFE_95': pfe_95
})

print("\n--- Exposure Profile Snapshot (First 5 Steps) ---")
print(exposure_profile.head())
print(f"\nPeak PFE (95% Confidence): ${max_pfe:,.2f}")

plt.figure(figsize=(10, 6))
plt.plot(time_grid, expected_exposure, label='Expected Exposure (EE)', color='navy', lw=2)
plt.plot(time_grid, pfe_95, label='Potential Future Exposure (95% PFE)', color='crimson', linestyle='--', lw=2)

# Graph embellishments
plt.title('Counterparty Credit Risk Exposure Profile over Time', fontsize=14, fontweight='bold')
plt.xlabel('Time Horizon (Years)', fontsize=12)
plt.ylabel('Exposure Amount ($)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11)
plt.axvline(x=1.0, color='gray', linestyle=':', alpha=0.7, label='T001 Maturity')
plt.axvline(x=1.5, color='gray', linestyle=':', alpha=0.7, label='T002 Maturity')

plt.show()

