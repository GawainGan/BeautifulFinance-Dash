import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import yfinance as yf
from functools import reduce
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

last_year_today = str(date.today() - relativedelta(years=1))
index_dict = {
      # US Market:
      'S&P_original': '^GSPC', 
      'S&P_energy': '^GSPE', 
      'S&P_industry': '^SP500-20', 
      'S&P_consumer': '^SP500-30',
      # London Market:
      'FTSE_100': '^FTSE', 
      # Europe Market:
      'Euro_Stoxx_50': '^STOXX50E', 
      # Hong Kong Market:
      'HANG_SENG': '^HSI', 
      # Tokyo Market:
      'Nikkei_225': '^N225'
}

def get_daily_data(dicts=index_dict, category='Close', start_date=last_year_today):
      """
      Parameters:
            dicts (dict, optional): The dictionary of global index. Default including 8 indices.
            category (str, optional): The category of data to include in the data frame. 
                  Options are:
                  'Open', 'High', 'Low', 'Close' (default), 'Adj Close', 'Volume'
            start_date (str, optional): The start date of the data. Default is last year today.
      """
      index_name = list(dicts.keys())
      index_name.insert(0, 'date')
      df_total = pd.DataFrame(columns=index_name)
      dfs = []
      for index in dicts.keys():
            symbol = dicts[index]
            df = yf.download([symbol], group_by='ticker', interval='1d', start=start_date, progress=False)
            df = df[[category]].reset_index()
            df = df.rename(columns = {'Close': index})
            df['Date'] = df['Date'].astype(str).str[:10]
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
            dfs.append(df)

      # Merge all dataframes based on date column
      df_total = reduce(lambda  left,right: pd.merge(left, right, on=['Date'], how='outer'), dfs)
      df_total = df_total.sort_values('Date')

      dates = [i.strftime("%Y-%m-%d") for i in pd.date_range(start=last_year_today, end=date.today(), freq='D')]
      df_date = pd.DataFrame(dates, columns=['Date'])
      df_date['Date'] = pd.to_datetime(df_date['Date'], format='%Y-%m-%d')
      df_total = df_date.merge(df_total, on='Date', how='outer')
      
      return df_total


def select_time_range(df, time_range):
      # take time_range as the number of rows to select
      # start from the last row
      end = df['Date'].max()
      d = datetime.timedelta(days=time_range)
      start = end - d
      select = (df['Date'] >= start) & (df['Date'] <= end)
      return df.loc[select]

def moving_average(df, symbol, moving_average_window):
      ma = df[symbol].rolling(window=moving_average_window).mean()
      return ma

moving_days = [['7 Day', '7'], ['15 Day', '15'], ['30 Day', '30']]

# get data
df_line_chart = get_daily_data()

df_line_chart['Date'] = pd.to_datetime(df_line_chart['Date'])
df_line_chart.set_index('Date', inplace=True)
# Interpolate null values
df_line_chart = df_line_chart.interpolate()
df_line_chart.reset_index(inplace=True)
df_line_chart.rename({'index':'Date'})
symbols = df_line_chart.columns[1:] # exclude Date column


# css
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
US_Market = {'font-size': '15px', 'text-align':'left', 'color':'#036d90', 'margin-left':'20px'}
other_Market = {'font-size': '15px', 'text-align':'left', 'margin-left':'20px'}
labels = {'display':'inline', 'font-size':'20px', 'margin-left':'5px'}
page_height = '100vh'

app.layout = html.Div([
      # left part
      html.Div([
            # growth rate info
            html.Div([
                  html.P('Summary of Stock Symbol', style={'font-size': '25px', 'text-align':'center'}),
                  html.P('SP500 - US Market', style=US_Market),
                  html.P('FTSE_100 - London Market', style=other_Market),
                  html.P('Euro_Stoxx_50 - Europe Market', style=other_Market),
                  html.P('HANG_SENG - Hong Kong Market', style=other_Market),
                  html.P('Nikkei_225 - Toyko Market', style=other_Market),
            ], style={'border-style':'solid', 'border-color':'#a1979e', 'margin':'10px'}),
            # radio
            html.Div([
                  dcc.RadioItems(
                  id='time_range_selector',
                  options=[
                        {'label':html.P(['Last 7 Days'], style=labels), 'value':7},
                        {'label':html.P(['Last 30 Days'], style=labels), 'value':30},
                        {'label':html.P(['Last 90 Days'], style=labels), 'value':90},
                        {'label':html.P(['Last 180 Days'], style=labels), 'value':180},
                        {'label':html.P(['Last Year'], style=labels), 'value':365}
                  ], value=7, labelStyle={'display': 'block'}
                  )
            ], style={'margin':'20px'})
      ], style={'width':'20%', 'height':'100%', 'float':'left', 'margin':'0px', 'background':'#e1edd5'}),
      # right part
      html.Div([
            dbc.Tabs([
                  # tab 1 -  Stock markets compare trend plot
                  dbc.Tab(html.Div([
                  html.Div([
                        html.Div([
                              dcc.Dropdown(
                              id='symbol-dropdown',
                              options=[{'label': symbol, 'value': symbol} for symbol in symbols],
                              value='S&P_original',
                              style={'width': '200px', 'float':'left'}),
                              dcc.Dropdown(
                              id='compare-dropdown',
                              options=[{'label': symbol, 'value': symbol} for symbol in symbols],
                              value='FTSE_100',
                              style={'width': '200px', 'float':'left'})
                        ], style={'height':'10%'}),
                        # add Radioitem for moving average
                        html.P('Chose Moving Average'),
                        dcc.Checklist(
                              id = 'moving_average_checklist',
                              options=[{'label': value[0], 'value': int(value[1])} for value in moving_days],
                              value=[],
                              inline=True,
                              # style={'float':'left', 'width':'100%', 'height':'10%', 'margin':'-10px','margin-left':'25px'}, # make the radio item in one line and set the margin
                              # labelStyle={'display': 'inline-block', 'margin-right': '20px'},
                              # inputStyle={'border-radius': '5px'},
                              
                        ),
                        dcc.Graph(id='line-chart', figure={}, style={'width':'90%','height':'90%', 'margin':'60px'})
                  ], style={'width':'100%', 'height':'80vh'})
                  ]), label='Stock markets compare trend plot'),
            ])
      ],style={'width':'80%', 'height':'100%', 'float':'right', 'margin':'0px'})
], 
      style={'height':page_height, 'margin':'0px'}      )

# callback for tab 1
@app.callback(Output('line-chart', 'figure'), 
      [Input('symbol-dropdown', 'value'), 
            Input('compare-dropdown', 'value'),
            Input('time_range_selector', 'value'),
            Input('moving_average_checklist', 'value'),# add moving average radio
      ])


def update_line_chart(symbol, compare_symbol, time_range, moving_average_window):
      df_selected = select_time_range(df_line_chart, time_range)
      fig = make_subplots(specs=[[{"secondary_y": True}]])
      # Add trace for selected index
      fig.add_trace(go.Scatter(x=df_selected['Date'], 
                                    y=df_selected[symbol], 
                                    name=symbol
                                    ), 
                        secondary_y=False,
                        ),
      
      # Add trace for comparison index
      fig.add_trace(go.Scatter(x=df_selected['Date'], y=df_selected[compare_symbol], name=compare_symbol), secondary_y=True)
      
      # adjust x and y axis content
      fig.update_xaxes(title_text="Date")
      fig.update_yaxes(tickprefix="$")
      
      # add moving average line
      if len(moving_average_window) != 0:
            ma_number = len(moving_average_window)
            for i in range(ma_number):
                  window = int(moving_average_window[i])
                  ma = moving_average(df_selected, symbol, window)
                  fig.add_trace(go.Scatter(x=df_selected['Date'], 
                                          y=ma, 
                                          name='MA {} for {} '.format(window, symbol)
                                          ), 
                              secondary_y=False)
            for i in range(ma_number):
                  window = int(moving_average_window[i])
                  ma_2nd = moving_average(df_selected, compare_symbol, window)
                  fig.add_trace(go.Scatter(x=df_selected['Date'], 
                                          y=ma_2nd, 
                                          name='MA {} for {}'.format(window, compare_symbol)
                                          ), 
                              secondary_y=True)
      
      fig.update_layout(
            xaxis=dict(title='Date'),
            yaxis=dict(title=symbol, 
                        showgrid=False),
            yaxis2=dict(title=compare_symbol, 
                              overlaying='y', 
                              side='right'),
            hovermode='x',
            title='{} vs {} Price'.format(symbol, compare_symbol),
      )
      return fig

if __name__ == '__main__':
      app.run_server(debug=True)