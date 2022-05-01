import dash_bootstrap_components as dbc
import html as html
from dash import dash_table
from dash import html
from dash import dcc
import pandas as pd




pairBlotter = pd.DataFrame(
    columns=['Date', 'Currency_Buy', 'Currency_Sell', 'Buy_Price', 'Sell_Price', 'Status', 'MTM']
)


dbc.Label('lot size a'),
dbc.Input(id="lot-size-a", type="text", value='100000'),
dbc.Label('lot size b'),
dbc.Input(id="lot-size-b", type="text", value='100000'),

pair_blotter = (html.Div(
        children = [
            html.Div(
                children = [
                    dbc.Label('Pair:'),
                    dbc.Input(id="pair", type="text", value='AUD.NZD')
                ],
                style = {
                    'display': 'inline-block',
                    'margin-right': '20px',
                }
            ),
            html.Div(
                children = [
                    dbc.Label('candle average'),
                    dbc.Input(id="candle-avg", type="text", value='9'),
                ],
                style = {
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            )
                   ]
),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dbc.Label('Threshold buy:'),
                            dbc.Input(id="tsh-buy", type="text", value='-1'),
                        ],
                        style={
                            'display': 'inline-block',
                            'margin-right': '20px',
                        }
                    ),
                    html.Div(
                        children=[
                            dbc.Label('Threshold sell:'),
                            dbc.Input(id="tsh-sell", type="text", value='1'),
                        ],
                        style={
                            'display': 'inline-block',
                            'padding-right': '50px'
                        }
                    ),
                    html.Div(
                        children=[
                            html.H4('The profit of this strategy is:'),
                            html.Div(id="profit", style={'color': 'blue', 'fontSize': 24}),
                        ],
                        style={
                            'display': 'inline-block',
                            'padding-right': '5px'
                        }

                    )
                ]
            ),

                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dbc.Label('Stop-loss:'),
                                dbc.Input(id="stop-loss-a", type="text", value='-2250'),
                            ],
                            style={
                                'display': 'inline-block',
                                'margin-right': '20px',
                            }
                        ),
                        html.Div(
                            children=[
                                dbc.Label('Take-profit:'),
                                dbc.Input(id="stop-loss-b", type="text", value='2250'),
                            ],
                            style={
                                'display': 'inline-block',
                                'padding-right': '5px'
                            }
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dbc.Label('Size trade'),
                                dbc.Input(id="lot-size", type="text", value='100000'),
                            ],
                            style={
                                'display': 'inline-block',
                                'margin-right': '20px',
                            }
                        ),
                        html.Div(
                            children=[
                                html.Button(' Run Backtesting ', id='start-algo-button', n_clicks=0),
                            ],
                            style={
                                'display': 'inline-block',
                                'padding-right': '5px'
                            }
                        )
                    ]
                ),
    html.Br(),
    html.Br(),
    dbc.Container(dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in pairBlotter.columns],
        data=pairBlotter.to_dict('records'),
        id='pairBlotter-link'
    )
    )
)





