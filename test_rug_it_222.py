# from interactive_trader import *
from datetime import datetime
from datetime import date
from interactive_trader.synchronous_functions import data_pull
from dateutil.relativedelta import relativedelta
import dateutil.utils
import pandas
from ibapi.contract import Contract
# from ibapi.order import Order
import time
import threading
import pandas as pd
import numpy as np
import interactive_trader
import yfinance as yf

end = ('2022-04-18')
start = ('2017-04-18')
ccy_a = 'AUDUSD=X'
ccy_b = 'NZDUSD=X'
candle_avg = 8
tsh_buy = -1
tsh_sell = 1
stop_loss_a = -225
stop_loss_b = 225
lot_size_a = 100000
lot_size_b = 100000

def rug_it_entry(ccy_a, ccy_b, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size_a, lot_size_b):

    asset_a = yf.download(ccy_a, start, end)
    asset_a.reset_index(inplace=True)
    asset_b = yf.download(ccy_b, start, end)
    asset_b.reset_index(inplace=True)

    # asset_a = data_pull(ccy_a)
    # asset_a.reset_index(inplace=True)
    # asset_b = data_pull(ccy_b)
    # asset_b.reset_index(inplace=True)

    big_table = pd.DataFrame()

    big_table['Date'] = asset_a['Date']
    big_table['Date'] = pd.to_datetime(big_table['Date'])
    big_table[ccy_a] = asset_a['Close']
    big_table[ccy_a] = pd.to_numeric(big_table[ccy_a])
    big_table[ccy_b] = asset_b['Close']
    big_table[ccy_b] = pd.to_numeric(big_table[ccy_b])

    # calculating NLog for ccy_b/ccy_a
    big_table['NLog'] = np.log(big_table[ccy_b] / big_table[ccy_a])

    # number of rows, just in case, I don't know if I'll need it, LOL.
    nRows = big_table.shape[0]

    # creating a new Candle Average column and calculating moving average
    big_table = big_table.assign(Candle_Average=big_table['NLog'].rolling(candle_avg).mean())
    big_table.loc[:, 'Candle_Average'] = big_table.Candle_Average.shift(1)

    # creating a new St Dev column and calculating moving St Dev
    big_table = big_table.assign(StDev=big_table['NLog'].rolling(candle_avg).std())
    big_table.loc[:, 'StDev'] = big_table.StDev.shift(1)

    # creating a new z-score column and calculating z-score
    big_table['Z-Score'] = (big_table['NLog'] - big_table['Candle_Average']) / big_table['StDev']

    # creating a new Signal column and filling it as per specific conditions
    conditions = [
        (big_table['Z-Score'] < tsh_buy),
        (big_table['Z-Score'] > tsh_sell),
    ]
    values = ['BUY', 'SELL']
    big_table['Signal'] = np.select(conditions, values, default='')

    # creating a column for Buy price, filling depending on the Signal type, let's see how it goes mazafaka
    conditions = [
        (big_table['Signal'] == 'BUY'),
        (big_table['Signal'] == 'SELL'),
    ]
    values1 = [big_table[ccy_b], big_table[ccy_a]]
    values2 = [big_table[ccy_a], big_table[ccy_b]]
    big_table['Buy'] = np.select(conditions, values1, default='')
    big_table['Sell'] = np.select(conditions, values2, default='')

    big_table['Buy'] = pd.to_numeric(big_table['Buy'])
    big_table['Sell'] = pd.to_numeric(big_table['Sell'])

    # creating a new deep copy of big_table for further operations
    big_table2 = big_table.copy(deep=True)

    Buy_Price = []
    Sell_Price = []
    MTM = []
    status = []

    for i in range(0, nRows):
        if (i < candle_avg):
            MTM.append('')
            status.append('')
            Buy_Price.append('')
            Sell_Price.append('')
        else:
            # Filling MTM list depending on value of previous (i-1) index of Status list
            if (status[i - 1] == 'BUY'):
                MTM.append((Sell_Price[i - 1] - big_table2.at[i, ccy_a]) * lot_size_a +
                           (big_table2.at[i, ccy_b] - Buy_Price[i - 1]) * lot_size_b),
            #  status.append(big_table2.at[i, 'Signal'])
            elif (status[i - 1] == 'SELL'):
                MTM.append((Sell_Price[i - 1] - big_table2.at[i, ccy_b]) * lot_size_b +
                           (big_table2.at[i, ccy_a] - Buy_Price[i - 1]) * lot_size_a),
            #    status.append(big_table2.at[i, 'Signal'])
            else:
                MTM.append('')

                # Filling Status list depending on value of previous (i-1) index of Status list
            # and value of current (i) index of MTM
            if (status[i - 1] == '' or status[i - 1] == 'SL' or status[i - 1] == 'TP'):
                status.append(big_table2.at[i, 'Signal'])
            #         if (status[i-1] == ''):
            #             status.append(big_table2.at[i, 'Signal'])
            elif (MTM[i] == ''):
                status.append('')
            elif (MTM[i] < stop_loss_a):
                status.append('SL')
            elif (MTM[i] > stop_loss_b):
                status.append('TP')
            else:
                status.append(status[i - 1])

                # Filling Buy_Price and Sell-Price depending on messy conditions
            if (status[i] == status[i - 1]):
                Buy_Price.append(Buy_Price[i - 1]),
                Sell_Price.append(Sell_Price[i - 1])
            elif (status[i] == 'TP' or status[i] == 'SL'):
                Buy_Price.append(''),
                Sell_Price.append('')
            elif (big_table2.at[i, 'Signal'] == 'BUY' or big_table2.at[i, 'Signal'] == 'SELL'):
                Buy_Price.append(big_table2.at[i, 'Buy']),
                Sell_Price.append(big_table2.at[i, 'Sell'])
            else:
                Buy_Price.append(''),
                Sell_Price.append('')

    # print(MTM)
    # print(status)
    # print(Buy_Price)
    # print(Sell_Price)

    big_table2['Buy_Price'] = Buy_Price
    big_table2['Sell_Price'] = Sell_Price
    big_table2['MTM'] = MTM
    big_table2['Status'] = status

    final_table = big_table2.copy(deep=True)
    final_table = final_table[final_table['Status'].isin(['SL', 'TP', 'BUY', 'SELL'])]
    final_table = final_table.drop(columns=['NLog', 'Candle_Average', 'StDev', 'Z-Score', 'Buy', 'Sell'])

    Profit2 = final_table.loc[final_table['Status'].isin(['SL', 'TP']), 'MTM'].sum()
    Profit2 = "${:,.2f}".format(Profit2)
    # print(final_table)

    return final_table, Profit2


# def data_pull(forex_asset):
#     contract = Contract()
#     contract.symbol = forex_asset
#     contract.secType = 'CASH'
#     contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
#     contract.currency = 'USD'
#
#     data = interactive_trader.fetch_historical_data(contract)
#     dataframex = pd.DataFrame(data)[['date', 'open', 'high', 'low', 'close']]
#
#     return dataframex


dataFin = rug_it_entry(ccy_a, ccy_b, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size_a, lot_size_b)
print(dataFin)

# for ind in dataFin.index:
#  print(((dataFin['log_spread'][ind]) - (dataFin['SMA'][ind])) / dataFin['STD'][ind])

# Create the table with the trades
# Monitoring the SL and TP (code) -> Algo to stop


# Back_testing profits
# Profit/loss
