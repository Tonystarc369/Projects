import os
import matplotlib.pyplot as plt
from ccr_engine.market_sim import MarketSimulator
from ccr_engine.risk_metrics import PortfolioRiskEngine
from ccr_engine.stress_testing import StressTestEngine

def run_pipeline():
    print("Initializing $100M Portfolio Counterparty Credit Risk Engine...\n")
    
    sim = MarketSimulator(T=5.0, steps=100, num_paths=1500)
    r_p, fx_p, cs_p = sim.simulate_paths()
    
    risk_engine = PortfolioRiskEngine(r_p, fx_p, cs_p, sim.time_grid)
    _, exposure = risk_engine.run_exposure_simulation()
    metrics = risk_engine.compute_metrics(exposure)
    
    wwr_cva = StressTestEngine.compute_wrong_way_cva(
        exposure, sim.time_grid, base_hazard=0.03, wwr_sensitivity=0.8
    )
    
    os.makedirs("outputs", exist_ok=True)
    
    report_path = "outputs/ccr_risk_report.txt"
    with open(report_path, "w") as f:
        f.write("PORTFOLIO COUNTERPARTY CREDIT RISK REPORT\n")
        f.write("="*50 + "\n")
        f.write(f"Portfolio Notional:          $100,000,000\n")
        f.write(f"Current Exposure (t=0):      ${metrics['Current Exposure']:,.2f}\n")
        f.write(f"Expected Positive Exp (EPE): ${metrics['Expected Positive Exposure (EPE)']:,.2f}\n")
        f.write(f"Baseline CVA:                ${metrics['Credit Valuation Adjustment (CVA)']:,.2f}\n")
        f.write(f"WWR CVA:                     ${wwr_cva:,.2f}\n")
        f.write(f"Regulatory SA-CCR EAD:       ${metrics['SA-CCR EAD']:,.2f}\n")
        
    print(f"Success: Report generated at {report_path}")

    plt.figure(figsize=(10, 6))
    plt.plot(sim.time_grid, metrics["EE Profile"] / 1e6, label="Expected Exposure (EE)", color='navy', lw=2)
    plt.plot(sim.time_grid, metrics["PFE Profile"] / 1e6, label="95% PFE", color='crimson', linestyle='--', lw=2)
    plt.axhline(metrics["Expected Positive Exposure (EPE)"] / 1e6, color='darkgreen', linestyle=':', label="EPE", lw=2)
    
    plt.title("OTC Portfolio CCR Exposure Profiles (5-Year Horizon)")
    plt.xlabel("Time (Years)")
    plt.ylabel("Exposure ($ Millions)")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    plot_path = "outputs/ccr_exposure_profiles.png"
    plt.savefig(plot_path)
    print(f"Success: Plot saved at {plot_path}")

if __name__ == "__main__":
    run_pipeline()