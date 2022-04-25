from dash import dash_table
import datetime
import pandas as pd

pairBlotter = pd.DataFrame(
    columns=['Date', 'Curr_A_(BUY)', 'Curr_B_(SELL)', 'signal', 'Buy_price', 'Sell_price', 'size']
)

pair_blotter = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in pairBlotter.columns],
    data=pairBlotter.to_dict('records'),
    id='pairBlotter-link'
)



