"""midas.py"""
import datetime
import pandas as pd
import pandas_datareader as pdr
import requests
import streamlit as st
import yfinance as yf
from secedgar import FilingType, filings
from yfinance import shared
import json


@st.cache_data
def fetch_thirteen_f(ticker):
    """doc str."""
    # FIXME: This is not working
    # response = requests.get(url, timeout=30)
    # if response.status_code == 200:
    # return response.content

    return None


def parse_thirteen_f(ticker):
    """doc str."""
    # FIXME: This is not working
    my_filings = filings(
        cik_lookup=ticker,
        filing_type=FilingType.FILING_10Q,
        user_agent="Jon P (your email)",
    )

    # TODO: secedgar library fails with JSON errors all the time...
    # my_filings.save(f'data/')
    return {}


# ------ Data Fetching Functions ------
@st.cache_data
def fetch_stock_data(ticker):
    """doc str."""
    print(f"Getting stock data for {ticker}")
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

    try:
        # get historical market data
        mo1 = stock_ticker.history(period="1mo")
        data["1mo_hist"] = pd.DataFrame(mo1).to_json()
    except Exception as err:
        print("Error: %s", err)

    try:
        # show meta information about the history (requires history() to be called first)
        data["history_metadata"] = stock_ticker.history_metadata
    except Exception as err:
        print("Error: %s", err)

    try:
        # show actions (dividends, splits, capital gains)
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

    try:
        # show share count
        get_shares_full = stock_ticker.get_shares_full(start="2022-01-01", end=None)
        df = pd.DataFrame(get_shares_full)
        df.reset_index(inplace=True)
        data["get_shares_full"] = pd.DataFrame(df).to_json()
    except Exception as err:
        print("Error: %s", err)

    # show financials:
    # - income statement

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
        print("Error: %s", err)

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
        print("Error: %s", err)

    try:
        # show news
        data["news"] = stock_ticker.news
    except Exception as err:
        print("Error: %s", err)

    # TODO: This is only used when debuggins Json not Serializable errors
    # with open(f'data/{symbol}.txt', 'w') as f:
    #     print(data, file=f)

    with open(f'data/{ticker}.json', 'w') as file:
        file.write(json.dumps(data))

    return data

    print(ticker)
    return {}  # Logic to fetch stock data


@st.cache_data
def fetch_economic_data():
    """doc str."""
    # FIXME: This is not working
    start = datetime.datetime(1960, 1, 1)
    end = datetime.datetime(2023, 6, 9)

    # Retrieve the data for each feature
    data_gdp = pdr.DataReader("GDP", "fred", start, end)["GDP"]
    data_gdp.index = pd.to_datetime(data_gdp.index)

    data_cpi = pdr.DataReader("CPIAUCSL", "fred", start, end)["CPIAUCSL"]
    data_cpi.index = pd.to_datetime(data_cpi.index)

    data_stock = pdr.DataReader("SPASTT01USM661N", "fred", start, end)[
        "SPASTT01USM661N"
    ]
    data_stock.index = pd.to_datetime(data_stock.index)

    data_pce = pdr.DataReader("PCE", "fred", start, end)["PCE"]
    data_pce.index = pd.to_datetime(data_pce.index)

    data_govs = pdr.DataReader("FGEXPND", "fred", start, end)["FGEXPND"]
    data_govs.index = pd.to_datetime(data_govs.index)

    data_binv = pdr.DataReader("W987RC1Q027SBEA", "fred", start, end)["W987RC1Q027SBEA"]
    data_binv.index = pd.to_datetime(data_binv.index)

    data_em = pdr.DataReader("PAYEMS", "fred", start, end)["PAYEMS"]
    data_em.index = pd.to_datetime(data_em.index)

    data_unem = pdr.DataReader("ICSA", "fred", start, end)["ICSA"]
    data_unem.index = pd.to_datetime(data_unem.index)

    # Combine the features into a single DataFrame
    data = pd.DataFrame(
        {
            "data_gdp": data_gdp,
            "data_cpi": data_cpi,
            "data_stock": data_stock,
            "data_pce": data_pce,
            "data_govs": data_govs,
            "data_binv": data_binv,
            "data_em": data_em,
            "data_unem": data_unem,
        }
    )

    # Remove rows with missing values
    data = data.dropna()
    # data.head()
    return data  # Logic to fetch economic data


# ------ Analysis Functions ------
# ---- Leading Indicators ----
def calculate_moving_average(data):
    """doc str."""
    # FIXME: This is not working
    return {}  # Logic for Moving Average


def calculate_macd(data):
    """doc str."""
    # FIXME: This is not working
    return {}  # Logic for MACD


def analyze_social_media_sentiment(data):
    """doc str."""
    # FIXME: This is not working
    return {}  # Logic for social media sentiment


# ---- Lagging Indicators ----
def calculate_rsi(data):
    """doc str."""
    # FIXME: This is not working
    return {}  # Logic for Relative Strength Index


def calculate_bollinger_bands(data):
    """doc str."""
    # FIXME: This is not working
    return {}  # Logic for Bollinger Bands


# ---- Economic Indicators ----
def analyze_gdp(data):
    """doc str."""
    # FIXME: This is not working
    return data  # Logic for GDP Analysis


def analyze_interest_rates(data):
    """doc str."""
    # FIXME: This is not working
    return data  # Logic for Interest Rates Analysis


def analyze_unemployment(data):
    """doc str."""
    # FIXME: This is not working
    return data  # Logic for Unemployment Analysis


# ------ Display Functions ------
def display_stock_data(data):
    """doc str."""
    # FIXME: This is not working
    st.subheader("Stock Data")


    for news in data['news']:
        st.subheader(news['title'])
        if 'thumbnail' in news:
            st.image(news['thumbnail']['resolutions'][0]['url'])
        st.write(news['link'])

    skip_keys = ['news']
    for key in data:
        if key in skip_keys:
            continue

        st.header(key)

        with st.expander(f'See more: {key}'):
            st.json(data[key])
    return {}  # Logic to display stock data


def display_economic_data(data):
    """doc str."""
    # FIXME: This is not working
    # print(data)
    st.subheader("Econ Data")
    st.dataframe(data.tail())


def display_thirteen_f(data):
    """doc str."""
    # FIXME: This is not working
    st.subheader("13f")
    print(data)


def display_analysis(data):
    """doc str."""
    # FIXME: This is not working
    st.subheader("Stock Analysis")


# ------ Main App Function ------
def main():
    """main."""
    # FIXME: This is not working
    st.title("Financial Analytics Dashboard")

    # User Inputs
    ticker = st.text_input("Enter stock ticker", "AAPL")
    INDICATORS = ["GDP", "Interest Rates", "Unemployment"]
    # economic_indicator = st.selectbox(
    #     "Choose an Economic Indicator", ["GDP", "Interest Rates", "Unemployment"]
    # )
    for ind in INDICATORS:
        st.subheader(ind)

    # Fetch Data
    stock_data = fetch_stock_data(ticker)
    _13f = parse_thirteen_f(ticker)
    economic_data = fetch_economic_data()
    sec_thirteen_f_data = fetch_thirteen_f(ticker)

    # Analyze Data
    moving_avg = calculate_moving_average(stock_data)
    macd = calculate_macd(stock_data)
    social_media_sentiment = analyze_social_media_sentiment(ticker)

    rsi = calculate_rsi(stock_data)
    bollinger_bands = calculate_bollinger_bands(stock_data)

    gdp_analysis = analyze_gdp(economic_data)
    interest_rates_analysis = analyze_interest_rates(economic_data)
    unemployment_analysis = analyze_unemployment(economic_data)

    # Display Data and Analysis
    display_stock_data(stock_data)
    display_economic_data(economic_data)
    display_thirteen_f(sec_thirteen_f_data)
    display_analysis(
        {
            "Moving Average": moving_avg,
            "MACD": macd,
            "Social Media Sentiment": social_media_sentiment,
            "RSI": rsi,
            "Bollinger Bands": bollinger_bands,
            "GDP": gdp_analysis,
            "Interest Rates": interest_rates_analysis,
            "Unemployment": unemployment_analysis,
        }
    )


if __name__ == "__main__":
    main()
