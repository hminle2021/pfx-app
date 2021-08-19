from pathlib import Path
import math

import streamlit as st
import numpy as np
import pandas as pd
from src.pages import var_calculation
from src.pages import event_volatility


PAGES = {
    "VaR Calculation": var_calculation,
    "Event Volatility": event_volatility
}

def main():

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    hide_streamlit_menu = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>

    """
    st.markdown(hide_streamlit_menu, unsafe_allow_html=True) 

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        page.render()

if __name__ == "__main__":
    main()