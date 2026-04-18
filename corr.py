import pandas as pd
import os

stocks = {
    "TataPower": "TataPower_FULL_5Y.csv",
    "UPL": "UPL_FULL_5Y.csv",
    "HUL": "HUL_FULL_5Y.csv",
    "Indigo": "Indigo_FULL_5Y.csv",
    "HDFC": "HDFCBank_FULL_5Y.csv"
}

regions = {
    "North": "North_Weather_5Y.csv",
    "South": "South_Weather_5Y.csv",
    "East": "East_Weather_5Y.csv",
    "West": "West_Weather_5Y.csv",
    "Central": "Central_Weather_5Y.csv"
}

os.makedirs("results", exist_ok=True)

# 🔥 STORE RESULTS
region_results = {region: {} for region in regions.keys()}

# -------------------------------
# LOOP
# -------------------------------

for stock_name, stock_file in stocks.items():

    stock = pd.read_csv(stock_file)
    stock['Date'] = pd.to_datetime(stock['Date'])

    for region_name, weather_file in regions.items():

        weather = pd.read_csv(weather_file)
        weather['Date'] = pd.to_datetime(weather['Date'])

        df = pd.merge(stock, weather, on="Date", how="inner")
        df = df.sort_values("Date")

        # Convert numeric
        numeric_cols = ['Close', 'High', 'Low', 'Open', 'Volume', 'Temperature', 'Precipitation']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Clean
        df.ffill(inplace=True)
        df.bfill(inplace=True)

        # Features
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = (df['High'] - df['Low']) / df['Open']
        df.dropna(inplace=True)

        # Correlation
        columns = ['Temperature', 'Precipitation', 'Close', 'Returns', 'Volume']
        pearson_corr = df[columns].corr(method='pearson')

        # 🔥 STORE ONLY IMPORTANT VALUE
        # Example: correlation between Temperature & Returns
        region_results[region_name][stock_name] = pearson_corr.loc['Temperature', 'Returns']

# -------------------------------
# PRINT REGION-WISE COMPARISON
# -------------------------------

print("\n🔥 REGION-WISE WEATHER IMPACT (Temperature vs Returns):\n")

for region, data in region_results.items():
    print(f"\n📍 {region} India:")
    for stock, value in data.items():
        print(f"{stock}: {value:.4f}")
