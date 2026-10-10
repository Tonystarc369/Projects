import numpy as np
import pandas as pd
import pandas_ta as ta
from sklearn.linear_model import LinearRegression

def prepare_features(df, sentiment_score, lookback=5):
    """Generates matrix equations using historical lags, sentiment, and technical indicators."""
    df = df.copy()
    
    # 1. Add Technical Indicators
    # ta.rsi calculates the Relative Strength Index (momentum)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # ta.sma calculates a 20-day Simple Moving Average (trend tracking)
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    
    # 2. Securely create temporal lag features
    feature_cols = []
    for i in range(1, lookback + 1):
        col_name = f'Close_Lag_{i}'
        df[col_name] = df['Close'].shift(i)
        feature_cols.append(col_name)
        
    # 3. Add Sentiment static score
    df['Sentiment'] = sentiment_score
    
    # Track all our columns to feed into the AI model
    feature_cols.extend(['RSI', 'SMA_20', 'Sentiment'])
    
    # Drop rows that don't have enough history to calculate indicators or lags
    df = df.dropna(subset=feature_cols)
    
    X = df[feature_cols]
    y = df['Close']
    
    return X, y, feature_cols

def train_and_predict(df, sentiment_score, lookback=5):
    """Fits data matrix to a linear framework to output tomorrow's market estimate."""
    X, y, feature_cols = prepare_features(df, sentiment_score, lookback)
    
    # Make sure we have enough historical data rows left to train accurately
    if len(X) < 15:
        return None
        
    # Split training sets to preserve timeline continuity
    X_train = X.iloc[:-1]
    y_train = y.iloc[:-1]
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Extract the exact last row of valid calculated features to predict tomorrow
    latest_row = X.iloc[[-1]] 
    
    tomorrow_prediction = model.predict(latest_row)[0]
    return tomorrow_prediction36