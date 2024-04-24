# midas

Stock Analysis App


## Goals

### Leading Indicators
1. [ ] **Moving Averages**: Short-term moving averages can predict future price movement.
2. [ ] **RSI (Relative Strength Index)**: Helps identify overbought or oversold conditions.
3. [ ] **MACD (Moving Average Convergence Divergence)**: Highlights changes in the strength, direction, momentum, and duration of a trend.
4. [ ] **Stochastic Oscillator**: Compares a stock's current price to its price range over a period of time.
5. [ ] **Fibonacci Retracement**: Uses horizontal lines to indicate where support and resistance levels should be.
6. [ ] **Bollinger Bands**: A volatility indicator that defines a range of price levels.
7. [ ] **Economic Indicators**: Like employment rates, GDP, etc., which could affect a sector or the entire market.
8. [ ] **Sentiment Analysis**: Gauging market sentiment from news or social media.

### Lagging Indicators
1. [ ] **Moving Averages**: Longer-term moving averages to confirm a market trend.
2. [ ] **Volume**: Trading volume following a price move.
3. [ ] **EPS (Earnings Per Share)**: Historical earnings growth can be indicative of future performance but is a lagging indicator.
4. **P/E Ratio**: Indicates how much investors are willing to pay for a company’s earnings.
5. **Dividend Yields**: Higher yields may signify a mature, established company.
6. **Balance Sheet Metrics**: Debt-to-equity ratio, working capital, etc.
7. **Market Capitalization**: Can indicate stability but lags real-time events.

Prioritizing additional data sources would depend on the level of granularity you aim for in your analytics. Here are some options, organized by category:

### Economic Indicators
1. **GDP Growth Rate**: As a measure of economic health, it could impact the stock market broadly.
2. **Employment Data**: Unemployment rates and non-farm payrolls can signal economic direction.
3. **Interest Rates**: Central bank rates can significantly impact stock market performance.

### Company-Specific Metrics
1. **Earnings Reports**: Quarterly or annual financial reports provide deep insights.
2. **News & Press Releases**: Real-time news can have immediate impact on stock prices.
3. **Insider Trading Records**: Buying and selling by company executives can be an indicator.

### Sector-Specific Metrics
1. **Commodity Prices**: Important for energy, mining, and agriculture sectors.
2. **Consumer Confidence Index**: Useful for companies in the consumer sector.
3. **Housing Data**: Relevant for real estate, construction, and home goods sectors.

### Market Sentiment
1. **Social Media Feeds**: Twitter sentiment analysis can be a powerful leading indicator.
2. **Analyst Ratings**: Upgrades, downgrades, and coverage initiations can move stocks.

### Alternative Data
1. **Web Traffic and App Usage**: Metrics like these can offer insights into consumer engagement.
2. **Supply Chain Data**: For companies that rely heavily on logistics and manufacturing.

Prioritize according to the kinds of stocks or sectors you're most interested in. For instance, if you're focusing on tech companies, keeping track of product launches, earnings call data, and specific news sources might be most relevant. If your aim is broader market analysis, economic indicators will be more suitable.

To integrate these, you can consider APIs like Quandl, Alpha Vantage for economic data, or even web scraping for news and sentiment analysis.


Understanding the layers of bonds or funds requires digging into their structures, components, and underlying assets. Here's how you can go about it:

### For Bonds
1. **Issuer Information**: Check who the issuer is (government, corporation, etc.) and their credit rating.
2. **Coupon Rate**: Understand the interest payment terms.
3. **Maturity Date**: Know when the bond will mature.
4. **Yield**: Look at both current yield and yield to maturity.
5. **Covenants**: Understand any restrictions or conditions.
6. **Market and Liquidity**: How easily can the bond be bought or sold?
7. **Callable or Convertible**: Know if the issuer or bondholder has special rights.

### For Funds (Mutual Funds, ETFs)
1. **Fund Objective**: What is the fund's investment strategy?
2. **Asset Allocation**: What kinds of assets does the fund invest in (stocks, bonds, other assets)?
3. **Top Holdings**: Identify the largest positions in the fund.
4. **Sector Allocation**: Which sectors does the fund focus on?
5. **Expense Ratio**: This is the annual fee as a percentage of assets.
6. **Performance History**: Look at both short-term and long-term performance.
7. **Manager Tenure and Strategy**: How long has the manager been in charge, and what is their strategy?

### Tools and Resources:
1. **Prospectus**: For both bonds and funds, the prospectus will be the most detailed source of information.
2. **Financial News Sites**: Websites like Bloomberg, Reuters, and Morningstar often provide analyses.
3. **Broker Platforms**: Many offer in-depth analytics tools.
4. **Regulatory Filings**: For bonds, look for documents like offering circulars. For funds, check out their quarterly and annual reports.

### Analytical Tools:
1. **Yield Curve Analysis**: For bonds, especially treasuries.
2. **Risk Metrics**: Such as Beta, Sharpe Ratio, etc., for funds.
3. **Comparative Analysis**: Compare the bond or fund with its peers.

### Sources:

1. **Fund Prospectus**: The most accurate and comprehensive source. Funds are legally obligated to disclose their holdings in the prospectus, which is usually updated annually or semi-annually.
2. **Quarterly and Annual Reports**: These SEC filings (like the 13F for U.S.-based funds) provide up-to-date information on fund holdings. They are usually available on the SEC’s EDGAR database or the fund’s website.
3. **Financial Websites**: Websites like Morningstar, Yahoo Finance, and Bloomberg often provide a snapshot of the top holdings of a fund, usually sourced from the latest available filings.
4. [ ] **Fund's Official Website**: Many funds list their top holdings on their websites, often in the investor relations or 'portfolio' section.
5. [ ] **Brokerage Platforms**: If you have access to a trading platform through a brokerage account, these often have tools that allow you to examine the composition of a fund.
6. [ ] **Industry Reports**: Some specialized financial news services provide deep dives into fund holdings but may require a subscription.
7. [ ] **Media Reports**: Financial news outlets occasionally publish articles that detail the largest holdings of high-profile funds.

### Best Practices:

1. [ ] **Multiple Sources**: Verify from multiple sources to ensure the data is current and accurate.
2. [ ] **Latest Data**: Make sure you are looking at the most recently available data, as funds can change their holdings frequently.
3. [ ] **Cross-Reference**: It can be beneficial to cross-reference the information you find with the fund's stated investment objectives and strategies to get a full picture.
4. [ ] **Peer Comparison**: To get a sense of how a fund's largest position compares with its peers, you can look up similar funds and their holdings.




## API Goals

1. [ ] **Yahoo Finance**: While not officially an API, it's possible to scrape fund data from Yahoo Finance, which usually includes top holdings.
2. [ ] **Morningstar API**: Provides extensive fund data, including portfolio holdings, although it generally requires a subscription.
3. [ ] **Alpha Vantage**: Offers information on mutual funds and ETFs, including sector weighting and top constituents. They offer both free and premium plans.
4. [ ] **E*TRADE API**: If you have an E*TRADE account, their API provides access to a wealth of fund data, including holdings.
5. [ ] **IEX Cloud**: Provides various types of financial data, including mutual fund holdings, through its API. It offers both free and premium plans.
6. [ ] **Quandl**: Offers a wide variety of financial and economic data, including fund holdings, but usually requires a subscription for the most valuable datasets.
7. [ ] **Intrinio**: Provides various types of financial market data, including information on ETFs and mutual funds, through their API.
8. [ ] **Zacks Investment Research**: Their API provides detailed mutual fund data including holdings, but typically requires a subscription.
9. [ ] **Interactive Brokers API**: Known for its powerful trading API, it also allows you to fetch quite a bit of fund data if you have an account with them.
