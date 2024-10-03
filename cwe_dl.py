import requests
import pandas as pd
from io import StringIO
import re
from bs4 import BeautifulSoup


BASE = "https://cwe.mitre.org"
URL = f"{BASE}/data/downloads.html"


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.101 Safari/537.3"
    }
    # fname = f"{DATA_DIR}/500.csv"

    # if os.path.exists(fname):
    #     logger.info("File exists %s", fname)
    #     return

    # Fetch the page content
    response = requests.get(URL, headers=headers, timeout=30)

    # Use pandas to read the HTML tables
    tables = pd.read_html(response.text)
    table1 = tables[0]
    table2 = tables[1]
    table3 = tables[2]
    table4 = tables[3]
    print(table1, table2, table3, table4)
    # soup = BeautifulSoup(response.text)

    # for link in soup.findAll('a', attrs={'href': re.compile('.csv.zip')}):
    #     fname = link.get("href").split('/')[-1]
    #     link_abs = f'{BASE}{link.get("href")}'
    #     print(link_abs)
    #     with open(fname, 'wb') as f:
    #         f.write(requests.get(link_abs).content)


if __name__ == "__main__":
    main()
