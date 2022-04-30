# from interactive_trader import *
# from datetime import datetime
from datetime import date

from pandas import DataFrame

from interactive_trader.synchronous_functions import data_pull

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
stop_loss_a = -20
stop_loss_b = 20
lot_size_a = 100000
lot_size_b = 100000

def rug_it_entry(pair, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size_a, lot_size_b):
    ccy_a = pair.split('.')[0]
    ccy_b = pair.split('.')[1]

    asset_a = data_pull(ccy_a)[['date', 'close']]
    asset_b = data_pull(ccy_b)[['date', 'close']]
    window = int(candle_avg)
    pair_data = pd.merge(asset_a, asset_b, on='date')
    pair_data.columns = ['date', 'asset_a', 'asset_b']
    # convert date to datetime
    pair_data['date'] = pd.to_datetime(pair_data['date'])

    # creating a new Candle Average column and calculating moving average

    def calculate_log_spread(row):
        return np.log(row['asset_b'] / row['asset_a'])

    pair_data['log_spread'] = pair_data.apply(calculate_log_spread, axis=1)
    # Calculating Moving Average
    pair_data = pair_data.assign(SMA=pair_data['log_spread'].rolling(window).mean())
    pair_data.loc[:, 'SMA'] = pair_data.SMA.shift(1)
    # Calculate rolling Standard Deviation
    pair_data = pair_data.assign(STD=pair_data['log_spread'].rolling(window).std())
    pair_data.loc[:, 'STD'] = pair_data.STD.shift(1)
    # print(pair_data)
    # Z-Score
    trades_table = pd.DataFrame()

    for ind in range(len(pair_data)):
        #my_data.append(((pair_data['log_spread'][ind]) - (pair_data['SMA'][ind])) / pair_data['STD'][ind])
        pair_data.loc[ind, 'z_score'] = (((pair_data['log_spread'][ind]) - (pair_data['SMA'][ind])) / pair_data['STD'][ind])

        if pair_data.loc[ind, 'z_score'] < tsh_buy:
            pair_data.loc[ind, 'signal'] = "BUY"
            trades_table.loc[ind, 'Date'] = (date.today())
            trades_table.loc[ind, 'Curr_A_(BUY)'] = ccy_b
            trades_table.loc[ind, 'Curr_B_(SELL)'] = ccy_a
            trades_table.loc[ind, 'signal'] = "BUY"
            trades_table.loc[ind, 'Buy_price'] = pair_data.loc[ind, 'asset_b']
            trades_table.loc[ind, 'Sell_price'] = pair_data.loc[ind, 'asset_a']
            trades_table.loc[ind, 'size'] = lot_size_a

        elif pair_data.loc[ind, 'z_score'] > tsh_sell:
            pair_data.loc[ind, 'signal'] = "SELL"
            trades_table.loc[ind, 'Date'] = (date.today())
            trades_table.loc[ind, 'Curr_A_(BUY)'] = ccy_a
            trades_table.loc[ind, 'Curr_B_(SELL)'] = ccy_b
            trades_table.loc[ind, 'signal'] = "SELL"
            trades_table.loc[ind, 'Buy_price'] = pair_data.loc[ind, 'asset_a']
            trades_table.loc[ind, 'Sell_price'] = pair_data.loc[ind, 'asset_b']
            trades_table.loc[ind, 'size'] = lot_size_b

        else:
            pair_data.loc[ind, 'signal'] = ''

    #print(trades_table)
    #for to complete the pair_data Backtesting
    for ind2 in range(len(pair_data)):
        if ind2 == 0:
            pair_data.loc[ind2, 'Buy_price'] = ''
            pair_data.loc[ind2, 'Sell_price'] = ''
            pair_data.loc[ind2, 'MTM'] = ''
            pair_data.loc[ind2, 'TP_SL'] = ''
        if ind2 > 0:
            #Buy and Sell price logic
            if pair_data.loc[(ind2-1), 'TP_SL'] == pair_data.loc[ind2, 'TP_SL']:
                pair_data.loc[ind2, 'Buy_price'] = pair_data.loc[(ind2-1), 'Buy_price']
                pair_data.loc[ind2, 'Sell_price'] = pair_data.loc[(ind2-1), 'Sell_price']
            elif pair_data.loc[ind2, 'TP_SL'] == "TP" or pair_data.loc[ind2, 'TP_SL'] == "SL":
                pair_data.loc[ind2, 'Buy_price'] = ''
                pair_data.loc[ind2, 'Sell_price'] = ''
            elif pair_data.loc[ind2, 'signal'] == "BUY":
                pair_data.loc[ind2, 'Buy_price'] = pair_data.loc[ind2, 'asset_b']
                pair_data.loc[ind2, 'Sell_price'] = pair_data.loc[ind2, 'asset_a']
            elif pair_data.loc[ind2, 'signal'] == "SELL":
                pair_data.loc[ind2, 'Buy_price'] = pair_data.loc[ind2, 'asset_a']
                pair_data.loc[ind2, 'Sell_price'] = pair_data.loc[ind2, 'asset_b']

            #Mark to market logic
            if pair_data.loc[(ind2-1), 'TP_SL'] == "BUY":
                pair_data.loc[ind2, 'MTM'] = (pair_data.loc[(ind2-1), 'Sell_price'] - pair_data.loc[
                    ind2, 'asset_a']) * lot_size_a + (pair_data.loc[ind2, 'asset_b'] - pair_data.loc[
                    (ind2-1), 'Buy_price']) * lot_size_b
            elif pair_data.loc[(ind2-1), 'TP_SL'] == "SELL":
                pair_data.loc[ind2, 'MTM'] = (pair_data.loc[(ind2 - 1), 'Sell_price'] - pair_data.loc[
                    ind2, 'asset_b']) * lot_size_b + (pair_data.loc[ind2, 'asset_a'] - pair_data.loc[
                    (ind2 - 1), 'Buy_price']) * lot_size_a
            else:
                pair_data.loc[ind2, 'MTM']= ''

            #Stop-Loss and Take profit
            if pair_data.loc[(ind2-1), 'TP_SL'] == "TP" or pair_data.loc[(ind2-1), 'TP_SL'] == "SL" or pair_data.loc[(ind2-1), 'TP_SL'] == '':
                pair_data.loc[ind2, 'TP_SL'] = pair_data.loc[ind2, 'signal']
            elif pair_data.loc[ind2, 'MTM'] == '':
                pair_data.loc[ind2, 'TP_SL'] = ''
            elif pair_data.loc[ind2, 'MTM'] < stop_loss_a:
                pair_data.loc[ind2, 'TP_SL'] = "SL"
            elif pair_data.loc[ind2, 'MTM'] > stop_loss_b:
                pair_data.loc[ind2, 'TP_SL'] = "TP"
            else:
                pair_data.loc[ind2, 'TP_SL'] = pair_data.loc[ind2, 'signal']

        #Profit & loss
            if pair_data.loc[ind2, 'TP_SL'] == "TP" or pair_data.loc[ind2, 'TP_SL'] == "SL":
                pair_data.loc[ind2, 'P&L'] = pair_data.loc[ind2, 'MTM']
            else:
                pair_data.loc[ind2, 'P&L'] = 0

    profits = dataFin.loc[:, 'P&L'].sum()
    #print(profits)
    # print(trades_table)
    return trades_table


def data_pull(forex_asset):
    contract = Contract()
    contract.symbol = forex_asset
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = 'USD'

    data = interactive_trader.fetch_historical_data(contract, '', '5 Y', '1 day')
    dataframex = pd.DataFrame(data)[['date', 'open', 'high', 'low', 'close']]

    return dataframex


dataFin = rug_it_entry(pair, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size_a, lot_size_b)
print(dataFin.loc[:, 'P&L'].sum())
dataFin.to_csv('output.csv')
print(dataFin)

