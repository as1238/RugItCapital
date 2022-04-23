import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from interactive_trader.synchronous_functions import data_pull
from page_1 import page_1
from order_page import order_page
from error_page import error_page
from navbar import navbar
from sidebar import sidebar, SIDEBAR_HIDDEN, SIDEBAR_STYLE
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from interactive_trader import *
from datetime import datetime
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
            id = 'ibkr-update-interval',
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
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/home-screen"]:
        return page_1
    elif pathname == "/blotter":
        return order_page
    elif pathname == "/errors":
        return error_page
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

#HERE WE RECEIVE FROM THE FRONTEND THE PARAMETERS
#WE SHOULD DO An APPCALLBACK, that triggers the rug_it_entry function and output the table in the front end


#STILL NEED TO WORK ON THE SL and TP strategies
#Def rug_it_entry
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
            trades_table.loc[ind, 'size'] = lot_size_a
        elif my_data[ind] > tsh_sell:
            my_trade.append("SELL")
            trades_table.loc[ind, 'Date'] = (date.today())
            trades_table.loc[ind, 'Curr_A_(BUY)'] = ccy_a
            trades_table.loc[ind, 'Curr_B_(SELL)'] = ccy_b
            trades_table.loc[ind, 'signal'] = "SELL"
            trades_table.loc[ind, 'Buy_price'] = 0
            trades_table.loc[ind, 'Sell_price'] = 0
            trades_table.loc[ind, 'size'] = lot_size_b
        else:
            my_trade.append('')

    pair_data['z_score'] = my_data
    pair_data['signal'] = my_trade

    #print(trades_table)
    return trades_table


if __name__ == "__main__":
    app.run_server()