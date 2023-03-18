import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
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
      'Nikkei_225': '^N225'}

def get_daily_data(dicts=index_dict, category='Close', start_date=last_year_today):
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


df_bar_chart = pd.read_csv('SP500_merged.csv', parse_dates=['Date'])
df_bar_chart = df_bar_chart[df_bar_chart['Symbol'] != 'GEHC']
def generate_growth_rate_mean(time_range):
      time_range = time_range
      df_selected = select_time_range(df_bar_chart, time_range)
      growth_rate_full = df_selected.groupby(['GICS Sector', 'Symbol'])['Close'].apply(lambda x: x.iloc[-1] / x.iloc[0] - 1)
      growth_rate_full = pd.DataFrame(growth_rate_full)
      growth_rate_full = growth_rate_full.reset_index()
      growth_top5 = growth_rate_full.groupby('GICS Sector').apply(lambda x: x.nlargest(5, 'Close'))
      growth_rate_top5 = growth_top5.sort_values(by='Close', ascending=False)
      growth_rate_top5 = growth_rate_top5.reset_index(drop=True)
      top5_name = growth_rate_top5.groupby('GICS Sector')['Symbol'].apply(lambda x: x.unique())
      top5_name = pd.DataFrame(top5_name)
      top5_name = top5_name.reset_index()

      growth_rate_mean = growth_rate_full.groupby('GICS Sector')['Close'].mean()
      growth_rate_mean = pd.DataFrame(growth_rate_mean)
      growth_rate_mean.rename(columns={'Close': 'growth_rate'}, inplace=True)
      growth_rate_mean = growth_rate_mean.reset_index()
      growth_rate_mean = growth_rate_mean.sort_values(by='growth_rate', ascending=False)
      growth_rate_mean = growth_rate_mean.join(top5_name.set_index('GICS Sector'), on='GICS Sector')
      
      return growth_rate_mean.reset_index()


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
                  ], value=7, labelStyle={'display': 'block'})
            ], style={'margin':'20px'})
      ], style={'width':'20%', 'height':'100%', 'float':'left', 'margin':'0px', 'background':'#e1edd5'}),
      # right part
      html.Div([
            dbc.Tabs([
                  # tab 2 - SP500 sectors growth rate rank
                  dbc.Tab(html.Div([
                  html.Div([
                        html.Div(id='bar-chart', children=[])
                  ], style={'width':'100%', 'height':'90vh',})
                  ]), label='SP500 sectors growth rate rank'),
            ]),
      ],style={'width':'80%', 'height':'100%', 'float':'right'})
],style={'height':page_height, 'margin':'0px'})

# callback for tab 2
@app.callback(Output('bar-chart', 'children'),
      [Input('time_range_selector', 'value')])
def update_output(time_range):
      growth_rate_mean = generate_growth_rate_mean(time_range)
      growth_rate_mean = growth_rate_mean.reset_index()
      fig = go.Figure(
            data=[
                  go.Bar(
                        x=growth_rate_mean['GICS Sector'], 
                        y=growth_rate_mean['growth_rate'], 
                        name= 'Growth Rate with Top 5 Stocks',
                        marker_color=growth_rate_mean['growth_rate'].apply(lambda x: 'green' if x > 0 else 'red'),
                        customdata=[', '.join(symbols) for symbols in growth_rate_mean['Symbol']],
                        hovertemplate = 'GICS Sector: %{x}<br>Growth Rate: %{y:.4%}<br>Top 5 Stocks:<br>%{customdata}',
                        )
                  ]
            )
      fig.update_layout(
            title='Sector Growth Rates',
            xaxis_title='Sector',
            yaxis_title='Growth Rate',
            xaxis={'categoryorder':'total descending'})

      
      return dcc.Graph(
            id='example-graph',
            figure=fig)

if __name__ == '__main__':
      app.run_server(debug=True)