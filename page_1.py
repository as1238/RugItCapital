from dash import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import dash_dangerously_set_inner_html
from tradingview_ta import TA_Handler, Interval, Exchange
import time
from urllib.parse import urlparse, parse_qs
import json
html.P("This is the content of page 1!")

#page_1 = html.Div([
 #   dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
page_1 = html.Div([
    html.H4("Welcome to Rugit Capital - Algorithmic Trading strategy (in process..)"),
    html.Br(),
    html.Div([
    html.Iframe(
srcDoc='''
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/AUDNZD/technicals/" rel="noopener" target="_blank"><span class="blue-text">Technical Analysis for AUDNZD</span></a> by TradingView</div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {
  "interval": "1m",
  "width": 425,
  "isTransparent": false,
  "height": 450,
  "symbol": "OANDA:AUDNZD",
  "showIntervalTabs": true,
  "locale": "en",
  "colorTheme": "light"
}
  </script>
</div>
<!-- TradingView Widget END -->
       ''',

    style={"width": 500, "height": 550, "margin-right": '-50%', "margin-left": '30%'})
    ]),

    html.Div([
    html.Iframe(
srcDoc='''
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div id="tradingview_c1606"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/AUDNZD/" rel="noopener" target="_blank"><span class="blue-text">AUDNZD Chart</span></a> by TradingView</div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {
  "width": 980,
  "height": 610,
  "symbol": "AUDNZD",
  "interval": "D",
  "timezone": "Etc/UTC",
  "theme": "light",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#f1f3f6",
  "enable_publishing": false,
  "allow_symbol_change": true,
  "container_id": "tradingview_c1606"
}
  );
  </script>
</div>
<!-- TradingView Widget END -->
    ''',

    style={"width": 1000, "height": 640,  "margin-right": '-50%', "margin-left": '5%'})
])

    ])




# <!-- TradingView Widget BEGIN -->
# <div class="tradingview-widget-container">
#   <div class="tradingview-widget-container__widget"></div>
#   <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/AUDNZD/technicals/" rel="noopener" target="_blank"><span class="blue-text">Technical Analysis for AUDNZD</span></a> by TradingView</div>
#   <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
#   {
#   "interval": "1m",
#   "width": 425,
#   "isTransparent": false,
#   "height": 450,
#   "symbol": "OANDA:AUDNZD",
#   "showIntervalTabs": true,
#   "locale": "en",
#   "colorTheme": "light"
# }
#   </script>
# </div>
# <!-- TradingView Widget END -->