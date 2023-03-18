import pandas as pd
import yfinance as yf
import os

def generate_Global_index(interval='1d', category='Close', start_date='2022-01-01'):
      """
      Generates Global index data and saves it to a CSV file.
      Global index includes:
            (US Market)
            - S&P 500 : ^GSPC
            - S&P 500 Energy : ^GSPE
            - S&P 500 Industrials : ^SP500-20
            - S&P 500 Consumer Discretionary : ^SP500-30
            (London Market)
            - FTSE 100 Index : ^FTSE
            (Europe Market)
            - Euro Stoxx 50 : ^STOXX50E
            (Hong Kong Market)
            - HANG SENG INDEX: ^HSI
            (Tokyo Market)
            - Nikkei 225: ^N225
      Parameters:
            interval (str, optional): The interval to download the data with. 
                  Options are:
                  '1d' = daily data
                  '1wk' = weekly data
                  '1mo' = monthly data
                  Default is '1d'.
            category (str, optional): The category of data to include in the data frame. 
                  Options are:
                  'Open'
                  'High'
                  'Low'
                  'Close'
                  'Adj Close'
                  'Volume'
                  Default is 'Close'.
            save_path (str, optional): The path to the directory where the CSV file will be saved. 
                  Default is None.
            start_date (str, optional): The start date of the data. Default is '2022-01-01'.
      """
      
      index_dict = {
            'S&P_original': '^GSPC',
            'S&P_energy': '^GSPE',
            'S&P_industry': '^SP500-20',
            'S&P_consumer': '^SP500-30',
            'FTSE_100': '^FTSE',
            'Euro_Stoxx_50': '^STOXX50E',
            'HANG_SENG': '^HSI',
            'Nikkei_225': '^N225'
      }
      index_name = list(index_dict.keys())
      index_name.insert(0, 'date')
      df_total = pd.DataFrame(columns=index_name)
      
      for index in index_dict.keys():
            symbol = index_dict[index]
            df = yf.download([symbol], group_by='ticker', interval=interval, start=start_date)
            df = df[[category]]
            df = df.reset_index()
            df = df.rename(columns = {'Date': 'date','Close': index})
            df['date'] = df['date'].astype(str).str[:10]
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            
            
            if not os.path.exists(os.getcwd()+'/data'):
                  os.makedirs(os.getcwd()+'/data')
            df.to_csv('data/'+index+'.csv', index=False)
            print('Global_'+index+'.csv', 'is saved')   



      # read all csv files in the directory
      # concat all csv files into one dataframe , use query on date column so that all dataframes have same date column
      folder_path = os.getcwd()+'/data'
      dfs = []
      for key, value in index_dict.items():
            df = pd.read_csv(f"{folder_path}/{key}.csv")
            df.set_index('date', inplace=True)
            df.rename(columns={'close': value}, inplace=True)
            dfs.append(df)

      # Merge all dataframes based on their index (date column)
      df_total = pd.concat(dfs, axis=1, join='outer')
      df_total.index = pd.to_datetime(df_total.index)
      df_total.sort_index(inplace=True)
      
      print('Global_index.csv', 'is saved')
      df_total.to_csv('data/Global_index.csv', index=True)
      



def select_time_range(df, time_range):
      # take time_range as the number of rows to select
      # start from the last row
      df = df.iloc[-time_range:]
      return df

# generate Global index data
generate_Global_index()
global_df = pd.read_csv('data/Global_index.csv')

# select the last 100 rows
# select_time_range(global_df, 100)