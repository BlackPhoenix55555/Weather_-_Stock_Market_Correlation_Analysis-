import pandas as pd
import numpy as np
import statsmodels.api as sm

# File paths
stock_files = {
    "HDFC": "HDFCBank_FULL_5Y.csv",
    "TataPower": "TataPower_FULL_5Y.csv",
    "UPL": "UPL_FULL_5Y.csv",
    "HUL": "HUL_FULL_5Y.csv",
    "Indigo": "Indigo_FULL_5Y.csv"
}

weather_files = {
    "North": "North_Weather_5Y.csv",
    "South": "South_Weather_5Y.csv",
    "East": "East_Weather_5Y.csv",
    "West": "West_Weather_5Y.csv",
    "Central": "Central_Weather_5Y.csv"
}

def load_stock(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df.sort_values('Date', inplace=True)
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df.dropna(subset=['Close'], inplace=True)
    df['Return'] = df['Close'].pct_change()
    df.dropna(subset=['Return'], inplace=True)
    return df[['Date', 'Return']]

def load_weather(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df.sort_values('Date', inplace=True)
    for col in ['Temperature', 'Precipitation']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['Temperature', 'Precipitation'], inplace=True)
    return df[['Date', 'Temperature', 'Precipitation']]

results = []

for stock_name, stock_file in stock_files.items():
    stock = load_stock(stock_file)
    print(f"Processing {stock_name}...")
    
    for region_name, weather_file in weather_files.items():
        weather = load_weather(weather_file)
        merged = pd.merge(stock, weather, on='Date', how='inner')
        if merged.empty:
            continue
        
        # Add lags
        merged['Temp_lag1'] = merged['Temperature'].shift(1)
        merged['Precip_lag1'] = merged['Precipitation'].shift(1)
        merged.dropna(inplace=True)
        
        # Add day-of-week and month
        merged['dow'] = merged['Date'].dt.dayofweek
        merged['month'] = merged['Date'].dt.month
        
        # Create dummy variables (drop first to avoid collinearity)
        dummies = pd.get_dummies(merged[['dow', 'month']], drop_first=True)
        X = pd.concat([merged[['Temperature', 'Precipitation', 'Temp_lag1', 'Precip_lag1']], dummies], axis=1)
        X = sm.add_constant(X)
        y = merged['Return']
        
        # Fit OLS with Newey-West (HAC) standard errors
        model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
        
        for var in ['Temperature', 'Precipitation', 'Temp_lag1', 'Precip_lag1']:
            results.append({
                'Stock': stock_name,
                'Region': region_name,
                'Variable': var,
                'Coefficient': model.params[var],
                'PValue': model.pvalues[var],
                'Significant': model.pvalues[var] < 0.05,
                'R2': model.rsquared
            })

# Save results
pd.DataFrame(results).to_csv('regression_results.csv', index=False)
print("Regression results saved to regression_results.csv")
