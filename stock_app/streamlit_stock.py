"""This is my module."""
import csv
import os
import time
import glob
import json
from datetime import datetime
import pandas as pd
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

TODAY = datetime.now().strftime("%Y-%m-%d")
SLEEP_TIME = 0.25
SP_500_LIST = pd.read_csv("sp500_list.csv")
MORE_STOCK_LIST = pd.read_csv("more_stocks.csv")
BASE_DIR = '/Users/jon/data'

def init():
    pass


def fetch_stock_data(stock_ticker):
    """
    Fetch stock data using yfinance library.

    Parameters:
        stock_ticker (str): The stock ticker symbol.

    Returns:
        pd.DataFrame: A DataFrame containing the stock data.
    """
    stock_data = yf.download(stock_ticker)
    return stock_data


def fetch_stock_info(ticker_symbol):
    """doc str."""
    stock = yf.Ticker(ticker_symbol)
    print(f"Pulling stock info for {ticker_symbol}")
    return stock.info


def save_stock_data_to_csv(stock_data, ticker_symbol):
    """
    Save stock data to a CSV file.

    Parameters:
        data (pd.DataFrame): The stock data.
        ticker (str): The stock ticker symbol.
    """
    stock_data.to_csv(f"{BASE_DIR}/{ticker_symbol}.csv")
    print(f"Saved csv data {ticker_symbol}")


def fetch_yahoo_finance_info(ticker_symbol):
    """doc str."""
    stock = yf.Ticker(ticker_symbol)
    stock_info = stock.info
    print(stock_info)
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
    with open("more_stocks.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)

        if not file_exists:
            writer.writeheader()

        writer.writerow(additional_info)


def save_stock_info_to_json(stock_data, ticker_symbol):
    """Save stock metadata to a JSON file."""
    filename = f"{BASE_DIR}/{TODAY}-{ticker_symbol}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(stock_data, file)
    print(f"Saving stock info json for {ticker_symbol}")


def read_stock_data_from_csv(ticker_symbol):
    """
    Read stock data from a CSV file.

    Parameters:
        ticker (str): The stock ticker symbol.

    Returns:
        pd.DataFrame: A DataFrame containing the stock data.
    """
    return pd.read_csv(f"{BASE_DIR}/{ticker_symbol}.csv", index_col="Date", parse_dates=True)


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
    with open("more_stocks.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)

        if not file_exists:
            writer.writeheader()

        writer.writerow(additional_info)


###############################################################################

# Streamlit UI
st.title("Stock Data Analyzer")

ALL_TICKER = list(SP_500_LIST["Symbol"]) + list(MORE_STOCK_LIST["Symbol"])

for symbol in ALL_TICKER:
    # Check if data exists locally
    if not os.path.exists(f"{BASE_DIR}/{TODAY}-{symbol}.json"):
        info = fetch_stock_info(symbol)
        save_stock_info_to_json(info, symbol)
        time.sleep(SLEEP_TIME)

    if os.path.exists(f"{BASE_DIR}/{symbol}.csv"):
        # print(f"Stock data for {symbol} exists locally")
        pass
    else:
        tmp_data = fetch_stock_data(symbol)
        save_stock_data_to_csv(tmp_data, symbol)
        print(f"Cached data for {symbol}")
        time.sleep(SLEEP_TIME)


def list_local_csv_files():
    """
    List all local CSV files in the data directory.
    """
    return [os.path.basename(x)[:-4] for x in glob.glob("{BASE_DIR}/*.csv")]


# List local CSV files and display dropdown
local_files = list_local_csv_files()
sorted_local_files = sorted(local_files)  # Sort the files alphabetically
selected_tickers = st.multiselect(
    "Select a local stock ticker:", [""] + sorted_local_files
)

# User input for a new stock ticker
new_ticker = st.text_input("Or enter new stock tickers (comma separated):", "")
if len(new_ticker.split(",")) > 0:
    new_tickers = [ticker.strip().upper() for ticker in new_ticker.split(",")]
else:
    new_ticker = []

# Combine selected and new tickers
all_tickers = selected_tickers + new_tickers

# Initialize data dictionary to hold data DataFrames for each ticker
data_dict = {}

for ticker in all_tickers:
    if ticker:  # Check if the ticker is not an empty string
        # Check if data exists locally
        if os.path.exists(f"{BASE_DIR}/{ticker}.csv"):
            st.write(f"Stock data for {ticker} exists locally.")
            data = read_stock_data_from_csv(ticker)
        else:
            st.write(f"Stock data for {ticker} does not exist locally.")
            if st.button(f"Download Data for {ticker}"):
                data = fetch_stock_data(ticker)
                save_stock_data_to_csv(data, ticker)
                st.write(f"Downloaded and saved data for {ticker}")

        # Store the data in the data dictionary
        if "data" in locals():
            data_dict[ticker] = data

# If data is available, allow user to select columns and date range
if data_dict:
    sample_data = next(iter(data_dict.values()))
    available_columns = sample_data.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display (excluding Volume)",
        [col for col in available_columns if col != "Volume"],
        default=[col for col in available_columns if col != "Volume"],
    )

    min_date = min(data.index.min().date() for data in data_dict.values())
    max_date = max(data.index.max().date() for data in data_dict.values())
    selected_date_range = st.date_input("Select a date range", [min_date, max_date])

    # Initialize a plot for stock data and another for volume
    fig, ax = plt.subplots()
    fig_volume, ax_volume = plt.subplots()

    # Loop through each ticker and plot the data
    for ticker, data in data_dict.items():
        filtered_data = data[selected_date_range[0] : selected_date_range[1]]

        for column in selected_columns:
            ax.plot(
                filtered_data.index, filtered_data[column], label=f"{ticker} {column}"
            )

        if "Volume" in data.columns:
            ax_volume.plot(
                filtered_data.index, filtered_data["Volume"], label=f"{ticker} Volume"
            )

    ax.legend()
    ax.set_title("Stock Data Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")

    ax_volume.legend()
    ax_volume.set_title("Stock Volume Over Time")
    ax_volume.set_xlabel("Date")
    ax_volume.set_ylabel("Volume")

    st.pyplot(fig)
    st.pyplot(fig_volume)

    # Fetch and display metadata for each selected ticker
    for ticker, data in data_dict.items():
        info = fetch_stock_info(ticker)
        save_stock_info_to_json(info, ticker)
        for k, v in info.items():
            if k == "companyOfficers":
                for officer in info[k]:
                    st.write(
                        officer["name"], officer.get("age"), officer.get("totalPay")
                    )
            else:
                st.write(k, "-> ", str(v))
