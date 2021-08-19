from typing import List
from pathlib import Path
from functools import reduce

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .event_utils import *

CCY_PAIRS = {
    "EUR": ["EURUSD", "EURJPY"],
    "GBP": ["GBPUSD", "GBPJPY"],
    "USD": ["EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDJPY", "USDCHF"],
    "NZD": ["NZDUSD", "NZDJPY"],
    "AUD": ["AUDJPY"],
    "CAD": ["USDCAD", "CADJPY"],
    "CHF": ["USDCHF"],
    "JPY": ["USDJPY"]
}

def render() -> None:
    st.title("Event Volatility")

    ff_calendar_path = Path("data/forex_calendar_01-2011_04-2021_GMT0.csv")
    calendar_df = pd.read_csv(ff_calendar_path)
    calendar_df = calendar_df[~calendar_df['Event'].astype(str).str.contains("Holiday")]
    calendar_df = calendar_df[~calendar_df['Time'].astype(str).str.contains("[a-z]", regex=True)]

    base_ccys: np.ndarray = calendar_df['Currency'].unique()
    events: np.ndarray = np.sort(calendar_df['Event'].unique().astype(str))

    event: str = st.sidebar.selectbox("Event:", events, index=0)
    base_ccys: np.ndarray = np.sort(calendar_df[calendar_df['Event'] == event]['Currency'].unique())

    if 'All' in base_ccys:
        base_ccys: np.ndarray = np.sort(calendar_df['Currency'].unique())
    
    base_ccy = st.sidebar.selectbox("Base Currency:", base_ccys, index=0)

    pairs: List[str] = CCY_PAIRS[base_ccy]
    pair: str = st.sidebar.selectbox("Pair:", pairs, index=0)

    price_path = Path(f"data/PFX Fixing 25.7.21/{pair}.xlsx")
    price_df_dict = pd.read_excel(price_path, 
                                  usecols="B:F", 
                                  skiprows=[0], 
                                  sheet_name=list(range(24)), 
                                  engine="openpyxl")
    price_df_dict = clean_price_df(price_df_dict)
    price_dfs = [price_df_dict[i] for i in list(range(24))]
    df_calendar_filtered = get_df_calendar_filtered(calendar_df, event, base_ccy)
    df_calendar_filtered['Hour'] = pd.to_datetime(df_calendar_filtered['Time']).dt.hour
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Date'],
                                            how='left'), [df_calendar_filtered] + price_dfs)

    df_merged['6 Hour Volatility'] = df_merged.apply(calc_6_hours_volatility, axis=1, pair="EURUSD")

    st.header(f"Volatility Histogram Chart")
    with st.expander("See charts"):
        fig, ax = plt.subplots()
        ax.set_title("6-Hour Volatility")
        ax.hist(df_merged['6 Hour Volatility'].dropna(), bins=10)
        st.pyplot(fig)

    st.header(f"Volatility Table")
    with st.expander("See table"):
        st.write(df_merged[['Datetime', '6 Hour Volatility']]
                    .dropna()
                    .assign(hack='')
                    .set_index('hack'))

