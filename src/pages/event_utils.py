import re
from pathlib import Path
import os 
import pandas as pd
import numpy as np
import unidecode
from typing import Dict, Tuple

SPECIAL_EVENTS = ['OPEC-JMMC Meetings', 'OPEC Meetings', 'G20 Meetings', 
                  'G7 Meetings', 'Jackson Hole Symposium', 'WEF Annual Meetings',
                  'IMF Meetings']


def get_df_calendar_filtered(df_calendar, event, ccy):
    
    if event not in SPECIAL_EVENTS:
        df_calendar_filtered = df_calendar[(df_calendar['Event'] == event) & (df_calendar['Currency'] == ccy)]
    else:
        df_calendar_filtered = df_calendar[(df_calendar['Event'] == event)]
    df_calendar_filtered['Datetime'] = df_calendar_filtered['Date'] + ' ' + df_calendar_filtered['Time']
    df_calendar_filtered['Date'] = pd.to_datetime(df_calendar_filtered['Date'])
    
    df_calendar_filtered = df_calendar_filtered[(df_calendar_filtered['Day'] != 'Sun') & 
                                                (df_calendar_filtered['Day'] != 'Sat')]
    df_calendar_filtered = df_calendar_filtered.sort_values(by="Date")
    
    return df_calendar_filtered

def get_df_price_RT(pair, price_RT=None):
    
    header_list = ['Exchange Date', 'Bid', 'Ask', 'High', 'Low', 'Open', 'Refresh Rate', 
              'BidNet', 'Bid%Chg', f'{pair}00H= CHT', f'{pair}08H= CHT', f'{pair}16H= CHT', 'Date']

    
    if price_RT == None:
        price_RT = Path(f"data/RT_data/{pair}.csv")
    
    df_price_RT = pd.read_csv(price_RT, names=header_list, skiprows=[0])
    df_price_RT['Date'] = pd.to_datetime(df_price_RT['Date'])
    
    ## Clean df d1: Remove Sunday and Saturday
    df_price_RT['Day_of_week'] = df_price_RT['Date'].dt.day_name()
    df_price_RT = df_price_RT[(df_price_RT['Day_of_week'] != 'Sunday') & (df_price_RT['Day_of_week'] != 'Saturday')]
    df_price_RT = df_price_RT.sort_values(by="Date")
    
    df_price_RT['Day_1_bf'] = df_price_RT['Date'].shift(1)
    df_price_RT['Day_2_bf'] = df_price_RT['Date'].shift(2)
    df_price_RT['Day_3_bf'] = df_price_RT['Date'].shift(3)

    df_price_RT['Day_1_at'] = df_price_RT['Date'].shift(-1)
    df_price_RT['Day_2_at'] = df_price_RT['Date'].shift(-2)
    df_price_RT['Day_3_at'] = df_price_RT['Date'].shift(-3)
    df_price_RT['Day_4_at'] = df_price_RT['Date'].shift(-4)
    df_price_RT['Day_5_at'] = df_price_RT['Date'].shift(-5)


    df_price_RT[f'{pair}00H_Day_1_bf'] = df_price_RT[f'{pair}00H= CHT'].shift(1)
    df_price_RT[f'{pair}00H_Day_2_bf'] = df_price_RT[f'{pair}00H= CHT'].shift(2)
    df_price_RT[f'{pair}00H_Day_3_bf'] = df_price_RT[f'{pair}00H= CHT'].shift(3)

    df_price_RT[f'{pair}00H_Day_1_at'] = df_price_RT[f'{pair}00H= CHT'].shift(-1)
    df_price_RT[f'{pair}00H_Day_2_at'] = df_price_RT[f'{pair}00H= CHT'].shift(-2)
    df_price_RT[f'{pair}00H_Day_3_at'] = df_price_RT[f'{pair}00H= CHT'].shift(-3)
    df_price_RT[f'{pair}00H_Day_4_at'] = df_price_RT[f'{pair}00H= CHT'].shift(-4)
    df_price_RT[f'{pair}00H_Day_5_at'] = df_price_RT[f'{pair}00H= CHT'].shift(-5)


    df_price_RT[f'{pair}08H_Day_1_bf'] = df_price_RT[f'{pair}08H= CHT'].shift(1)
    df_price_RT[f'{pair}08H_Day_2_bf'] = df_price_RT[f'{pair}08H= CHT'].shift(2)
    df_price_RT[f'{pair}08H_Day_3_bf'] = df_price_RT[f'{pair}08H= CHT'].shift(3)

    df_price_RT[f'{pair}08H_Day_1_at'] = df_price_RT[f'{pair}08H= CHT'].shift(-1)
    df_price_RT[f'{pair}08H_Day_2_at'] = df_price_RT[f'{pair}08H= CHT'].shift(-2)
    df_price_RT[f'{pair}08H_Day_3_at'] = df_price_RT[f'{pair}08H= CHT'].shift(-3)
    df_price_RT[f'{pair}08H_Day_4_at'] = df_price_RT[f'{pair}08H= CHT'].shift(-4)
    df_price_RT[f'{pair}08H_Day_5_at'] = df_price_RT[f'{pair}08H= CHT'].shift(-5)


    df_price_RT[f'{pair}16H_Day_1_bf'] = df_price_RT[f'{pair}16H= CHT'].shift(1)
    df_price_RT[f'{pair}16H_Day_2_bf'] = df_price_RT[f'{pair}16H= CHT'].shift(2)
    df_price_RT[f'{pair}16H_Day_3_bf'] = df_price_RT[f'{pair}16H= CHT'].shift(3)

    df_price_RT[f'{pair}16H_Day_1_at'] = df_price_RT[f'{pair}16H= CHT'].shift(-1)
    df_price_RT[f'{pair}16H_Day_2_at'] = df_price_RT[f'{pair}16H= CHT'].shift(-2)
    df_price_RT[f'{pair}16H_Day_3_at'] = df_price_RT[f'{pair}16H= CHT'].shift(-3)
    df_price_RT[f'{pair}16H_Day_4_at'] = df_price_RT[f'{pair}16H= CHT'].shift(-4)
    df_price_RT[f'{pair}16H_Day_5_at'] = df_price_RT[f'{pair}16H= CHT'].shift(-5)
    
    df_price_RT['High_Day_1_bf'] = df_price_RT['High'].shift(1)
    df_price_RT['High_Day_1_at'] = df_price_RT['High'].shift(-1)

    df_price_RT['Low_Day_1_bf'] = df_price_RT['Low'].shift(1)
    df_price_RT['Low_Day_1_at'] = df_price_RT['Low'].shift(-1)
    
    return df_price_RT

def combine_calendar_with_price_RT(df_calendar_filtered, 
                                   df_price_RT, 
                                   event_valid_string, 
                                   pair, ccy, output_dir=None):
    
    export_headers = ['Date', 'Datetime', 'Day', 'Event', 'Currency', 'Impact', 'Actual', 'Forecast', 'Previous',
              f'{pair}00H_Day_3_bf', f'{pair}08H_Day_3_bf', f'{pair}16H_Day_3_bf',
              f'{pair}00H_Day_2_bf', f'{pair}08H_Day_2_bf', f'{pair}16H_Day_2_bf',
              f'{pair}00H_Day_1_bf', f'{pair}08H_Day_1_bf', f'{pair}16H_Day_1_bf',
              'Bid', 'Ask', 'High', 'Low', 'Open',f'{pair}00H= CHT', f'{pair}08H= CHT', f'{pair}16H= CHT',
              f'{pair}00H_Day_1_at', f'{pair}08H_Day_1_at', f'{pair}16H_Day_1_at', 
              f'{pair}00H_Day_2_at', f'{pair}08H_Day_2_at', f'{pair}16H_Day_2_at',
              f'{pair}00H_Day_3_at', f'{pair}08H_Day_3_at', f'{pair}16H_Day_3_at',
              f'{pair}00H_Day_4_at', f'{pair}08H_Day_4_at', f'{pair}16H_Day_4_at',
              f'{pair}00H_Day_5_at', f'{pair}08H_Day_5_at', f'{pair}16H_Day_5_at',
              'High_Day_1_bf', 'High_Day_1_at', 'Low_Day_1_bf', 'Low_Day_1_at',
              'Day_1_bf', 'Day_2_bf', 'Day_3_bf', 
              'Day_1_at', 'Day_2_at', 'Day_3_at', 'Day_4_at', 'Day_5_at']
    
    result = pd.merge(df_calendar_filtered, df_price_RT, how='left', on='Date')
    result = result[export_headers]
    
#     print(f'Result Num of Rows {pair}: {result.shape[0]}')
    if output_dir != None:
        result.to_csv(output_dir / f'{ccy}_{event_valid_string}_01-2011_04-2021_GMT0_{pair}.csv', 
                  header=True, 
                  columns=export_headers,
                  index=False)
    return result

def calc_pips(high, low, pair):
    if pair[3:] == 'JPY':
        return (high-low)*100
    else:
        return (high-low)*10000

def calc_volatility(df: pd.DataFrame, 
                    base_ccy: str, 
                    event: str, 
                    pair: str) -> pd.DataFrame:
    df['PAR'] = ((df['Bid'] + df['Ask'])/2 + df['High'] + df['Low'] + df['Open'])/4
        
    # Volatility
    df['Volatility_pips_bf'] = df.apply(lambda row: calc_pips(row['High_Day_1_bf'], 
                                                              row['Low_Day_1_bf'],
                                                              pair=pair), axis=1)
    df['Volatility_pips_af'] = df.apply(lambda row: calc_pips(row['High_Day_1_at'], 
                                                              row['Low_Day_1_at'],
                                                              pair=pair), axis=1)
    
    # Volatility Intraday
    df['Volatility_pips_intraday'] = df.apply(lambda row: 
                                               calc_pips(row['High'], 
                                                                  row['Low'],
                                                                  pair=pair), 
                                                        axis=1)

    return df