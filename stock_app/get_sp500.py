import pandas as pd
import requests

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# Set a User-Agent to mimic a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '\
                  'AppleWebKit/537.36 (KHTML, like Gecko) '\
                  'Chrome/91.0.4472.101 Safari/537.3'
}

# Fetch the page content
response = requests.get(url, headers=headers, timeout=30)

# Use pandas to read the HTML tables
tables = pd.read_html(response.text)
sp500_table = tables[0]

# Save the table to a CSV file
sp500_table.to_csv('sp500_list.csv', index=False)
