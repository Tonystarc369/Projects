OTC Risk Engine: Master Parameter Specifications

This document serves as our logical blueprint. We will build our engine by calculating these parameters in sequence, starting from the most fundamental (curves and discounting) to the most complex (credit exposure simulations).

Phase 1: Foundations (The Pricing Inputs)

Before we can calculate any risk metrics, we must build the foundations that feed into our models.

1.1 Discount Factors ($DF(t)$)

What it is: The present value of $1 received at a future time $t$.

Formula:


$$DF(t) = e^{-r(t) \cdot t}$$


where $r(t)$ is the continuously compounded zero-rate interpolated for time $t$.

1.2 Forward Rates ($F(t_1, t_2)$)

What it is: The implied risk-free interest rate for a future period between $t_1$ and $t_2$, locked in today. Used to project floating cash flows for Interest Rate Swaps.

Formula:


$$F(t_1, t_2) = \frac{r(t_2) \cdot t_2 - r(t_1) \cdot t_1}{t_2 - t_1}$$

Phase 2: Valuation / Net Present Value (NPV)

Once we have our curves, we calculate the fair value of our contracts.

2.1 Interest Rate Swap (IRS) PV

An interest rate swap consists of a Fixed Leg and a Floating Leg.

Fixed Leg PV ($PV_{\text{fixed}}$):


$$PV_{\text{fixed}} = N \cdot K \cdot \sum_{i=1}^{n} \tau_i \cdot DF(t_i)$$


where $N$ is notional, $K$ is the fixed strike rate, and $\tau_i$ is the day-count fraction (typically $0.5$ for semi-annual).

Floating Leg PV ($PV_{\text{float}}$):


$$PV_{\text{float}} = N \cdot \sum_{j=1}^{m} \tau_j \cdot F(t_{j-1}, t_j) \cdot DF(t_j)$$

Net Swap PV:


$$PV_{\text{Swap}} = \text{Direction} \cdot (PV_{\text{float}} - PV_{\text{fixed}})$$


(Direction is $+1$ for Receive Floating/Pay Fixed, and $-1$ for Pay Floating/Receive Fixed)

2.2 Black-Scholes Option PV

Used to price European Equity Options.

Formula:


$$PV_{\text{Call}} = S \cdot N(d_1) - K \cdot e^{-r \cdot T} \cdot N(d_2)$$

$$PV_{\text{Put}} = K \cdot e^{-r \cdot T} \cdot N(-d_2) - S \cdot N(-d_1)$$


where:


$$d_1 = \frac{\ln(S/K) + \left(r + \frac{\sigma^2}{2}\right)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$


$N(\cdot)$ is the cumulative standard normal distribution, $S$ is spot price, $K$ is strike, $T$ is maturity, $r$ is risk-free rate, and $\sigma$ is implied volatility.

2.3 FX Forward PV

What it is: Locked-in exchange rate valued today under Interest Rate Parity.

Formula:


$$PV_{\text{FX}} = N \cdot \left( S_0 \cdot e^{-r_f \cdot T} - K \cdot e^{-r_d \cdot T} \right)$$


where $S_0$ is the spot FX rate, $K$ is the contract delivery rate, $r_d$ is the domestic risk-free rate, and $r_f$ is the foreign risk-free rate.

Phase 3: Market Risk Sensitivities (Greeks & Curve Shocks)

Sensitivities measure how our NPV changes when market conditions shift. These are critical for hedging.

3.1 Interest Rate Delta / DV01 (Dollar Value of a 1 bp Shift)

What it is: The change in a swap or portfolio's value for a $1\text{ basis point } (0.01\%)$ parallel upward shift in the yield curve.

Formula (Numerical Approximation):


$$DV01 = \frac{PV(r + 1\text{ bp}) - PV(r - 1\text{ bp})}{2}$$

3.2 Option Delta ($\Delta$)

What it is: Sensitivity of the option price to a change in the underlying spot price $S$.

Formula:


$$\Delta_{\text{Call}} = N(d_1), \quad \Delta_{\text{Put}} = N(d_1) - 1$$

3.3 Option Gamma ($\Gamma$)

What it is: The rate of change of Delta with respect to the spot price $S$.

Formula:


$$\Gamma = \frac{N'(d_1)}{S \cdot \sigma\sqrt{T}}$$

3.4 Option Vega ($\mathcal{V}$)

What it is: Sensitivity of the option price to changes in implied volatility $\sigma$.

Formula:


$$\mathcal{V} = S \cdot \sqrt{T} \cdot N'(d_1)$$

Phase 4: Portfolio Risk Metrics

Aggregated measures of extreme loss.

4.1 Parametric Value at Risk (Parametric VaR)

What it is: The maximum portfolio loss over a time horizon $t$ at a confidence level $\alpha$ (e.g., $95\%$), assuming a normal distribution of asset returns.

Formula:


$$\text{VaR}_{\alpha} = \sigma_{\text{portfolio}} \cdot Z_{\alpha} \cdot \sqrt{t}$$


where $Z_{\alpha}$ is the normal distribution inverse (e.g., $1.645$ for $95\%$), and $\sigma_{\text{portfolio}}$ is calculated using the covariance matrix $\Sigma$ of our risk factors:


$$\sigma^2_{\text{portfolio}} = w^T \Sigma w$$

Phase 5: Counterparty Credit Risk (CCR)

Evaluating the risk that a counterparty defaults before our trades mature.

5.1 Potential Future Exposure (PFE)

What it is: A peak credit exposure at a high confidence level (e.g., $95\%$) at a future point in time $t$. Calculated by running Monte Carlo simulations of the underlying risk factors (yield curves, spot prices) and pricing the portfolio at every future step.

Formula:


$$\text{PFE}_{\alpha}(t) = \alpha\text{-percentile of } \max(PV_{\text{portfolio}}(t), 0)$$

Our Step-by-Step Execution Plan

We will build the engine by checking off these logic blocks one by one:

Block 1: Yield Curve Bootstrapper & Continuous Interpolator (Phase 1.1)

Block 2: Portfolio CSV/Excel Parser (Phase 1)

Block 3: Interest Rate Swap Pricing Engine & DV01 (Phases 2.1 & 3.1)

Block 4: Black-Scholes Pricing Engine & Greeks ($\Delta, \Gamma, \mathcal{V}$) (Phases 2.2, 3.2-3.4)

Block 5: FX Forward Pricing Engine (Phase 2.3)

Block 6: Historical/Parametric Value-at-Risk (VaR) Engine (Phase 4.1)

Block 7: Monte Carlo Engine for PFE Profiles (Phase 5.1)