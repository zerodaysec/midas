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

    with open(fname, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, default=str))
        logger.info("Wrote %s", fname)

    logger.info("Sleeping for 15m %s", ticker)
    sleep(60 * 15)
    return data
