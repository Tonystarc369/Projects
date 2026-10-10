# OTC Counterparty Credit Risk (CCR) Engine

A simulated Python engine evaluating Counterparty Credit Risk metrics across a **$100M OTC Portfolio** (Interest Rate Swaps, FX Forwards, and Credit Default Swaps) using Monte Carlo paths.

## Key Features Implemented
* **Simulated Market Engines:** Real-time correlation mapped across IR (Vasicek Model), FX (GBM), and Credit Spreads.
* **Financial Pricers:** Built-in pricing logic calculating exposure valuation changes across varying steps of the simulated timeline.
* **Risk Profiles & Regulatory Capital:** Computes Expected Exposure (EE), 95% Potential Future Exposure (PFE), Expected Positive Exposure (EPE), and Credit Valuation Adjustment (CVA). Calculates **Basel III SA-CCR** Exposure at Default (EAD).
* **Wrong-Way Risk (WWR):** Dynamics correlating survival matrices directly with path-wise exposure spikes.

## Setup & Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the engine:
   ```bash
   python main.py
   ```
3. Run unit tests:
   ```bash
   python -m unittest discover tests/