from dash import dash_table, dcc, html
import datetime
import pandas as pd
import dash_bootstrap_components as dbc


backtest_parameters = html.Div(
    [
        dbc.Label("Candle Average"),
        dbc.Input(id="candle-average", type="number", value="7"),
        dbc.Label("Threshold Buy"),
        dbc.Input(id="threshold-buy", type="number", value="1"),
        dbc.Label("Threshold Sell"),
        dbc.Input(id="threshold-sell", type="number", value="-1"),
        dbc.Label("Take Profit USD"),
        dbc.Input(id="take-profit-usd", type="number", value=225),
        dbc.Label("Stop Loss USD"),
        dbc.Input(id="stop-loss-usd", type="number", value=-225),
        dbc.Label("Lot Size AUD"),
        dbc.Input(id="lot-size-aud", type="number", value=100000),
        dbc.Label("Lot Size NZD"),
        dbc.Input(id="lot-size-nzd", type="number", value=100000),
        html.Hr(),
        html.Button('Run Backtest', id='backtest-button', n_clicks=0),
        html.Br(),
    ],

)

# df = pd.read_csv(r"trades.csv")
# backtest_page = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]),


# # reading file
# df = pd.read_csv(r"trades.csv")
#
# # Trying to build this datatable
# backtest_page = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
