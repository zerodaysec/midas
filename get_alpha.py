"""get alpha.py"""
import os
import json
import time
import sys
from datetime import datetime
import requests


RATE_LIMIT_SLEEP = 15


def fetch_alpha_vantage_data(reqparams, apicall):
    """
    Fetches financial data for a given stock ticker from the Alpha Vantage API
    based on the chosen function.

    Parameters:
        api_key (str): The API key for the Alpha Vantage API.
        ticker (str): The stock ticker to query.
        apicall (str): The API function to use for data retrieval.

    Returns:
        dict: The JSON response from the API as a Python dictionary.
    """
    base_url = "https://www.alphavantage.co/query"

    if apicall == "TIME_SERIES_INTRADAY":
        params["interval"] = "5min"

    response = requests.get(base_url, params=reqparams, timeout=30)
    response.raise_for_status()

    return response.json()


def save_to_json(jsondata, ticker, apicall):
    """
    Saves the API data to a JSON file.

    Parameters:
        data (dict): The API data to save.
        ticker (str): The stock ticker to be used in the filename.
        apicall (str): The API function name to be used in the filename.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"../data/{date_str}-{ticker}-{apicall}.json"

    with open(filename, "w", encoding='utf-8') as f:
        json.dump(jsondata, f, indent=4)

    print(f"Data saved to {filename}")


if __name__ == "__main__":
    # Fetch the API key from environment variables
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if api_key is None:
        print(
            "Please set your Alpha Vantage API key in the ALPHA_VANTAGE_API_KEY"
             " environment variable."
        )
        sys.exit(1)

    # Define available endpoints
    available_functions = [
        "TIME_SERIES_INTRADAY",
        "TIME_SERIES_DAILY",
        "TIME_SERIES_WEEKLY",
        "TIME_SERIES_MONTHLY",
        "GLOBAL_QUOTE",
        "INCOME_STATEMENT",
        "BALANCE_SHEET",
        "CASH_FLOW",
        "EARNINGS",
        "CASH_FLOW",
    ]

    available_global = [
        "LISTING_STATUS",
        "EARNINGS_CALENDAR",
        "IPO_CALENDAR",
        "CURRENCY_EXCHANGE_RATE",
        "CURRENCY_EXCHANGE_RATE",
    ]
    commodities = [
        "WTI",
        "BRENT",
        "NATURAL_GAS",
        "COPPER",
        "ALUMINUM",
        "WHEAT",
        "CORN",
        "COTTON",
        "SUGAR",
        "COFFEE",
        "ALL_COMMODITIES",
    ]
    economic_indicators = [
        "REAL_GDP",
        "REAL_GDP_PER_CAPITA",
        "TREASURY_YIELD",
        "FEDERAL_FUNDS_RATE",
        "CPI",
        "INFLATION",
        "RETAIL_SALES",
        "DURABLES",
        "UNEMPLOYMENT",
        "NONFARM_PAYROLL",
    ]
    tech_indicators = [
        "SMA",
        "EMA",
        "WMA",
        "DEMA",
        "TEMA",
        "TRIMA",
        "KAMA",
        "MAMA",
        "T3",
        "MACDEXT",
        "STOCH",
        "STOCHF",
        "RSI",
        "STOCHRSI",
        "WILLR",
        "ADX",
        "AROON",
    ]
    # Get the ticker symbol from the user
    # TICKER = input("Enter the stock ticker: ").strip().upper()
    TICKER = "AAPL"

    # Loop through all available functions to fetch and save data
    for function in available_functions:
        try:
            params = {"function": function, "symbol": TICKER, "apikey": api_key}
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            save_to_json(data, TICKER, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(RATE_LIMIT_SLEEP)  # Adjust this based on your API rate limits
        except requests.RequestException as e:
            print(
                f"An error occurred while fetching data from function {function}: {e}"
            )

    # Loop through all available functions to fetch and save data
    for function in economic_indicators:
        try:
            TICKER = "EconomicIndicator"
            params = {"function": function, "apikey": api_key}
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            save_to_json(data, TICKER, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(RATE_LIMIT_SLEEP)  # Adjust this based on your API rate limits
        except requests.RequestException as e:
            print(
                f"An error occurred while fetching data from function {function}: {e}"
            )

    # Loop through all available functions to fetch and save data
    for function in commodities:
        try:
            TICKER = "COMOD"
            params = {"function": function, "apikey": api_key}
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            save_to_json(data, TICKER, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(RATE_LIMIT_SLEEP)  # Adjust this based on your API rate limits
        except requests.RequestException as e:
            print(
                f"An error occurred while fetching data from function {function}: {e}"
            )

    # Loop through all available functions to fetch and save data
    for function in tech_indicators:
        try:
            TICKER = "AAPL"
            params = {
                "function": function,
                "symbol": TICKER,
                "apikey": api_key,
                "interval": "daily"
            }
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(api_key, params, TICKER, function)
            # Save the data to a JSON file
            save_to_json(data, TICKER, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(RATE_LIMIT_SLEEP)  # Adjust this based on your API rate limits
        except requests.RequestException as e:
            print(f"An error occurred while fetching data from function {function}: {e}")
