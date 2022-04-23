# from interactive_trader import *
# from datetime import datetime
from datetime import date

import dateutil.utils
import pandas
from ibapi.contract import Contract
# from ibapi.order import Order
# import time
# import threading
import pandas as pd
import numpy as np
import interactive_trader

# import yfinance as yf

pair = "AUD.NZD"
candle_avg = 8
tsh_buy = -1
tsh_sell = 1

#Si la senial el venta compramos AUD y vendemos NZD
#BUY is long NZD and short AUD

# pair = ['AUDUSD=X', 'NZDUSD=X']
# start = '2019-12-31'
# end = '2022-04-21'

def rug_it_entry(pair, candle_avg, tsh_buy, tsh_sell):
    ccy_a = pair.split('.')[0]
    ccy_b = pair.split('.')[1]

    asset_a = data_pull(ccy_a)[['date', 'close']]
    asset_b = data_pull(ccy_b)[['date', 'close']]
    window = int(candle_avg)
    pair_data = pd.merge(asset_a, asset_b, on='date')
    pair_data.columns = ['date', 'asset_a', 'asset_b']
    # convert date to datetime
    pair_data['date'] = pd.to_datetime(pair_data['date'])

    # pair_data = pd.DataFrame()
    # pair_data.columns = ['date']
    # for stock in pair:
    #    prices = yf.download(stock, start, end)
    #    pair_data[stock] = prices['Close']
    # pair_data = pd.DataFrame({'date': ['2022-03-13', '2022-03-14', '2022-03-15', '2022-03-16', '2022-03-17'], 'asset_a': [0.6804, 0.6604, 0.6814, 0.682, 0.683], 'asset_b': [0.7804, 0.7604, 0.7014, 0.782, 0.783]})

    def calculate_log_spread(row):
        return np.log(row['asset_a'] / row['asset_b'])

    pair_data['log_spread'] = pair_data.apply(calculate_log_spread, axis=1)
    # Calculating Moving Average
    pair_data = pair_data.assign(SMA=pair_data['log_spread'].rolling(window).mean())
    # Calculate rolling Standard Deviation
    pair_data = pair_data.assign(STD=pair_data['log_spread'].rolling(window).std())
    #print(pair_data)
    # Z-Score
    my_data = []
    my_trade = []
    trades_table = pd.DataFrame()

    for ind in range(len(pair_data)):
        my_data.append(((pair_data['log_spread'][ind]) - (pair_data['SMA'][ind])) / pair_data['STD'][ind])

        if my_data[ind] < tsh_buy:
            my_trade.append("BUY")
            trades_table.loc[ind, 'Date'] = (date.today())
            trades_table.loc[ind, 'Curr_A_(BUY)'] = ccy_b
            trades_table.loc[ind, 'Curr_B_(SELL)'] = ccy_a
            trades_table.loc[ind, 'signal'] = "BUY"
            trades_table.loc[ind, 'Buy_price'] = 0
            trades_table.loc[ind, 'Sell_price'] = 0
            trades_table.loc[ind, 'size'] = 100000
        elif my_data[ind] > tsh_sell:
            my_trade.append("SELL")
            trades_table.loc[ind, 'Date'] = (date.today())
            trades_table.loc[ind, 'Curr_A_(BUY)'] = ccy_a
            trades_table.loc[ind, 'Curr_B_(SELL)'] = ccy_b
            trades_table.loc[ind, 'signal'] = "SELL"
            trades_table.loc[ind, 'Buy_price'] = 0
            trades_table.loc[ind, 'Sell_price'] = 0
            trades_table.loc[ind, 'size'] = 100000
        else:
            my_trade.append('')

    pair_data['z_score'] = my_data
    pair_data['signal'] = my_trade

    #print(trades_table)

    return trades_table


def data_pull(forex_asset):
    contract = Contract()
    contract.symbol = forex_asset
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = 'USD'

    data = interactive_trader.fetch_historical_data(contract)
    dataframex = pd.DataFrame(data)[['date', 'open', 'high', 'low', 'close']]

    return dataframex


dataFin = rug_it_entry(pair, candle_avg, tsh_buy, tsh_sell)
dataFin.to_csv('C:/Users/vcm/Desktop/output.txt')
print(dataFin)

# for ind in dataFin.index:
#  print(((dataFin['log_spread'][ind]) - (dataFin['SMA'][ind])) / dataFin['STD'][ind])

# Create the table with the trades
# Monitoring the SL and TP (code) -> Algo to stop


# Back_testing profits
# Profit/loss
