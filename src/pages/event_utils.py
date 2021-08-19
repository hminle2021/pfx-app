import re
from pathlib import Path
import os 
import pandas as pd
import numpy as np
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

def clean_price_df(price_df_dict):
    for i in list(range(24)):
        price_df_dict[i] = price_df_dict[i].rename(columns={"Bid High": f"Bid High {i}H", 
                                            "Bid Low": f"Bid Low {i}H"})
        price_df_dict[i]['Date'] =  pd.to_datetime(price_df_dict[i]['Timestamp'])
        price_df_dict[i] = price_df_dict[i].drop(columns=['Timestamp', 'Bid Open', 'Bid Close'])
    return price_df_dict

def calc_6_hours_volatility(row, pair):
    
    row['max_bid_high'] = max(row[f"Bid High {row['Hour'] - 2}H"],
                             row[f"Bid High {row['Hour'] - 1}H"],
                             row[f"Bid High {row['Hour']}H"],
                             row[f"Bid High {row['Hour'] + 1}H"],
                             row[f"Bid High {row['Hour'] + 2}H"],
                             row[f"Bid High {row['Hour'] + 3}H"],
                             row[f"Bid High {row['Hour'] + 4}H"])
    row['min_bid_low'] =  min(row[f"Bid Low {row['Hour'] - 2}H"],
                             row[f"Bid Low {row['Hour'] - 1}H"],
                             row[f"Bid Low {row['Hour']}H"],
                             row[f"Bid Low {row['Hour'] + 1}H"],
                             row[f"Bid Low {row['Hour'] + 2}H"],
                             row[f"Bid Low {row['Hour'] + 3}H"],
                             row[f"Bid Low {row['Hour'] + 4}H"])
    if "JPY" in pair:
        return (row['max_bid_high'] - row['min_bid_low'])*100
    else:
        return (row['max_bid_high'] - row['min_bid_low'])*10000