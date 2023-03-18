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
import warnings
warnings.filterwarnings('ignore')

# 更新tab 3&4的内容，讲tab2种的growth rate function 更新替换原来的内容

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

# Define a function to subset the original df to only include the top 5 companies in each sector
def top_5_company(time_range, df):
      df_selected = select_time_range(df, time_range)
      company_growth_rate = df_selected.groupby(['GICS Sector', 'Symbol']).apply(lambda x: (x['Close'].iloc[-1] - x['Close'].iloc[0])/x['Close'].iloc[0]).reset_index(name='Growth Rate')

      # Filter the top 5 companies in each sector
      top_5 = company_growth_rate.groupby('GICS Sector').apply(lambda x: x.nlargest(5, 'Growth Rate'))
      top_5 = top_5.reset_index(drop=True)

      # Obtain the symbol of top 5 companies in each sector
      top_5_symbol = top_5['Symbol'].unique().tolist()

      # Subset the df to only include the top 5 companies in each sector
      df_top_5 = df_selected[df_selected['Symbol'].isin(top_5_symbol)]

      return df_top_5


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
                  # tab 3 - 
                  dbc.Tab(html.Div([
                  html.Div([
                        dcc.Dropdown(
                              id='dropdown_sector',
                              options=[],
                              value=[],
                              style={'width':'300px', 'float':'left'}),
                        dcc.Checklist(
                              id='checkbox_company',
                              options=[],
                              value=[],
                              style={'float':'left', 'margin-left':'10px'}),
                  ], style={'width':'100%', 'display':'inline-block'}),
                  html.Div([
                        html.Iframe(
                              id='scatter', style={'width': '100%', 'height': '70vh', 'margin-left':'10%', 'margin-top':'10%'})
                  ], style={'width':'50%', 'height':'90vh', 'float':'left'}),
                  html.Div([
                        html.Iframe(
                              id='pie', style={'width': '100%', 'height': '70vh', 'margin-left':'10%', 'margin-top':'10%'})
                  ], style={'width':'50%', 'height':'90vh', 'float':'right'})
                  ]), label='Top 5 companies in SP500 GICS sectors')
            ])
      ], style={'width':'80%', 'height':'100%', 'float':'right', 'margin':'0px'})
      ], style={'height':page_height, 'margin':'0px'}
)



#! callback for tab 3
@app.callback(
      Output('dropdown_sector', 'options'),
      [Input('time_range_selector', 'value')]
)
def update_company_options(time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)
      sectors = df_top_5['GICS Sector'].unique().tolist()
      options = [{'label': sector, 'value': sector} for sector in sectors]
      return options

@app.callback(
      Output('dropdown_sector', 'value'),
      [Input('time_range_selector', 'value')]
)
def update_company_options(time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)
      sectors = df_top_5['GICS Sector'].unique().tolist()
      return sectors[0]

# Define the callback to update the options of the checkbox based on the selected sector
@app.callback(
      Output('checkbox_company', 'options'),
      [Input('dropdown_sector', 'value'),
      Input('time_range_selector', 'value')]
)
def update_company_options(selected_sector, time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)
      df_top_5_selected_sector = df_top_5[df_top_5['GICS Sector'] == selected_sector]
      top_5_symbol = df_top_5_selected_sector['Symbol'].unique().tolist()
      options = [{'label': symbol, 'value': symbol} for symbol in top_5_symbol]
      return options

@app.callback(
      Output('checkbox_company', 'value'),
      [Input('dropdown_sector', 'value'),
      Input('time_range_selector', 'value')]
)
def update_company_options(selected_sector, time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)
      df_top_5_selected_sector = df_top_5[df_top_5['GICS Sector'] == selected_sector]
      top_5_symbol = df_top_5_selected_sector['Symbol'].unique().tolist()
      return top_5_symbol

# Define the callback to update the graph based on the selected sector and companies
@app.callback(
      Output('scatter', 'srcDoc'),
      [Input('dropdown_sector', 'value'),
      Input('checkbox_company', 'value'),
      Input('time_range_selector', 'value')]
)
def update_trend_line(selected_sector, selected_companies, time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)

      df_top_5_selected_sector = df_top_5[df_top_5['GICS Sector'] == selected_sector]
      df_top_5_selected_sector['Date'] = df_top_5_selected_sector['Date'].astype(str).str[:10]
      df_top_5_selected_sector['Date'] = pd.to_datetime(df_top_5_selected_sector['Date'], format='%Y-%m-%d')
      if not selected_companies:
            # If no companies are selected, return an empty dataframe
            df_top_5_selected_sector_company = pd.DataFrame(columns=df_top_5.columns)
      else:
            # Filter the dataframe based on the selected companies
            df_top_5_selected_sector_company = df_top_5_selected_sector[
                  df_top_5_selected_sector['Symbol'].isin(selected_companies)]

      chart = alt.Chart(df_top_5_selected_sector_company).mark_line().encode(
            x='Date:T',
            y='Close:Q',
            color='Symbol:N',
            tooltip=['Date','Symbol:N', 'Close:Q']
      ).properties(
            title='Top 5 Companies by Growth Rate'
      ).interactive()
      return chart.to_html()

#!
# Define the callback to update the graph based on the selected sector
@app.callback(Output('pie', 'srcDoc'),
      [Input('dropdown_sector', 'value'),
      Input('time_range_selector', 'value')])
def update_pie_chart(selected_sector, time_range):
      df_top_5 = top_5_company(time_range, df_bar_chart)

      df_top_5_selected_sector = df_top_5[df_top_5['GICS Sector'] == selected_sector]
      df_top_5_selected_sector['Date'] = df_top_5_selected_sector['Date'].astype(str).str[:10]
      df_top_5_selected_sector['Date'] = pd.to_datetime(df_top_5_selected_sector['Date'], format='%Y-%m-%d')

      df_summary = df_top_5_selected_sector.groupby('Symbol', as_index=False).sum('Volume')
      df_summary['Proportion'] = df_summary['Volume']/sum(df_summary['Volume'])
      chart = alt.Chart(df_summary).mark_arc().encode(
            color='Symbol:N',
            theta='Volume:Q',
            tooltip=['Symbol:N', 'Volume:Q', 'Proportion:Q']
      ).properties(
            title='Top 5 Companies Volume Proportion'
      ).configure_view(
            strokeWidth=0
      )
      return chart.to_html()

if __name__ == '__main__':
      app.run_server(debug=True)
