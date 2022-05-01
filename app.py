import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from interactive_trader.synchronous_functions import data_pull
from page_1 import page_1
from order_page import order_page
from error_page import error_page
from navbar import navbar
from Backtesting import pair_blotter
from sidebar import sidebar, SIDEBAR_HIDDEN, SIDEBAR_STYLE
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from interactive_trader import *
from datetime import datetime, date
from ibapi.contract import Contract
from ibapi.order import Order
import time
import threading
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import scipy.optimize as spop

CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

order_status = ""
errors = ""
connected = ""

ibkr_async_conn = ibkr_app()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Store(id='side_click'),
        dcc.Location(id="url"),
        navbar,
        sidebar,
        html.Div(id="page-content", style=CONTENT_STYLE),
        dcc.Interval(
            id='ibkr-update-interval',
            interval=5000,
            n_intervals=0
        )
    ],
)


@app.callback(
    [Output('trade-blotter', 'data'), Output('trade-blotter', 'columns')],
    Input('ibkr-update-interval', 'n_intervals')
)
def update_order_status(n_intervals):
    global ibkr_async_conn
    global order_status

    order_status = ibkr_async_conn.order_status

    df = order_status
    dt_data = df.to_dict('records')
    dt_columns = [{"name": i, "id": i} for i in df.columns]
    return dt_data, dt_columns


# # This callback and function will populate the pairs blotter page
# @app.callback(
#     [Output('pairBlotter-link', 'data'), Output('pairBlotter-link', 'columns')],
#     Input('rug_it_entry', 'pair, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size_a, lot_size_b')
# )


@app.callback(
    [Output('errors-dt', 'data'), Output('errors-dt', 'columns')],
    Input('ibkr-update-interval', 'n_intervals')
)
def update_order_status(n_intervals):
    global ibkr_async_conn
    global errors

    errors = ibkr_async_conn.error_messages

    df = errors
    dt_data = df.to_dict('records')
    dt_columns = [{"name": i, "id": i} for i in df.columns]
    return dt_data, dt_columns


@app.callback(
    [
        Output("sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'

    return sidebar_style, content_style, cur_nclick


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 5)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 5)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/home-screen"]:
        return page_1
    elif pathname == "/blotter":
        return order_page
    elif pathname == "/errors":
        return error_page
    elif pathname == "/Backtesting":
        return pair_blotter
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(
    Output('ibkr-async-conn-status', 'children'),
    [
        Input('ibkr-async-conn-status', 'children'),
        Input('master-client-id', 'value'),
        Input('port', 'value'),
        Input('hostname', 'value')
    ]
)
def async_handler(async_status, master_client_id, port, hostname):
    if async_status == "CONNECTED":
        raise PreventUpdate
        pass

    global ibkr_async_conn
    ibkr_async_conn.connect(hostname, port, master_client_id)

    timeout_sec = 5

    start_time = datetime.now()
    while not ibkr_async_conn.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            ibkr_async_conn.disconnect()
            raise Exception(
                "set_up_async_connection",
                "timeout",
                "couldn't connect to IBKR"
            )

    def run_loop():
        ibkr_async_conn.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while ibkr_async_conn.next_valid_id is None:
        time.sleep(0.01)

    global order_status
    order_status = ibkr_async_conn.order_status

    global errors
    errors = ibkr_async_conn.error_messages

    global connected
    connected = ibkr_async_conn.isConnected()

    return str(connected)

@app.callback(
    [Output('pairBlotter-link', 'data'), Output('pairBlotter-link', 'columns'),
     Output('profit', 'children')
     ],
    [
        # new button to start the algo defined in sidebar.py
        Input('start-algo-button', 'n_clicks'),
        # State('pair', 'value'),
        # # candle_avg
        State('candle-avg', 'value'),
        # tsh_buy
        State('tsh-buy', 'value'),
        # tsh_sell
        State('tsh-sell', 'value'),
        # stop_loss_a,
        State('stop-loss-a', 'value'),
        # stop_loss_b
        State('stop-loss-b', 'value'),
        # lot_size_a
        State('lot-size', 'value'),

    ],
    prevent_initial_call = True
)
def rug_it_entry(n_clicks, candle_avg, tsh_buy, tsh_sell, stop_loss_a, stop_loss_b, lot_size):
    end = ('2022-04-18')
    start = ('2017-04-18')
    ccy_a = 'AUDUSD=X'
    ccy_b = 'NZDUSD=X'
    candle_avg = int(candle_avg)
    tsh_buy = int(tsh_buy)
    tsh_sell = int(tsh_sell)
    stop_loss_a = int(stop_loss_a)
    stop_loss_b = int(stop_loss_b)
    lot_size_a = int(lot_size)
    lot_size_b = int(lot_size)

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
   # big_table['Date'] = pd.to_datetime(big_table['Date'])
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
    Lot_Size = []
    Trades = []


    # oh my God, some more lists to fill in some more columns in the big table to get correct final table
    Buy_Price_F = []
    Sell_Price_F = []
    Curr_Buy = []
    Curr_Sell = []

    for i in range(0, nRows):
        if (i < candle_avg):
            MTM.append('')
            status.append('')
            Buy_Price.append('')
            Sell_Price.append('')
            Trades.append('')
            Buy_Price_F.append('')
            Sell_Price_F.append('')
            Curr_Buy.append('')
            Curr_Sell.append('')
        else:
            # Filling MTM list depending on value of previous (i-1) index of Status list
            if (status[i - 1] == 'BUY'):
                MTM.append(((Sell_Price[i - 1] - big_table2.at[i, ccy_a]) * lot_size_a +
                           (big_table2.at[i, ccy_b] - Buy_Price[i - 1]) * lot_size_b).round(decimals =0)),
            #  status.append(big_table2.at[i, 'Signal'])
            elif (status[i - 1] == 'SELL'):
                MTM.append(((Sell_Price[i - 1] - big_table2.at[i, ccy_b]) * lot_size_b +
                           (big_table2.at[i, ccy_a] - Buy_Price[i - 1]) * lot_size_a).round(decimals=0)),
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
            elif (MTM[i] <= stop_loss_a):
                status.append('SL')
            elif (MTM[i] >= stop_loss_b):
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

            # Filling Trades column to use it further for keeping only rows with Trades happened
            if (status[i] != status[i - 1] and status[i] != ''):
                Trades.append('Tx Done')
            else:
                Trades.append('')

            # Filling 2 columns to get Buy and Sell Prices
            if ((status[i] == 'TP' or status[i] == 'SL') and status[i - 1] == 'SELL'):
                Buy_Price_F.append(big_table2.at[i, ccy_b]),
                Sell_Price_F.append(big_table2.at[i, ccy_a])
            elif ((status[i] == 'TP' or status[i] == 'SL') and status[i - 1] == 'BUY'):
                Buy_Price_F.append(big_table2.at[i, ccy_a]),
                Sell_Price_F.append(big_table2.at[i, ccy_b])
            elif (status[i] == 'SELL' and status[i - 1] != 'SELL'):
                Buy_Price_F.append(big_table2.at[i, ccy_a]),
                Sell_Price_F.append(big_table2.at[i, ccy_b])
            elif (status[i] == 'BUY' and status[i - 1] != 'BUY'):
                Buy_Price_F.append(big_table2.at[i, ccy_b]),
                Sell_Price_F.append(big_table2.at[i, ccy_a])
            else:
                Buy_Price_F.append(''),
                Sell_Price_F.append('')

            # Filling 2 columns to set which currencies we're Buying and Selling
            if (status[i] == 'SELL' and status[i - 1] != 'SELL'):
                Curr_Buy.append(ccy_a),
                Curr_Sell.append(ccy_b)
            elif (status[i] == 'BUY' and status[i - 1] != 'BUY'):
                Curr_Buy.append(ccy_b),
                Curr_Sell.append(ccy_a)
            elif ((status[i] == 'SL' or status[i] == 'TP') and status[i - 1] == 'BUY'):
                Curr_Buy.append(ccy_a),
                Curr_Sell.append(ccy_b)
            elif ((status[i] == 'SL' or status[i] == 'TP') and status[i - 1] == 'SELL'):
                Curr_Buy.append(ccy_b),
                Curr_Sell.append(ccy_a)
            else:
                Curr_Buy.append(''),
                Curr_Sell.append('')

        Lot_Size.append(lot_size_a)
    # print(MTM)
    # print(status)
    # print(Buy_Price)
    # print(Sell_Price)

    big_table2['Buy_Price'] = Buy_Price
    big_table2['Sell_Price'] = Sell_Price
    big_table2['MTM'] = MTM
    big_table2['Status'] = status
    big_table2['size'] = Lot_Size
    big_table2['Trades'] = Trades
    big_table2['Buy_Price_F'] = Buy_Price_F
    big_table2['Sell_Price_F'] = Sell_Price_F
    big_table2['Currency_Buy'] = Curr_Buy
    big_table2['Currency_Sell'] = Curr_Sell

    Profit2 = big_table2.loc[big_table2['Status'].isin(['SL', 'TP']), 'MTM'].sum()
    Profit2 = "${:,.2f}".format(Profit2)

    prefinal_table = big_table2.copy(deep=True)
    prefinal_table = prefinal_table[prefinal_table['Trades'].isin(['Tx Done'])]

    # final_table = big_table2.copy(deep=True)
    # final_table = final_table[final_table['Trades'].isin(['Tx Done'])]
    # final_table = final_table.drop(
    #     columns=[ccy_a, ccy_b, 'NLog', 'Candle_Average', 'StDev', 'Z-Score', 'Signal', 'Buy_Price', 'Sell_Price', 'Trades'])
    final_table = pd.DataFrame()

    final_table['Date'] = prefinal_table['Date']
    final_table['Currency_Buy'] = prefinal_table['Currency_Buy']
    final_table['Currency_Sell'] = prefinal_table['Currency_Sell']
    final_table['Buy_Price'] = prefinal_table['Buy_Price_F']
    final_table['Sell_Price'] = prefinal_table['Sell_Price_F']
    final_table['Status'] = prefinal_table['Status']
    final_table['MTM'] = prefinal_table['MTM']

    final_table.to_csv('Backtesting.csv')
    # print(final_table)

    return final_table.to_dict('records'), [{"name": i, "id": i} for i in final_table.columns], Profit2

@app.callback(
    Output('placeholder-div', 'children'),
    [
        Input('trade-button', 'n_clicks'),
        State('contract-symbol', 'value'),
        State('contract-sec-type', 'value'),
        State('contract-currency', 'value'),
        State('contract-exchange', 'value'),
        State('contract-primary-exchange', 'value'),
        State('order-action', 'value'),
        State('order-type', 'value'),
        State('order-size', 'value'),
        State('order-lmt-price', 'value'),
        State('order-account', 'value')
    ],
    prevent_initial_call = True
)
def place_order(n_clicks, contract_symbol, contract_sec_type,
                contract_currency, contract_exchange,
                contract_primary_exchange, order_action, order_type,
                order_size, order_lmt_price, order_account):
    # Contract object: STOCK
    contract = Contract()
    contract.symbol = contract_symbol
    contract.secType = contract_sec_type
    contract.currency = contract_currency
    contract.exchange = contract_exchange
    contract.primaryExchange = contract_primary_exchange

    # ===== The above contract object needs to be a currency pair for our algo
    # contract = Contract()
    # contract.symbol = currency_string.split(".")[0]
    # contract.secType = 'CASH'
    # contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    # contract.currency = currency_string.split(".")[1]

    # Example LIMIT Order
    order = Order()
    order.action = order_action
    order.orderType = order_type
    order.totalQuantity = order_size

    if order_type == 'LMT':
        order.lmtPrice = order_lmt_price

    if order_account:
        order.account = order_account

    ibkr_async_conn.reqIds(1)

    # Place orders!
    ibkr_async_conn.placeOrder(
        ibkr_async_conn.next_valid_id,
        contract,
        order
    )

    return ''

if __name__ == "__main__":
    app.run_server()
