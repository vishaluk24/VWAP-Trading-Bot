import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from stockstats import StockDataFrame as sdf
from tabulate import tabulate  # Import the tabulate library

# Download data
df = yf.download('ITC.NS', start='2023-07-06', end='2023-08-8', interval='5m')

df_copy = df.copy()

def vwap(df):
    df['Cum_Vol'] = df['Volume'].cumsum()
    df['Cum_Vol_Price'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum()
    df['VWAP'] = df['Cum_Vol_Price'] / df['Cum_Vol']
    return df

nine_ema = df.Close.ewm(span=9, adjust=False).mean()

df_copy = vwap(df_copy)
df['VWAP'] = df_copy['VWAP']
df['9EMA'] = nine_ema

def buy_sell(signal):
    advice_list = []
    global flag
    global mbuy
    for i in range(1, len(signal)):
        if signal['VWAP'][i] > signal['Close'][i] and signal['VWAP'][i-1] <= signal['Close'][i-1]:
            if flag != 1:
                advice_list.append(['BUY', 'at', str(signal['Close'][i])])
                mbuy = signal['Close'][i]
                flag = 1
        elif signal['VWAP'][i] < signal['Close'][i] and signal['VWAP'][i-1] >= signal['Close'][i-1]:
            if flag != 0:
                if mbuy < signal['Close'][i] and mbuy != 0:
                    advice_list.append(['SELL', 'at', str(signal['Close'][i])])
                    flag = 0
    return advice_list

mbuy = 0
flag = -1
a = buy_sell(df)

# Print the advice list using tabulate for better formatting
print(tabulate(a, headers=['Action', 'Type', 'Price'], tablefmt='fancy_grid'))

# Plot the stock data
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Close Price', color='blue')
plt.plot(df.index, df['VWAP'], label='VWAP', color='orange')
plt.plot(df.index, df['9EMA'], label='9 EMA', color='green')

# Add buy and sell markers
for advice in a:
    if advice[0] == 'BUY':
        buy_indices = df.index[df['Close'] == float(advice[2])]
        if len(buy_indices) > 0:
            plt.plot(buy_indices, df.loc[buy_indices]['Close'], 'go', markersize=8, label='Buy Signal')
    elif advice[0] == 'SELL':
        sell_indices = df.index[df['Close'] == float(advice[2])]
        if len(sell_indices) > 0:
            plt.plot(sell_indices, df.loc[sell_indices]['Close'], 'ro', markersize=8, label='Sell Signal')

# Add labels and legend
plt.title('Stock Price Analysis with Buy/Sell Signals')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)

# Add legend specifically for the buy and sell markers
plt.legend(loc='upper left', labels=['Close Price', 'VWAP', '9 EMA', 'Buy Signal', 'Sell Signal'])

# Show the plot
plt.show()