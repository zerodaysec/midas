import yfinance as yf
from yfinance import shared
import json
import pandas as pd
import time

def get_stock_data(symbol):
    print(f'Getting stock data for {symbol}')
    data ={}
    try:
        stock_ticker = yf.Ticker(symbol)
    except Exception as err:
        print('Error: %s', err)

    # get all stock info
    try:
        data['info'] = stock_ticker.info
    except Exception as err:
        print('Error: %s', err)

    try:
        # get historical market data
        mo1 = stock_ticker.history(period="1mo")
        data['1mo_hist'] = pd.DataFrame(mo1).to_json()
    except Exception as err:
        print('Error: %s', err)

    try:
        # show meta information about the history (requires history() to be called first)
        data['history_metadata'] = stock_ticker.history_metadata
    except Exception as err:
        print('Error: %s', err)

    try:
        # show actions (dividends, splits, capital gains)
        data['actions'] = pd.DataFrame(stock_ticker.actions).to_json()
        data['dividends'] = pd.DataFrame(stock_ticker.dividends).to_json()
        data['splits'] = pd.DataFrame(stock_ticker.splits).to_json()
    except Exception as err:
        print('Error: %s', err)
    try:
        data['capital_gains'] = pd.DataFrame(stock_ticker.capital_gains).to_json()  # only for mutual funds & etfs
    except Exception as err:
        print('Error: %s', err)

    try:
        # show share count
        get_shares_full = stock_ticker.get_shares_full(start="2022-01-01", end=None)
        df = pd.DataFrame(get_shares_full)
        df.reset_index(inplace=True)
        data['get_shares_full'] = pd.DataFrame(df).to_json()
    except Exception as err:
        print('Error: %s', err)

    # show financials:
    # - income statement
    
    try:
        income_stmt = stock_ticker.income_stmt
        data['income_stmt'] = pd.DataFrame(income_stmt).to_json()

        data['quarterly_income_stmt'] = pd.DataFrame(stock_ticker.quarterly_income_stmt).to_json() 
        # - balance sheet
        data['balance_sheet'] = pd.DataFrame(stock_ticker.balance_sheet).to_json() 
        data['quarterly_balance_sheet'] = pd.DataFrame(stock_ticker.quarterly_balance_sheet).to_json() 
        # - cash flow statement
        data['cashflow'] = pd.DataFrame(stock_ticker.cashflow).to_json() 
        data['quarterly_cashflow'] = pd.DataFrame(stock_ticker.quarterly_cashflow).to_json() 
        # see `Ticker.get_income_stmt()` for more options
    except Exception as err:
        print('Error: %s', err)

    try:
        # show holders
        data['major_holders'] = pd.DataFrame(stock_ticker.major_holders).to_json() 
        data['institutional_holders'] = pd.DataFrame(stock_ticker.institutional_holders).to_json() 
        data['mutualfund_holders'] = pd.DataFrame(stock_ticker.mutualfund_holders).to_json() 
        data['insider_transactions'] = pd.DataFrame(stock_ticker.insider_transactions).to_json() 
        data['insider_purchases'] = pd.DataFrame(stock_ticker.insider_purchases).to_json() 
        data['insider_roster_holders'] = pd.DataFrame(stock_ticker.insider_roster_holders).to_json() 
    except Exception as err:
        print('Error: %s', err)

    try:
        # show recommendations
        data['recommendations'] = pd.DataFrame(stock_ticker.recommendations).to_json() 
        data['recommendations_summary'] = pd.DataFrame(stock_ticker.recommendations_summary).to_json() 
        data['upgrades_downgrades'] = pd.DataFrame(stock_ticker.upgrades_downgrades).to_json() 
    except Exception as err:
        print('Error: %s', err)

    # Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default. 
    # Note: If more are needed use stock_ticker.get_earnings_dates(limit=XX) with increased limit argument.
    # data['earnings_dates'] = pd.DataFrame(stock_ticker.earnings_dates).to_json() 

    # show ISIN code - *experimental*
    # ISIN = International Securities Identification Number
    try:
        data['isin'] = stock_ticker.isin
    except Exception as err:
        print('Error: %s', err)

    try:
        # show options expirations
        data['options'] = stock_ticker.options

        # FIXME: Get the options data into the json dict so we can publish to mongo
        # data['options_data'] = {}
        # for opt in data['options']:
        #     print(f'Getting options for {opt}')
        #     # data['options_data'][opt] = stock_ticker.option_chain(opt)
        # #     data['options_data'][opt] = stock_ticker.option_chain(opt)
        #     data['options_data'][f'{opt}_calls'] = pd.DataFrame(stock_ticker.option_chain(opt)).to_json() 
        #     data['options_data'][f'{opt}_puts'] = pd.DataFrame(stock_ticker.option_chain(opt)).to_json() 
    except Exception as err:
        print('Error: %s', err)

    try:
        # show news
        data['news'] = stock_ticker.news
    except Exception as err:
        print('Error: %s', err)

    #TODO: This is only used when debuggins Json not Serializable errors
    # with open(f'data/{symbol}.txt', 'w') as f:
    #     print(data, file=f)

    with open(f'data/{symbol}.json', 'w') as file:
        file.write(json.dumps(data))

    # return data

# csv_data = pd.read_csv('https://gist.githubusercontent.com/yongghongg/4fa63c26369f844f22fed6121a24e04f/raw/8bda30f0b3ffbc82e563821ec131ebd62126c20d/SAP500_symbol_list.csv', index_col='Symbol')

csv_data = pd.read_csv('sp500_list.csv', index_col='Symbol')

for symbol in csv_data.iterrows():
    get_stock_data(symbol[0])
    time.sleep(5)



