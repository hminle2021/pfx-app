from typing import List
from pathlib import Path

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .event_utils import *

def render() -> None:
    st.title("Event Volatility")
    
    ccy_pairs = ['EURUSD', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD', 
                'AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 
                'CHFJPY', 'GBPAUD', 'GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPNZD', 'GBPUSD', 
                'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY']

    ff_calendar_path = Path("data/forex_calendar_01-2011_04-2021_GMT0.csv")
    calendar_df = pd.read_csv(ff_calendar_path)
    calendar_df = calendar_df[~calendar_df['Event'].astype(str).str.contains("Holiday")]
    base_ccys: np.ndarray = calendar_df['Currency'].unique()
    events: np.ndarray = np.sort(calendar_df['Event'].unique().astype(str))

    event: str = st.sidebar.selectbox("Event:", events, index=0)
    base_ccys: np.ndarray = np.sort(calendar_df[calendar_df['Event'] == event]['Currency'].unique())

    if 'All' in base_ccys:
        base_ccys: np.ndarray = np.sort(calendar_df['Currency'].unique())
    
    base_ccy = st.sidebar.selectbox("Base Currency:", base_ccys, index=0)

    pairs: List[str] = [i for i in ccy_pairs if base_ccy in i]
    pair: str = st.sidebar.selectbox("Pair:", pairs, index=0)


    df_calendar_filtered = get_df_calendar_filtered(calendar_df, event, base_ccy)

    df_calendar_filtered['Actual'] = df_calendar_filtered['Actual'].fillna('0')
    df_calendar_filtered['Forecast'] = df_calendar_filtered['Forecast'].fillna('0')
    df_calendar_filtered['Previous'] = df_calendar_filtered['Previous'].fillna('0')

    df_price_RT = get_df_price_RT(pair)
    result_df = combine_calendar_with_price_RT(df_calendar_filtered, 
                                df_price_RT,
                                event, 
                                pair, base_ccy)

    result_df = calc_volatility(result_df, base_ccy, event, pair)

    st.header(f"Volatility Histogram Charts")
    with st.expander("See charts"):
        fig_par, ax_par = plt.subplots()
        ax_par.set_title("Volatility At Event Release")
        ax_par.hist(result_df['Volatility_pips_intraday'].dropna(), bins=10)
        st.pyplot(fig_par)

        fig_bf, ax_bf = plt.subplots()
        ax_bf.set_title("Volatility Before Event Release")
        ax_bf.hist(result_df['Volatility_pips_bf'].dropna(), bins=10)
        st.pyplot(fig_bf)

        fig_af, ax_af = plt.subplots()
        ax_af.set_title("Volatility After Event Release")
        ax_af.hist(result_df['Volatility_pips_af'].dropna(), bins=10)
        st.pyplot(fig_af)

    st.header(f"Volatility Table")
    with st.expander("See table"):
        st.write(result_df[['Volatility_pips_bf', 'Volatility_pips_af', 'Volatility_pips_intraday']]
                    .dropna()
                    .assign(hack='')
                    .set_index('hack'))

