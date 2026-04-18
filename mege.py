import pandas as pd
import os

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

# Create a folder for merged files
if not os.path.exists('merged_data'):
    os.makedirs('merged_data')

for stock_name, stock_file in stock_files.items():
    print(f"Processing {stock_name}...")
    
    # Load stock data with proper error handling
    stock = pd.read_csv(stock_file)
    
    # Print first few rows to see the data structure (for debugging)
    print(f"  Stock columns: {stock.columns.tolist()}")
    print(f"  First few Close values: {stock['Close'].head().tolist()}")
    
    # Convert Date column
    stock['Date'] = pd.to_datetime(stock['Date'], errors='coerce')
    stock = stock.dropna(subset=['Date'])
    stock = stock.sort_values('Date')
    
    # Convert Close to numeric - this is the key fix
    # Try to clean the data first if it has commas, currency symbols, etc.
    stock['Close'] = stock['Close'].astype(str).str.replace(',', '')  # Remove commas
    stock['Close'] = stock['Close'].str.replace('₹', '')  # Remove rupee symbol if present
    stock['Close'] = stock['Close'].str.replace('$', '')  # Remove dollar symbol if present
    stock['Close'] = pd.to_numeric(stock['Close'], errors='coerce')
    
    # Drop rows where Close is NaN
    stock = stock.dropna(subset=['Close'])
    
    # Calculate daily returns (as percentage)
    stock['Return'] = stock['Close'].pct_change() * 100
    
    # Drop the first row with NaN return
    stock = stock.dropna(subset=['Return'])
    
    # Keep only needed columns
    stock = stock[['Date', 'Close', 'Return']]
    stock.columns = ['Date', 'Price', 'Return']  # Rename Close to Price
    
    print(f"  Stock data ready: {len(stock)} records from {stock['Date'].min()} to {stock['Date'].max()}")
    
    for region_name, weather_file in weather_files.items():
        # Load weather data
        weather = pd.read_csv(weather_file)
        
        # Convert Date column
        weather['Date'] = pd.to_datetime(weather['Date'], errors='coerce')
        weather = weather.dropna(subset=['Date'])
        weather = weather.sort_values('Date')
        
        # Convert Temperature and Precipitation to numeric
        weather['Temperature'] = pd.to_numeric(weather['Temperature'], errors='coerce')
        weather['Precipitation'] = pd.to_numeric(weather['Precipitation'], errors='coerce')
        
        # Drop rows with NaN values
        weather = weather.dropna(subset=['Temperature', 'Precipitation'])
        
        # Keep only needed columns
        weather = weather[['Date', 'Temperature', 'Precipitation']]
        
        # Merge on date (inner join - only keep dates present in both)
        merged = pd.merge(stock, weather, on='Date', how='inner')
        
        if not merged.empty:
            # Add metadata columns
            merged['Stock'] = stock_name
            merged['Region'] = region_name
            
            # Reorder columns for better readability
            merged = merged[['Date', 'Stock', 'Region', 'Price', 'Return', 'Temperature', 'Precipitation']]
            
            # Save to CSV
            filename = f"merged_data/{stock_name}_{region_name}_merged.csv"
            merged.to_csv(filename, index=False)
            print(f"  ✓ Created {filename} ({len(merged)} records)")
        else:
            print(f"  ✗ No overlapping dates for {stock_name} - {region_name}")

print("\n" + "="*50)
print("✅ All merged files created successfully!")
print(f"Total files: {len(stock_files) * len(weather_files)}")
print("Check the 'merged_data' folder for your CSV files.")