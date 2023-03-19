import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from functools import reduce
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

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

def get_minutely_data(day, dicts=index_dict, category='Close'):
    index_name = list(dicts.keys())
    index_name.insert(0, 'date')
    df_total = pd.DataFrame(columns=index_name)
    dfs = []
    for index in dicts.keys():
        symbol = dicts[index]
        df = yf.download([symbol], group_by='ticker', interval='1m', progress=False)
        df = df[[category]].reset_index()
        df = df.rename(columns = {'Datetime': 'datetime', 'Close': index})
        df['datetime'] = df['datetime'].astype(str).str[:-6]
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
        dfs.append(df)
    df_total = reduce(lambda left,right: pd.merge(left, right, on=['datetime'], how='outer'), dfs)
    df_total['date'] = df_total['datetime'].astype(str).str[:10]
    df_total = df_total[df_total['date']==day]
    df_total.drop('date', axis=1, inplace=True)
    return df_total

def select_time_range(df, time_range):
    # take time_range as the number of rows to select
    # start from the last row
    end = df['Date'].max()
    d = datetime.timedelta(days=time_range)
    start = end - d
    select = (df['Date'] >= start) & (df['Date'] <= end)
    return df.loc[select]

def SP500_co_info(day=last_year_today):
    # Send a request to the URL and get the HTML content
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table containing the data
    table = soup.find('table', {'class': 'wikitable sortable', 'id': 'constituents'})

    # Extract the data from the table and put it into a list
    data = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        symbol = cols[0].text.strip()
        security = cols[1].text.strip()
        sector = cols[2].text.strip()
        sub_industry = cols[3].text.strip()
        location = cols[4].text.strip()
        date_added = cols[5].text.strip()
        cik = cols[6].text.strip()
        founded = cols[7].text.strip()
        data.append([symbol, security, sector, sub_industry, location, date_added, cik, founded])

    # Convert the list of data into a Pandas DataFrame
    columns = ['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'CIK', 'Founded']
    df1 = pd.DataFrame(data, columns=columns)
    
    SP500_Companies_name = df1['Symbol'].tolist()
    dfs = {}
    for i in tqdm(SP500_Companies_name):
        df2 = yf.download([i], group_by='ticker', interval='1d', start=day, progress=False)
        df2 = df2.reset_index()
        dfs[i] = df2

    # create new df with columns: date， close， symbol，  GICS Sector， GICS Sub-Industry in both SP500_df and each company df
    merged_df_whole = pd.DataFrame(columns=['Date', 'Close', 'Volume' ,'Symbol', 'GICS Sector', 'GICS Sub-Industry'])
    count = 0
    for i in SP500_Companies_name:
        if count != len(SP500_Companies_name):
                merged_df = pd.DataFrame(columns=['Date', 'Close', 'Volume' ,'Symbol', 'GICS Sector', 'GICS Sub-Industry'])
                price_df = dfs[i]
                merged_df['Date'] = price_df['Date']
                merged_df['Close'] = price_df['Close']
                merged_df['Volume'] = price_df['Volume']
                merged_df['Symbol'] = i
                merged_df['GICS Sector'] = df1[df1['Symbol'] == i]['GICS Sector'].values[0]
                merged_df['GICS Sub-Industry'] = df1[df1['Symbol'] == i]['GICS Sub-Industry'].values[0]
                merged_df = merged_df.dropna()
                
                merged_df_whole = pd.concat([merged_df_whole, merged_df], axis=0)
                count = count + 1
        else:
                break

    return merged_df_whole