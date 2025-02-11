
import dash_bootstrap_components as dbc
from dash import dcc, html

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 62.5,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#f8f9fa",
}

SIDEBAR_HIDDEN = {
    "position": "fixed",
    "top": 62.5,
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink(
                    "Home Screen",
                    href="/home-screen",
                    id="home-screen-link"
                ),
                dbc.NavLink("Blotter", href="/blotter", id="blotter-link"),
                dbc.NavLink("Errors", href="/errors", id="errors-link"),
                dbc.NavLink("Backtesting", href="/Backtesting", id="pairBlotter-link")
            ],
            vertical=True,
            pills=True
        ),
        html.P(children="False", id='ibkr-async-conn-status'),
        html.Div(children='', id='placeholder-div'),
        dbc.Label('Master Client ID'),
        dbc.Input(id="master-client-id", type="number", value=10645),
        dbc.Label('Port'),
        dbc.Input(id="port", type="number", value=7497),
        dbc.Label('Hostname'),
        dbc.Input(id="hostname", type="text", value='127.0.0.1'),
        html.P(children='', id='uses-async'),
        html.Hr(),
        html.Button('Trade', id='trade-button', n_clicks=0),
        html.Hr(),
        #html.Button('Start Algo', id='start-algo-button', n_clicks=0),
        # dbc.Label('pair'),
        # dbc.Input(id="pair", type="text", value='AUD.USD'),
        # dbc.Label('candle average'),
        # dbc.Input(id="candle-avg", type="text", value='7'),
        # dbc.Label('tsh buy'),
        # dbc.Input(id="tsh-buy", type="text", value='-1'),
        # dbc.Label('tsh sell'),
        # dbc.Input(id="tsh-sell", type="text", value='1'),
        # dbc.Label('stop loss a'),
        # dbc.Input(id="stop-loss-a", type="text", value='-20'),
        # dbc.Label('stop loss b'),
        # dbc.Input(id="stop-loss-b", type="text", value='20'),
        # dbc.Label('lot size a'),
        # dbc.Input(id="lot-size-a", type="text", value='100000'),
        # dbc.Label('lot size b'),
        # dbc.Input(id="lot-size-b", type="text", value='100000'),
        dbc.Label('Contract Symbol (change this?)'),
        dbc.Input(id="contract-symbol", type="text", value='AUD.USD'),
        dbc.Label('Contract SecType'),
        dbc.Input(id="contract-sec-type", type="text", value='CASH'),
        dbc.Label('Contract Currency'),
        dbc.Input(id="contract-currency", type="text", value='USD'),
        dbc.Label('Contract Exchange'),
        dbc.Input(id="contract-exchange", type="text", value='IDEALPRO'),
        dbc.Label('Contract Primary Exchange'),
        dbc.Input(id="contract-primary-exchange", type="text", value='IDEALPRO'),
        html.Hr(),
        dbc.Label("Order Action"),
        dbc.Input(id="order-action", type="text", value="BUY"),
        dbc.Label("Order Type"),
        dbc.Input(id="order-type", type="text", value="MKT"),
        dbc.Label("Order Size"),
        dbc.Input(id="order-size", type="number", value=100),
        dbc.Label("Limit Price"),
        dbc.Input(id="order-lmt-price", type="number", placeholder='Limit '
                                                                   'Price'),
        dbc.Label("Account"),
        dbc.Input(id="order-account", type="text", value = 'DU5011570'),
        dbc.Label(),
        dbc.Label(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br()
    ],
    id="sidebar",
    style=SIDEBAR_STYLE
)
