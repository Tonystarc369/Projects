import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# ==========================================
# 1. STRATEGY ENGINE
# ==========================================
class MovingAverageCrossoverStrategy:
    """
    Dual Moving Average Crossover Strategy.
    - Buy (Long) when Short SMA crosses above Long SMA.
    - Sell/Close when Short SMA crosses below Long SMA.
    """
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        
        # Calculate moving averages
        data['SMA_Short'] = data['Close'].rolling(window=self.short_window).mean()
        data['SMA_Long'] = data['Close'].rolling(window=self.long_window).mean()
        
        # Default signal: 0 (Hold)
        data['Signal'] = 0.0
        
        # Generate 1 (Buy) when Short SMA > Long SMA
        data['Signal'][self.short_window:] = np.where(
            data['SMA_Short'][self.short_window:] > data['SMA_Long'][self.short_window:], 1.0, 0.0
        )
        
        # Position change: +1 = Buy order, -1 = Sell order
        data['Position_Change'] = data['Signal'].diff()
        
        return data

# ==========================================
# 2. BACKTESTING ENGINE
# ==========================================
class Backtester:
    """
    Simulates trading execution with transaction fees and position sizing.
    """
    def __init__(self, initial_capital: float = 100000.0, commission_pct: float = 0.001):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        cash = self.initial_capital
        holdings = 0.0
        portfolio_values = []
        trades = []

        for idx, row in df.iterrows():
            price = row['Close']
            signal = row['Position_Change']

            # BUY Signal
            if signal == 1.0 and cash > 0:
                # Buy max whole shares possible with available cash
                shares_to_buy = int(cash / (price * (1 + self.commission_pct)))
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    fee = cost * self.commission_pct
                    cash -= (cost + fee)
                    holdings += shares_to_buy
                    trades.append({'Date': idx, 'Type': 'BUY', 'Price': price, 'Shares': shares_to_buy, 'Fee': fee})

            # SELL Signal
            elif signal == -1.0 and holdings > 0:
                revenue = holdings * price
                fee = revenue * self.commission_pct
                cash += (revenue - fee)
                trades.append({'Date': idx, 'Type': 'SELL', 'Price': price, 'Shares': holdings, 'Fee': fee})
                holdings = 0.0

            # Calculate total portfolio value at current bar
            total_val = cash + (holdings * price)
            portfolio_values.append(total_val)

        df['Portfolio_Value'] = portfolio_values
        df['Strategy_Returns'] = df['Portfolio_Value'].pct_change().fillna(0.0)
        df['Benchmark_Returns'] = df['Close'].pct_change().fillna(0.0)
        
        return df, pd.DataFrame(trades)

# ==========================================
# 3. QUANTITATIVE ANALYTICS & VISUALIZATION
# ==========================================
class QuantitativeMetrics:
    """
    Calculates key financial risk metrics (Sharpe Ratio, Max Drawdown, CAGR).
    """
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, periods: int = 252) -> float:
        rf_per_period = risk_free_rate / periods
        excess_returns = returns - rf_per_period
        if excess_returns.std() == 0:
            return 0.0
        return np.sqrt(periods) * (excess_returns.mean() / excess_returns.std())

    @staticmethod
    def calculate_max_drawdown(portfolio_values: pd.Series) -> float:
        peak = portfolio_values.cummax()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()

    @classmethod
    def display_report(cls, df: pd.DataFrame, ticker: str, initial_capital: float):
        total_strategy_return = ((df['Portfolio_Value'].iloc[-1] - initial_capital) / initial_capital) * 100
        benchmark_cum_return = (((1 + df['Benchmark_Returns']).cumprod().iloc[-1]) - 1) * 100
        
        sharpe = cls.calculate_sharpe_ratio(df['Strategy_Returns'])
        max_dd = cls.calculate_max_drawdown(df['Portfolio_Value']) * 100

        print(f"\n================ PERFORMANCE METRICS [{ticker}] ================")
        print(f"Initial Capital         : ${initial_capital:,.2f}")
        print(f"Final Portfolio Value   : ${df['Portfolio_Value'].iloc[-1]:,.2f}")
        print(f"Strategy Total Return   : {total_strategy_return:.2f}%")
        print(f"Buy & Hold Benchmark    : {benchmark_cum_return:.2f}%")
        print(f"Annualized Sharpe Ratio : {sharpe:.2f}")
        print(f"Maximum Drawdown        : {max_dd:.2f}%")
        print("=================================================================\n")

    @staticmethod
    def plot_results(df: pd.DataFrame, ticker: str):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

        # Chart 1: Price, SMAs, and Buy/Sell Signals
        ax1.plot(df.index, df['Close'], label='Close Price', alpha=0.5, color='gray')
        ax1.plot(df.index, df['SMA_Short'], label='SMA Short (20)', color='blue', linestyle='--')
        ax1.plot(df.index, df['SMA_Long'], label='SMA Long (50)', color='orange', linestyle='--')

        # Buy / Sell Markers
        buys = df[df['Position_Change'] == 1.0]
        sells = df[df['Position_Change'] == -1.0]
        ax1.scatter(buys.index, buys['Close'], marker='^', color='green', s=100, label='Buy Signal', zorder=5)
        ax1.scatter(sells.index, sells['Close'], marker='v', color='red', s=100, label='Sell Signal', zorder=5)

        ax1.set_title(f"{ticker} - Algorithmic Strategy Backtest", fontsize=14, fontweight='bold')
        ax1.set_ylabel("Price ($)")
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend()

        # Chart 2: Cumulative Portfolio Equity Curve vs. Benchmark
        cum_benchmark = (1 + df['Benchmark_Returns']).cumprod() * df['Portfolio_Value'].iloc[0]
        ax2.plot(df.index, df['Portfolio_Value'], label='Quant Strategy Equity', color='green', linewidth=2)
        ax2.plot(df.index, cum_benchmark, label='Buy & Hold Benchmark', color='black', linestyle=':', alpha=0.7)
        ax2.set_title("Portfolio Equity Growth", fontsize=12)
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Portfolio Value ($)")
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend()

        plt.tight_layout()
        plt.show()

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    # Parameters
    TICKER = "NVO"
    START_DATE = "2021-01-01"
    END_DATE = "2024-01-01"
    INITIAL_CAPITAL = 100000.0
    COMMISSION = 0.001  # 0.1% per trade

    print(f"Fetching historical market data for {TICKER}...")
    data = yf.download(TICKER, start=START_DATE, end=END_DATE, progress=False)
    
    # Handle multi-level column indexing from recent yfinance versions
    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs(TICKER, level=1, axis=1)

    # 1. Initialize Strategy
    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)
    signals_df = strategy.generate_signals(data)

    # 2. Run Backtest
    backtester = Backtester(initial_capital=INITIAL_CAPITAL, commission_pct=COMMISSION)
    results_df, trades_df = backtester.run(signals_df)

    # 3. Print Results & Plot
    QuantitativeMetrics.display_report(results_df, TICKER, INITIAL_CAPITAL)
    QuantitativeMetrics.plot_results(results_df, TICKER)