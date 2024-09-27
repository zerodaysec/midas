"""SEC Data Downloader."""

import concurrent.futures
import logging
import sys
import time
import pandas as pd
from sec_edgar_downloader import Downloader
import os

from shared import OTHER_STOCKS, fetch_stock_data, refresh_sp500, get_sp500_tickers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

WORKERS = int(os.getenv("WORKERS", "1"))
WORKER_WAIT = 60
POLL_HOURS = 12
WORKER_POLL_FREQ = POLL_HOURS * (60 * 60)

refresh_sp500()

# NAS Location as we have TBs of data over time....
DATA_DIR = os.getenv("DATA_DIR", "/data")
SP500_LIST = get_sp500_tickers()


def generate_batch(tickers):
    """Generate list of tickers to download."""
    data = []
    for ticker in tickers:
        data.append(("form", ticker))

    return data


if __name__ == "__main__":
    TICKERS = OTHER_STOCKS + SP500_LIST
    batch = generate_batch(TICKERS)
    logger.info(len(batch))

    batch_count = len(TICKERS)
    if len(TICKERS) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            future_to_url = {
                executor.submit(
                    fetch_stock_data,
                    ticker,
                ): ticker
                for ticker in TICKERS
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    logger.debug(data)
                    batch_count -= 1
                    logger.info(
                        "Stock Grab Jobs left in batch - %s/%s",
                        batch_count,
                        len(TICKERS),
                    )

                except RuntimeWarning as exc:
                    logger.error("%r generated an exception: %s", url, exc)

    logger.info(
        "Worker jobs done - sleeping for %s (%s h)",
        WORKER_POLL_FREQ,
        ((WORKER_POLL_FREQ) / 60 / 60),
    )
    time.sleep(WORKER_POLL_FREQ)
