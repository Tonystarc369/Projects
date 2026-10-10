import yfinance as yf
import pandas as pd
import datetime

class StockTracker:
    def __init__(self):
        self.portfolio = {}  # {ticker: {"shares": count, "buy_price": price}}

    def add_stock(self, ticker: str, shares: float, buy_price: float):
        """Add or update a stock position."""
        ticker = ticker.upper()
        if ticker in self.portfolio:
            self.portfolio[ticker]['shares'] += shares
        else:
            self.portfolio[ticker] = {'shares': shares, 'buy_price': buy_price}
        print(f"Added {shares} shares of {ticker} at ${buy_price:.2f}")

    def fetch_current_prices(self) -> pd.DataFrame:
        """Fetch current market prices and calculate total P&L."""
        if not self.portfolio:
            print("Portfolio is empty.")
            return pd.DataFrame()

        tickers = list(self.portfolio.keys())
        # Fetch current data
        data = yf.download(tickers, period="1d", interval="1m", progress=False)
        
        results = []
        for ticker in tickers:
            try:
                # Get latest close price
                if len(tickers) == 1:
                    current_price = data['Close'].iloc[-1]
                else:
                    current_price = data['Close'][ticker].iloc[-1]
                
                shares = self.portfolio[ticker]['shares']
                buy_price = self.portfolio[ticker]['buy_price']
                total_cost = shares * buy_price
                market_value = shares * current_price
                pnl = market_value - total_cost
                pnl_pct = (pnl / total_cost) * 100

                results.append({
                    "Ticker": ticker,
                    "Shares": shares,
                    "Avg Buy Price": f"${buy_price:.2f}",
                    "Current Price": f"${current_price:.2f}",
                    "Market Value": f"${market_value:.2f}",
                    "P&L ($)": f"${pnl:.2f}",
                    "P&L (%)": f"{pnl_pct:.2f}%"
                })
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")

        return pd.DataFrame(results)

# --- Example Usage ---
if __name__ == "__main__":
    tracker = StockTracker()
    
    # Adding different companies (US & Indian markets supported by yfinance)
    tracker.add_stock("AAPL", shares=10, buy_price=180.0)   # Apple
    tracker.add_stock("MSFT", shares=5, buy_price=350.0)    # Microsoft
    tracker.add_stock("RELIANCE.NS", shares=20, buy_price=2800.0)  # Reliance (NSE)

    print("\nFetching latest prices...\n")
    df = tracker.fetch_current_prices()
    print(df.to_string(index=False))