from dash import dash_table, dcc, html
import datetime
import pandas as pd
import dash_bootstrap_components as dbc

df = pd.read_csv(r"trades.csv")

backtest_results = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]),
