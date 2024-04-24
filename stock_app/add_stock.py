import csv
import os
# import time
import pandas as pd
import streamlit as st
import yfinance as yf
# import glob
# import matplotlib.pyplot as plt
# import json
from datetime import datetime

st.set_page_config('Stock Data', page_icon=':bar_chart:')

TODAY = datetime.now().strftime("%Y-%m-%d")

def fetch_yahoo_finance_info(ticker_symbol):
    """doc str."""
    stock = yf.Ticker(ticker_symbol)
    stock_info = stock.info
    # print(stock_info)
    return {
        "Symbol": ticker_symbol,
        "Security": stock_info.get("longName", "N/A"),
        "GICS Sector": stock_info.get("sector", "N/A"),
        "GICS Sub-Industry": stock_info.get("industry", "N/A"),
        "Headquarters Location": stock_info.get("city", "N/A"),
        "Date added": "N/A",  # Not available from Yahoo Finance
        "CIK": "N/A",  # Not available from Yahoo Finance
        "Founded": stock_info.get("founded", "N/A"),
    }


def add_additional_stock(ticker_symbol):
    """Fetch additional information for a ticker and append it to more_stocks.csv."""
    # Fetch the additional information
    additional_info = fetch_yahoo_finance_info(ticker_symbol)

    # Define the header
    header = [
        "Symbol",
        "Security",
        "GICS Sector",
        "GICS Sub-Industry",
        "Headquarters Location",
        "Date added",
        "CIK",
        "Founded",
    ]

    # Check if the file exists to decide whether to write the header
    file_exists = os.path.isfile("more_stocks.csv")

    # Append the information to the CSV file
    with open("more_stocks.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)

        if not file_exists:
            writer.writeheader()

        writer.writerow(additional_info)


def save_stock_info_to_json(info, ticker_symbol):
    """Save stock metadata to a JSON file."""
    filename = f"data/{TODAY}-{ticker_symbol}.json"
    with open(filename, "w") as f:
        json.dump(info, f)
    print(f"Saving stock info json for {ticker_symbol}")


def read_stock_data_from_csv(ticker_symbol):
    """
    Read stock data from a CSV file.

    Parameters:
        ticker (str): The stock ticker symbol.

    Returns:
        pd.DataFrame: A DataFrame containing the stock data.
    """
    return pd.read_csv(f"data/{ticker_symbol}.csv", index_col="Date", parse_dates=True)


def append_to_csv(ticker_symbol):
    """Fetch additional information for a ticker and append it to more_stocks.csv."""
    # Fetch the additional information
    additional_info = fetch_yahoo_finance_info(ticker_symbol)

    # Define the header
    header = [
        "Symbol",
        "Security",
        "GICS Sector",
        "GICS Sub-Industry",
        "Headquarters Location",
        "Date added",
        "CIK",
        "Founded",
    ]

    # Check if the file exists to decide whether to write the header
    file_exists = os.path.isfile("more_stocks.csv")

    # Append the information to the CSV file
    with open("more_stocks.csv", "a", newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)

        if not file_exists:
            writer.writeheader()

        writer.writerow(additional_info)


###############################################################################


# add_additional_stock("VGT")

# Streamlit UI
st.title("Stock Data Addererere")


# User input for a new stock ticker
new_ticker = st.text_input("Or enter new stock tickers (comma separated):", "")
# print(new_ticker)
if new_ticker != '':
    new_tickers = [ticker.strip().upper() for ticker in new_ticker.split(",")]
    for symbol in new_tickers:
        add_additional_stock(symbol)

if st.button('Delete :heavy_minus_sign:'):
    print('Clicked...')

if st.button('Delete2 :heavy_minus_sign:'):
    print('Clicked...')
