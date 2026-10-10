import os
import sys
import shutil
import tempfile
import numpy as np
import pandas as pd

# ==============================================================================
# ABSOLUTE WINDOWS PATH CONFIGURATION
# ==============================================================================
# Your direct file path, using the raw 'r' prefix to make sure backslashes are safe
EXCEL_FILEPATH = r"/home/vinay/Documents/db_data_Sets/otc_portfolio.xlsx"

class PortfolioLoader:
    """
    Standardized loader to ingest and sanitize raw transaction data.
    Uses shadow copy buffering to read files that are currently locked/open in Excel.
    """
    @staticmethod
    def load_from_excel(filepath: str) -> pd.DataFrame:
        print(f"[Loader] Accessing spreadsheet at: '{filepath}'")
        
        # Verify the file actually exists to avoid silent failures
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"\n[Error] The Excel file was not found at: '{filepath}'\n"
                f"Please verify your file is placed in that directory and is named exactly 'otc_portfolio.xlsx'."
            )
            
        # Determine temporary buffer path
        temp_dir = tempfile.gettempdir()
        temp_filepath = os.path.join(temp_dir, "otc_portfolio_temp.xlsx")
        
        try:
            # This creates a shadow copy to read data even if the spreadsheet is open in Excel
            shutil.copy2(filepath, temp_filepath)
            trades_df = pd.read_excel(temp_filepath, sheet_name=0, engine='openpyxl')
            
            # Clean up immediately after reading
            try:
                os.remove(temp_filepath)
            except:
                pass
        except ImportError as ie:
            raise ImportError(
                f"\n[Dependency Error] Pandas requires 'openpyxl' to read .xlsx spreadsheets.\n"
                f"Please open your terminal and run:\n"
                f"    pip install openpyxl\n"
                f"Then run your script again."
            ) from ie
        except PermissionError:
            raise PermissionError(
                f"\n[Lock Error] Windows locked the file. Please close Excel or run your script as Administrator."
            )
        except Exception as e:
            # Direct read fallback if shadow copy fails
            try:
                trades_df = pd.read_excel(filepath, sheet_name=0, engine='openpyxl')
            except Exception as direct_e:
                raise ValueError(f"Failed to read spreadsheet: {direct_e}")

        # Standardize column headers: remove extra spaces and convert to lowercase
        trades_df.columns = trades_df.columns.str.strip().str.lower()
        
        # Look for the required data columns based on image_e24ce2.png
        required_cols = ['company', 'product', 'value']
        for col in required_cols:
            if col not in trades_df.columns:
                # Fuzzy match helper if columns are named slightly differently
                match = [c for c in trades_df.columns if col in c]
                if match:
                    print(f"[Loader] Mapping column '{match[0]}' to standard '{col}'")
                    trades_df = trades_df.rename(columns={match[0]: col})
                else:
                    raise KeyError(
                        f"Missing critical risk column: '{col}' in the Excel sheet. "
                        f"Found columns: {list(trades_df.columns)}"
                    )
                
        # Cast values to numeric and drop rows with corrupted or missing data
        trades_df['value'] = pd.to_numeric(trades_df['value'], errors='coerce')
        trades_df = trades_df.dropna(subset=['company', 'product', 'value'])
        
        # Standardize string fields for uniform grouping
        trades_df['company'] = trades_df['company'].str.strip()
        trades_df['product'] = trades_df['product'].str.strip().str.upper()
        
        return trades_df


class CounterpartyRiskEngine:
    """
    Calculates Current Exposures, Net-to-Gross Ratios (NGR), 
    and Credit Valuation Adjustments (CVA) for OTC books.
    """
    def __init__(self, portfolio_df: pd.DataFrame):
        self.df = portfolio_df.copy()
        
        # Standard Risk Parameters per counterparty based on market profiles
        # PD = 1-Year Probability of Default, LGD = Loss Given Default (60% standard)
        self.credit_params = {
            'Barclays': {'pd': 0.025, 'lgd': 0.60},
            'Goldman Sachs': {'pd': 0.015, 'lgd': 0.60},
            'Bnp Paribas': {'pd': 0.030, 'lgd': 0.60},
            'JP Morgan': {'pd': 0.130, 'lgd': 0.65},
            'Morgan Stanley': {'pd': 0.230, 'lgd': 0.45},
            'Citi': {'pd': 0.030, 'lgd': 0.60},
        }

    def calculate_current_exposure(self, df_to_use: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculates Unnetted (Gross) and Netted (Net) exposures per counterparty.
        """
        data = self.df if df_to_use is None else df_to_use
        results = []
        
        # Group all transactions by counterparty
        grouped = data.groupby('company')
        
        for company, group in grouped:
            # Gross Exposure: Sum of positive Mark-to-Market (MtM) values only
            gross_exposure = group['value'].apply(lambda x: max(x, 0.0)).sum()
            
            # Net Exposure: Max of the sum of ALL MtM values (netting positive against negative)
            net_exposure = max(group['value'].sum(), 0.0)
            
            # Net-to-Gross Ratio (NGR) represents netting efficiency
            ngr = (net_exposure / gross_exposure) if gross_exposure > 0 else 1.0
            
            # Fetch counterparty default curves
            cp_key = str(company).strip()
            pd_rate = self.credit_params.get(cp_key, {'pd': 0.03, 'lgd': 0.60})['pd']
            lgd_rate = self.credit_params.get(cp_key, {'pd': 0.03, 'lgd': 0.60})['lgd']
            
            # Credit Valuation Adjustment: CVA = Net Exposure * LGD * PD
            cva = net_exposure * lgd_rate * pd_rate
            
            results.append({
                'Counterparty': company,
                'Total MtM': group['value'].sum(),
                'Gross Exposure (Unnetted)': gross_exposure,
                'Net Exposure (Netted)': net_exposure,
                'Netting Efficiency (NGR)': ngr,
                'CVA Charge': cva
            })
            
        return pd.DataFrame(results)

    def run_stress_test(self, shocks: dict) -> pd.DataFrame:
        """
        Applies multiplicative shocks to specific product groups.
        shocks: {'COMMODITIES': 0.20, 'FOREX': -0.10, 'SWAPS': 0.15}
        """
        stressed_df = self.df.copy()
        for idx, row in stressed_df.iterrows():
            prod = str(row['product']).upper().strip()
            if prod in shocks:
                shock_val = shocks[prod]
                stressed_df.at[idx, 'value'] = row['value'] * (1 + shock_val)
                
        return stressed_df


class MarketRiskEngine:
    """
    Computes portfolio-wide Parametric Value-at-Risk (VaR) using 
    correlation structures between derivative product groups.
    """
    def __init__(self, portfolio_df: pd.DataFrame):
        self.df = portfolio_df.copy()
        
        # Get unique products present in the dataset dynamically
        self.asset_order = list(self.df['product'].unique())
        if not self.asset_order:
            self.asset_order = ['COMMODITIES', 'FOREX', 'SWAPS']
            
        # Assign standard volatilities dynamically with sensible fallbacks
        base_vols = {
            'COMMODITIES': 0.022,  # 2.2% daily vol
            'FOREX': 0.011,        # 1.1% daily vol
            'SWAPS': 0.008         # 0.8% daily vol
        }
        self.volatilities = {asset: base_vols.get(asset, 0.015) for asset in self.asset_order}
        
        # Build Correlation Matrix dynamically to prevent index errors
        n_assets = len(self.asset_order)
        self.correlation_matrix = np.eye(n_assets)
        for i, a1 in enumerate(self.asset_order):
            for j, a2 in enumerate(self.asset_order):
                if i != j:
                    if {a1, a2} == {'COMMODITIES', 'FOREX'}:
                        self.correlation_matrix[i, j] = 0.15
                    elif {a1, a2} == {'COMMODITIES', 'SWAPS'}:
                        self.correlation_matrix[i, j] = 0.25
                    elif {a1, a2} == {'FOREX', 'SWAPS'}:
                        self.correlation_matrix[i, j] = -0.10
                    else:
                        self.correlation_matrix[i, j] = 0.05 # Safe default correlation

    def calculate_parametric_var(self, confidence_level: float = 0.95) -> dict:
        """
        Calculates the 1-Day Parametric Value-at-Risk (VaR) for the portfolio.
        """
        # Calculate standard normal distribution inverse (Z-Score)
        if confidence_level == 0.95:
            z_score = 1.64485
        elif confidence_level == 0.99:
            z_score = 2.32635
        else:
            z_score = 1.96

        # Vectorize current position values mapping to index order
        weights = np.zeros(len(self.asset_order))
        total_abs_value = 0.0
        
        for idx, asset in enumerate(self.asset_order):
            asset_rows = self.df[self.df['product'] == asset]
            if not asset_rows.empty:
                weights[idx] = asset_rows['value'].sum()
                total_abs_value += abs(weights[idx])
        
        # Build Covariance Matrix: Cov = Vol_diag * Corr * Vol_diag
        vols_diag = np.diag([self.volatilities[a] for a in self.asset_order])
        covariance_matrix = vols_diag @ self.correlation_matrix @ vols_diag
        
        # Portfolio Variance: w^T * Cov * w
        portfolio_variance = weights.T @ covariance_matrix @ weights
        portfolio_volatility = np.sqrt(max(portfolio_variance, 0.0))
        
        # Parametric Value-at-Risk = Portfolio Volatility * Z-Score
        dollar_var = portfolio_volatility * z_score
        
        return {
            'Z-Score': z_score,
            'Portfolio Daily StdDev ($)': portfolio_volatility,
            'Value-at-Risk (VaR)': dollar_var,
            'VaR % of Portfolio': (dollar_var / total_abs_value) if total_abs_value > 0 else 0.0
        }


class PfeSimulationEngine:
    """
    Simulates Potential Future Exposure (PFE) profiles over a time horizon 
    using simulated Geometric Brownian Motion paths.
    """
    def __init__(self, portfolio_df: pd.DataFrame):
        self.df = portfolio_df.copy()
        
    def run_monte_carlo_pfe(self, time_steps: int = 10, paths: int = 1000, horizon_years: float = 5.0) -> dict:
        """
        Simulates future exposure pathways for active derivative holdings.
        Returns the Expected Exposure (EE) and 95% Potential Future Exposure (PFE) curves.
        """
        dt = horizon_years / time_steps
        time_grid = np.linspace(0, horizon_years, time_steps + 1)
        
        # We model each transaction as a simulated asset path
        total_paths_exposure = np.zeros((paths, time_steps + 1))
        np.random.seed(42)
        
        for idx, row in self.df.iterrows():
            asset_class = str(row['product']).upper().strip()
            initial_value = float(row['value'])
            
            # Map volatility behavior dynamically
            vol = 0.20 if asset_class == 'COMMODITIES' else (0.10 if asset_class == 'FOREX' else 0.15)
            drift = 0.02 # Safe asset growth drift
            
            # Simulate paths for this position
            asset_paths = np.zeros((paths, time_steps + 1))
            asset_paths[:, 0] = initial_value
            
            for t in range(1, time_steps + 1):
                rand_norm = np.random.normal(0, 1, paths)
                # Geometric Brownian Motion simulation
                exponent = (drift - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * rand_norm
                asset_paths[:, t] = asset_paths[:, t - 1] * np.exp(exponent)
                
            # Aggregate exposures per step (exposures are asymmetric)
            total_paths_exposure += np.maximum(asset_paths, 0.0)
            
        # Calculate statistical curves over the matrix
        expected_exposure = np.mean(total_paths_exposure, axis=0)
        pfe_95 = np.percentile(total_paths_exposure, 95, axis=0)
        pfe_99 = np.percentile(total_paths_exposure, 99, axis=0)
        
        return {
            'Time Grid (Years)': time_grid,
            'Expected Exposure (EE)': expected_exposure,
            '95% PFE Curve': pfe_95,
            '99% PFE Curve': pfe_99
        }


def run_system_diagnostics():
    """
    Executes pre-flight checks on paths and dependencies.
    """
    print("[Diagnostics] Verifying system configuration...")
    if not os.path.exists(EXCEL_FILEPATH):
        print(f"[Diagnostics] ERROR: File not found at '{EXCEL_FILEPATH}'")
    else:
        print(f"[Diagnostics] SUCCESS: Target Excel database located at '{EXCEL_FILEPATH}'")
    try:
        import openpyxl
        print("[Diagnostics] SUCCESS: Excel engine 'openpyxl' is active.")
    except ImportError:
        print("[Diagnostics] WARNING: 'openpyxl' dependency is missing. Run 'pip install openpyxl'")


if __name__ == "__main__":
    print("=" * 70)
    print("             KRATOS DERIVATIVES QUANTITATIVE RISK ENGINE       ")
    print("=" * 70)
    
    # Run system path and environmental pre-checks
    run_system_diagnostics()
    
    try:
        # 1. Load active portfolio safely
        portfolio_df = PortfolioLoader.load_from_excel(EXCEL_FILEPATH)
        print("\n[Success] Portfolio spreadsheet loaded successfully!")
        
        # 2. Compute Credit Risk Parameters
        credit_engine = CounterpartyRiskEngine(portfolio_df)
        base_risk_metrics = credit_engine.calculate_current_exposure()
        
        print("\n--- COUNTERPARTY CREDIT EXPOSURE & CVA CHARGES ---")
        formatted_credit = base_risk_metrics.copy()
        formatted_credit['Total MtM'] = formatted_credit['Total MtM'].map('${:,.2f}'.format)
        
        # Safely capture dictionary naming conventions if keys have slight whitespace shifts
        gross_col = [c for c in formatted_credit.columns if 'gross' in c.lower()][0]
        net_col = [c for c in formatted_credit.columns if 'net exposure' in c.lower()][0]
        ngr_col = [c for c in formatted_credit.columns if 'netting' in c.lower() or 'ngr' in c.lower()][0]
        cva_col = [c for c in formatted_credit.columns if 'cva' in c.lower()][0]
        
        formatted_credit[gross_col] = formatted_credit[gross_col].map('${:,.2f}'.format)
        formatted_credit[net_col] = formatted_credit[net_col].map('${:,.2f}'.format)
        formatted_credit[ngr_col] = formatted_credit[ngr_col].map('{:.1%}'.format)
        formatted_credit[cva_col] = formatted_credit[cva_col].map('${:,.2f}'.format)
        print(formatted_credit.to_string(index=False))
        
        # 3. Parametric Value-at-Risk (VaR) Engine
        market_engine = MarketRiskEngine(portfolio_df)
        var_95 = market_engine.calculate_parametric_var(confidence_level=0.95)
        var_99 = market_engine.calculate_parametric_var(confidence_level=0.99)
        
        print("\n--- MARKET RISK: PORTFOLIO VALUE-AT-RISK (1-DAY) ---")
        print(f"95% Confidence Parametric VaR : ${var_95['Value-at-Risk (VaR)']:,.2f} ({var_95['VaR % of Portfolio']:.2%})")
        print(f"99% Confidence Parametric VaR : ${var_99['Value-at-Risk (VaR)']:,.2f} ({var_99['VaR % of Portfolio']:.2%})")
        
        # 4. Monte Carlo Potential Future Exposure Simulation
        pfe_engine = PfeSimulationEngine(portfolio_df)
        pfe_results = pfe_engine.run_monte_carlo_pfe(time_steps=5, paths=1000, horizon_years=5.0)
        
        print("\n--- CREDIT RISK: POTENTIAL FUTURE EXPOSURE (PFE) SIMULATION ---")
        grid = pfe_results['Time Grid (Years)']
        ee_curve = pfe_results['Expected Exposure (EE)']
        pfe_95_curve = pfe_results['95% PFE Curve']
        
        print("Time Step | Expected Exposure (EE) | 95% PFE Limit")
        print("-" * 55)
        for t in range(len(grid)):
            print(f"Year {grid[t]:3.1f}  | ${ee_curve[t]:21,.2f} | ${pfe_95_curve[t]:,.2f}")
            
        # 5. Systemic Stress Shock Valuation
        scenarios = {
            'COMMODITIES': 0.35, # Commodities surge 35%
            'FOREX': -0.15,      # Forex changes 15%
            'SWAPS': -0.20       # Swaps liabilities scale down by 20%
        }
        print("\n--- SYSTEMIC STRESS SHOCK TEST RUN ---")
        print(f"Applying shocks: {scenarios}")
        stressed_positions = credit_engine.run_stress_test(scenarios)
        stressed_risk_metrics = credit_engine.calculate_current_exposure(stressed_positions)
        
        print("\nStressed Counterparty Exposures:")
        formatted_stressed = stressed_risk_metrics.copy()
        formatted_stressed['Total MtM'] = formatted_stressed['Total MtM'].map('${:,.2f}'.format)
        formatted_stressed[gross_col] = formatted_stressed[gross_col].map('${:,.2f}'.format)
        formatted_stressed[net_col] = formatted_stressed[net_col].map('${:,.2f}'.format)
        formatted_stressed[ngr_col] = formatted_stressed[ngr_col].map('{:.1%}'.format)
        formatted_stressed[cva_col] = formatted_stressed[cva_col].map('${:,.2f}'.format)
        print(formatted_stressed.to_string(index=False))
        
    except FileNotFoundError as fnf_error:
        print(f"\n[Path Error] {fnf_error}")
    except PermissionError as perm_error:
        print(f"\n[Permission Error] {perm_error}")
    except Exception as e:
        print(f"\n[Fatal Engine Error] Pipeline failed: {e}")