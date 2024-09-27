"""midas.py"""

import json
import logging
import os
import sys
import time
from datetime import datetime
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from sec_edgar_downloader import Downloader

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)

# Static variables
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.101 Safari/537.3"
}
DATA_DIR = os.getenv("DATA_DIR")
# Check if the DATA_DIR is set and exists
if DATA_DIR is None:
    logger.error("DATA_DIR not set, exiting")
    sys.exit(1)

MIDAS_DATA_DIR = f"{DATA_DIR}/midas"
SEC_DATA_DIR = f"{DATA_DIR}/SEC"
OTHER_STOCKS = [
    "RXT",
    "FXAIX",
    "VGT",
    "VIG",
    "VOO",
    "VTI",
    "VFAIX",
    "VEA",
    "GLD",
    "VNQ",
    "MUB",
    "ADT",
]
RATE_LIMIT_ALPHA_SLEEP = 15
TODAY = datetime.now().strftime("%Y-%m-%d")

SEC_DL = Downloader("Personal", "fixme@example.com", SEC_DATA_DIR)

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if ALPHA_VANTAGE_API_KEY is None:
    logger.error(
        "Please set your Alpha Vantage API key in the ALPHA_VANTAGE_API_KEY"
        " environment variable."
    )
    sys.exit(1)


@st.cache_data()
def refresh_sp500():
    """Refresh the sp500 from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    tables = pd.read_html(response.text)
    tables[0].to_csv(f"{MIDAS_DATA_DIR}/500.csv", index=False)

refresh_sp500()

CSV_DATA = pd.read_csv(f"{MIDAS_DATA_DIR}/500.csv", index_col="Symbol")
SP500_LIST = [symbol[0] for symbol in CSV_DATA.iterrows()]
SP500_LIST.sort()




@st.cache_data()
def refresh_ndxt():
    """Refresh the ndxt from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    tables = pd.read_html(response.text)
    tables[4].to_csv(f"{MIDAS_DATA_DIR}/ndxt.csv", index=False)


@st.cache_data()
def refresh_world_market_cap():
    """Refresh the ndxt from Wikipedia"""
    url = (
        "https://en.wikipedia.org/wiki/List_of_countries_by_stock_market_capitalization"
    )
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    tables = pd.read_html(response.text)
    tables[0].to_csv(f"{MIDAS_DATA_DIR}/world-market-cap-ranking.csv", index=False)
    tables[1].to_csv(f"{MIDAS_DATA_DIR}/world-market-cap.csv", index=False)


@st.cache_data
def fetch_thirteen_f(ticker):
    """doc str."""
    data = SEC_DL.get("13F-HR", ticker, download_details=True, include_amends=True)
    print(data)
    return data


@st.cache_data
def fetch_stock_data(ticker, force=False):
    """doc str."""
    try:
        with open(
            f"{MIDAS_DATA_DIR}/{TODAY}-{ticker}.json", "r", encoding="utf-8"
        ) as src_file:
            data = json.load(src_file)
            logger.info("Found data for ticker... %s", ticker)
            if force:
                pass

            return data
    except FileNotFoundError as err:
        print(err)

    print(f"Getting updated stock data for {ticker}")
    data = {}
    try:
        stock_ticker = yf.Ticker(ticker)
    except Exception as err:
        print("Error: %s", err)

    # get all stock info
    try:
        data["info"] = stock_ticker.info
    except Exception as err:
        print("Error: %s", err)

    # get historical market data
    try:
        mo1 = stock_ticker.history(period="1mo")
        data["1mo_hist"] = pd.DataFrame(mo1).to_json()
    except Exception as err:
        print("Error: %s", err)

    # show meta information about the history (requires history() to be called first)
    try:
        data["history_metadata"] = stock_ticker.history_metadata
    except Exception as err:
        print("Error: %s", err)

    # show actions (dividends, splits, capital gains)
    try:
        data["actions"] = pd.DataFrame(stock_ticker.actions).to_json()
        data["dividends"] = pd.DataFrame(stock_ticker.dividends).to_json()
        data["splits"] = pd.DataFrame(stock_ticker.splits).to_json()
    except Exception as err:
        print("Error: %s", err)
    try:
        data["capital_gains"] = pd.DataFrame(
            stock_ticker.capital_gains
        ).to_json()  # only for mutual funds & etfs
    except Exception as err:
        print("Error: %s", err)

    # show share count
    try:
        get_shares_full = stock_ticker.get_shares_full(start="2022-01-01", end=None)
        df = pd.DataFrame(get_shares_full)
        df.reset_index(inplace=True)
        data["get_shares_full"] = pd.DataFrame(df).to_json()
    except Exception as err:
        print("Error: %s", err)

    try:
        income_stmt = stock_ticker.income_stmt
        data["income_stmt"] = pd.DataFrame(income_stmt).to_json()

        data["quarterly_income_stmt"] = pd.DataFrame(
            stock_ticker.quarterly_income_stmt
        ).to_json()
        # - balance sheet
        data["balance_sheet"] = pd.DataFrame(stock_ticker.balance_sheet).to_json()
        data["quarterly_balance_sheet"] = pd.DataFrame(
            stock_ticker.quarterly_balance_sheet
        ).to_json()
        # - cash flow statement
        data["cashflow"] = pd.DataFrame(stock_ticker.cashflow).to_json()
        data["quarterly_cashflow"] = pd.DataFrame(
            stock_ticker.quarterly_cashflow
        ).to_json()
        # see `Ticker.get_income_stmt()` for more options
    except Exception as err:
        print("Error: %s", err)

    # show holders
    try:
        data["major_holders"] = pd.DataFrame(stock_ticker.major_holders).to_json()
        data["institutional_holders"] = pd.DataFrame(
            stock_ticker.institutional_holders
        ).to_json()
        data["mutualfund_holders"] = pd.DataFrame(
            stock_ticker.mutualfund_holders
        ).to_json()
        data["insider_transactions"] = pd.DataFrame(
            stock_ticker.insider_transactions
        ).to_json()
        data["insider_purchases"] = pd.DataFrame(
            stock_ticker.insider_purchases
        ).to_json()
        data["insider_roster_holders"] = pd.DataFrame(
            stock_ticker.insider_roster_holders
        ).to_json()
    except Exception as err:
        print("Error: %s", err)

    # show recommendations
    try:
        data["recommendations"] = pd.DataFrame(stock_ticker.recommendations).to_json()
        data["recommendations_summary"] = pd.DataFrame(
            stock_ticker.recommendations_summary
        ).to_json()
        data["upgrades_downgrades"] = pd.DataFrame(
            stock_ticker.upgrades_downgrades
        ).to_json()
    except Exception as err:
        print("Error: %s", err)

    # Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default.
    # Note: If more are needed use stock_ticker.get_earnings_dates(limit=XX) with increased limit argument.
    # data['earnings_dates'] = pd.DataFrame(stock_ticker.earnings_dates).to_json()

    # show ISIN code - *experimental*
    # ISIN = International Securities Identification Number
    try:
        data["isin"] = stock_ticker.isin
    except Exception as err:
        print("Error: %s", err)

    # show options expirations
    try:
        data["options"] = stock_ticker.options

        # FIXME: Get the options data into the json dict so we can publish to mongo
        # data['options_data'] = {}
        # for opt in data['options']:
        #     print(f'Getting options for {opt}')
        #     # data['options_data'][opt] = stock_ticker.option_chain(opt)
        # #     data['options_data'][opt] = stock_ticker.option_chain(opt)
        #     data['options_data'][f'{opt}_calls'] = pd.DataFrame(stock_ticker.option_chain(opt)).to_json()
        #     data['options_data'][f'{opt}_puts'] = pd.DataFrame(stock_ticker.option_chain(opt)).to_json()
    except Exception as err:
        print("Error: %s", err)

    # show news
    try:
        data["news"] = stock_ticker.news
    except Exception as err:
        print("Error: %s", err)

    # TODO: This is only used when debuggins Json not Serializable errors
    # with open(f'{MIDAS_DATA_DIR}/{symbol}.txt', 'w') as f:
    #     print(data, file=f)

    with open(f"{MIDAS_DATA_DIR}/{TODAY}-{ticker}.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(data))

    return data


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
        reqparams["interval"] = "5min"

    response = requests.get(base_url, params=reqparams, timeout=30)
    response.raise_for_status()

    return response.json()


def alpha_save_to_json(jsondata, ticker, apicall):
    """
    Saves the API data to a JSON file.

    Parameters:
        data (dict): The API data to save.
        ticker (str): The stock ticker to be used in the filename.
        apicall (str): The API function name to be used in the filename.
    """
    filename = f"{MIDAS_DATA_DIR}/alphavantage/{TODAY}-{ticker}-{apicall}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jsondata, f, indent=4)

    print(f"Data saved to {filename}")


ALPHA_OPTS = {
    "available_functions": [
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
    ],
    "available_global": [
        "LISTING_STATUS",
        "EARNINGS_CALENDAR",
        "IPO_CALENDAR",
        "CURRENCY_EXCHANGE_RATE",
        "CURRENCY_EXCHANGE_RATE",
    ],
    "commodities": [
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
    ],
    "economic_indicators": [
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
    ],
    "tech_indicators": [
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
    ],
}


def get_alpha_vantage_data():
    data = {}
    # Loop through all available functions to fetch and save data
    for function in ALPHA_OPTS["economic_indicators"]:
        try:
            ticker = "EconomicIndicator"
            params = {"function": function, "apikey": ALPHA_VANTAGE_API_KEY}
            data = fetch_alpha_vantage_data(params, function)
            alpha_save_to_json(data, ticker, function)
            time.sleep(
                RATE_LIMIT_ALPHA_SLEEP
            )
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s", function, e
            )

    # Loop through all available functions to fetch and save data
    for function in ALPHA_OPTS["commodities"]:
        try:
            ticker = "COMOD"
            params = {"function": function, "apikey": ALPHA_VANTAGE_API_KEY}
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            alpha_save_to_json(data, ticker, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(
                RATE_LIMIT_ALPHA_SLEEP
            )  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s", function, e
            )

    return data


def get_alpha_vantage_ticker_data(ticker):

    data = {}

    # Loop through all available functions to fetch and save data
    for function in ALPHA_OPTS["available_functions"]:
        try:
            params = {
                "function": function,
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
            }
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            alpha_save_to_json(data, ticker, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(
                RATE_LIMIT_ALPHA_SLEEP
            )  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s", function, e
            )

    # Loop through all available functions to fetch and save data
    for function in ALPHA_OPTS["tech_indicators"]:
        try:
            params = {
                "function": function,
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "interval": "daily",
            }
            # Fetch the data from the Alpha Vantage API
            data = fetch_alpha_vantage_data(params, function)
            # Save the data to a JSON file
            alpha_save_to_json(data, ticker, function)
            # To avoid hitting rate limits, wait before the next API call
            time.sleep(
                RATE_LIMIT_ALPHA_SLEEP
            )  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s",
                function,
                e,
            )

    return data


# ------ Main App Function ------
def main():
    """main."""
    st.title("Financial Data Downloader Dashboard")

    if st.button("Refresh All Data"):
        # for stk in OTHER_STOCKS:
        #     fetch_stock_data(stk)

        # for stk in SP500_LIST:
        #     fetch_stock_data(stk)

        st.write("Refreshing SP500.csv")
        refresh_sp500()
        refresh_ndxt()
        st.write("Refreshing ndxt.csv")
        # st.write('Refreshing get_alpha_vantage_data()')
        # get_alpha_vantage_data()

    # User Inputs
    ticker = st.text_input("Enter stock to refresh (ex. AAPL)")
    ticker_picker = st.selectbox("S&P500:", OTHER_STOCKS + SP500_LIST)

    if ticker != "":
        ticker = ticker.upper()
    else:
        ticker = ticker_picker


if __name__ == "__main__":
    refresh_world_market_cap()
    refresh_ndxt()
    refresh_sp500()
    main()
    # alpha_data = get_alpha_vantage_data()
    # logger.debug(alpha_data)
