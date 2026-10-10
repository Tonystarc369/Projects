Phase 1 Blueprint: Data Schemas & Yield Curve Bootstrapper

This blueprint outlines the data structures and mathematical models required to initialize our OTC Risk Engine. Your goal is to write the Python code that implements this specification.

1. Input Data Schemas (Excel Specs)

Our engine must ingest two distinct sheets from our Excel file (otc_portfolio.xlsx):

Sheet A: Trades

Each row represents an active OTC contract.

TradeID (String, Unique): e.g., IRS-001, OPT-102

AssetClass (String): IRS (Interest Rate Swap), EQ_OPTION (Equity Option), or FX_FORWARD (FX Forward)

Counterparty (String): e.g., Goldman Sachs

Notional (Float): Notional amount in USD (or base currency)

Direction (String): Pay or Receive (for IRS); Buy or Sell (for Options / FX)

Maturity (Float): Time to maturity in years (e.g., 2.5, 10.0)

StrikeRate (Float): The fixed swap rate (e.g., 0.035 for 3.5%) or option strike price (e.g., 150.0)

Underlying (String): Ticker or Currency Pair (e.g., SPY, EUR/USD, SOFR)

Sheet B: MarketCurves

Contains the raw market yields used to construct our risk-free discount curve.

Tenor (Float): Point on the curve in years (e.g., 0.25 for 3M, 1.0 for 1Y, 10.0 for 10Y)

ZeroRate (Float): Market-quoted yield as a decimal (e.g., 0.045 for 4.5% continuously compounded zero rate)

2. Mathematical Specification: Yield Curve Bootstrapper

We need to turn raw curve points into a continuous function that can return a Discount Factor ($DF$) for any arbitrary future time $t$.

Step 2.1: Continuous Rate Interpolation

If we need a rate for a maturity $t$ that sits between two known tenors $t_i$ and $t_{i+1}$, we use Linear Interpolation on Continuously Compounded Zero Rates:

$$r(t) = r_i + (t - t_i) \cdot \frac{r_{i+1} - r_i}{t_{i+1} - t_i}$$

Boundary rules:

If $t \le t_{\text{min}}$, set $r(t) = r_{\text{min}}$ (Flat extrapolation left).

If $t \ge t_{\text{max}}$, set $r(t) = r_{\text{max}}$ (Flat extrapolation right).

Step 2.2: Discount Factor Calculation

Once we have the interpolated zero-rate $r(t)$ for time $t$, the discount factor is calculated using continuous compounding:

$$DF(t) = e^{-r(t) \cdot t}$$

This $DF(t)$ tells us what $1 today is worth at time $t$ in the future.