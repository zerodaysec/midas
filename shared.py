import sys
import json
import logging
from time import sleep
from datetime import datetime
import pandas as pd
import requests
import yfinance as yf
import os

logger = logging.getLogger(__name__)

TODAY = datetime.now().strftime("%Y-%m-%d")

DATA_DIR = os.getenv("DATA_DIR", "/data")
MIDAS_DATA_DIR = f"{DATA_DIR}/MIDAS"
yf.set_tz_cache_location(f"{DATA_DIR}/tz_cache_location")
RATE_LIMIT_ALPHA_SLEEP = 15
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if ALPHA_VANTAGE_API_KEY is None:
    logger.error(
        "Please set your Alpha Vantage API key in the ALPHA_VANTAGE_API_KEY"
        " environment variable."
    )
    sys.exit(1)

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.101 Safari/537.3"
}

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
OTHER_STOCKS = [
    "RXT",
]


def refresh_sp500():
    """Refresh the sp500 from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    # Set a User-Agent to mimic a web browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.101 Safari/537.3"
    }
    fname = f"{DATA_DIR}/500.csv"

    if os.path.exists(fname):
        logger.info("File exists %s", fname)
        return

    # Fetch the page content
    response = requests.get(url, headers=headers, timeout=30)

    # Use pandas to read the HTML tables
    tables = pd.read_html(response.text)
    sp500_table = tables[0]

    # Save the table to a CSV file

    sp500_table.to_csv(fname, index=False)
    logger.info("Wrote %s", fname)


def get_sp500_tickers():
    """get the sp500 tickers"""
    refresh_sp500()
    try:
        csv_data = pd.read_csv(f"{DATA_DIR}/500.csv", index_col="Symbol")
        return [symbol[0] for symbol in csv_data.iterrows()]
    except FileNotFoundError as e:
        logger.error("Error reading 500.csv, exiting %s", e)
        csv_data = None


def fetch_stock_data(ticker, force=False):
    """doc str."""
    # cleanup bad data
    if os.path.exists(f"{DATA_DIR}/MIDAS/{ticker}.json"):
        os.remove(f"{DATA_DIR}/MIDAS/{ticker}.json")

    fname = f"{DATA_DIR}/MIDAS/{TODAY}-{ticker}.json"
    if os.path.exists(fname):
        try:
            with open(fname, "r", encoding="utf-8") as src_file:
                data = json.load(src_file)
                logger.info("Found data for ticker... %s - %s", ticker, fname)
                if force:
                    pass
                return data
        except FileNotFoundError as err:
            logger.error(err)

    print(f"Getting updated stock data for {ticker}")
    data = {}
    try:
        stock_ticker = yf.Ticker(ticker)
    except Exception as err:
        logger.error("Error: %s", err)

    # get all stock info
    try:
        data["info"] = stock_ticker.info
    except Exception as err:
        logger.error("Error: %s", err)
        data["info"] = err

    try:
        # get historical market data
        mo1 = stock_ticker.history(period="1mo")
        data["1mo_hist"] = pd.DataFrame(mo1).to_json()
    except Exception as err:
        logger.error("Error history_metadata: %s", err)

    try:
        # show meta information about the history (requires history() to be called first)
        data["history_metadata"] = stock_ticker.history_metadata
    except Exception as err:
        logger.error("Error history_metadata: %s", err)

    try:
        # show actions (dividends, splits, capital gains)
        data["actions"] = pd.DataFrame(stock_ticker.actions).to_json()
        data["dividends"] = pd.DataFrame(stock_ticker.dividends).to_json()
        data["splits"] = pd.DataFrame(stock_ticker.splits).to_json()
    except Exception as err:
        logger.error("Error actions: %s", err)

    try:
        data["capital_gains"] = pd.DataFrame(
            stock_ticker.capital_gains
        ).to_json()  # only for mutual funds & etfs
    except Exception as err:
        logger.error("Error capital_gains: %s", err)

    try:
        # show share count
        get_shares_full = stock_ticker.get_shares_full(start="2022-01-01", end=None)
        df = pd.DataFrame(get_shares_full)
        df.reset_index(inplace=True)
        data["get_shares_full"] = pd.DataFrame(df).to_json()
    except Exception as err:
        logger.error("Error get_shares_full: %s", err)

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
        logger.error("Error income_stmt more: %s", err)

    try:
        # show holders
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
        logger.error("Error other: %s", err)

    try:
        # show recommendations
        data["recommendations"] = pd.DataFrame(stock_ticker.recommendations).to_json()
        data["recommendations_summary"] = pd.DataFrame(
            stock_ticker.recommendations_summary
        ).to_json()
        data["upgrades_downgrades"] = pd.DataFrame(
            stock_ticker.upgrades_downgrades
        ).to_json()
    except Exception as err:
        logger.error("Error: %s", err)
        data["recommendations"] = err

    # Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default.
    # Note: If more are needed use stock_ticker.get_earnings_dates(limit=XX) with increased limit argument.
    # data['earnings_dates'] = pd.DataFrame(stock_ticker.earnings_dates).to_json()

    # show ISIN code - *experimental*
    # ISIN = International Securities Identification Number
    try:
        data["isin"] = stock_ticker.isin
    except Exception as err:
        logger.error("Error recommendations: %s", err)
        data["isin"] = err

    try:
        # show options expirations
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
        logger.error("Error options: %s", err)
        data["options"] = err

    try:
        # show news
        data["news"] = stock_ticker.news
    except yf.Exception as err:
        logger.error("Error news: %s", err)
        data["news"] = err

    with open(f"{DATA_DIR}/MIDAS/latest-{ticker}.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(data, default=str))
        logger.info("Wrote %s", f"{DATA_DIR}/MIDAS/latest-{ticker}.json")

    with open(fname, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, default=str))
        logger.info("Wrote %s", fname)

    wait = 0.1
    logger.info("Sleeping for %sm %s", wait, ticker)
    sleep(60 * wait)
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
            sleep(RATE_LIMIT_ALPHA_SLEEP)
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s",
                function,
                e,
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
            sleep(RATE_LIMIT_ALPHA_SLEEP)  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s",
                function,
                e,
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
            sleep(RATE_LIMIT_ALPHA_SLEEP)  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s",
                function,
                e,
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
            sleep(RATE_LIMIT_ALPHA_SLEEP)  # Adjust this based on your API rate limits
            data[function] = data
        except requests.RequestException as e:
            logger.error(
                "An error occurred while fetching data from function %s: %s",
                function,
                e,
            )

    return data


def refresh_world_market_cap():
    """Refresh the ndxt from Wikipedia"""
    url = (
        "https://en.wikipedia.org/wiki/List_of_countries_by_stock_market_capitalization"
    )
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    tables = pd.read_html(response.text)
    tables[0].to_csv(f"{MIDAS_DATA_DIR}/world-market-cap-ranking.csv", index=False)
    tables[1].to_csv(f"{MIDAS_DATA_DIR}/world-market-cap.csv", index=False)


def refresh_ndxt():
    """Refresh the ndxt from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    response = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    tables = pd.read_html(response.text)
    tables[4].to_csv(f"{MIDAS_DATA_DIR}/ndxt.csv", index=False)
