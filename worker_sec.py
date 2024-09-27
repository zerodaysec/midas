"""SEC Data Downloader."""

import argparse
import concurrent.futures
import logging
import os
import sys
import time
from glob import glob
from random import shuffle

import pandas as pd
from sec_edgar_downloader import Downloader

from shared import OTHER_STOCKS, fetch_stock_data, get_sp500_tickers, refresh_sp500

WORKER_POLL_FREQ = (24) * (60 * 60)
DATA_DIR = os.getenv("DATA_DIR", "/data")

WORKERS = int(os.getenv("WORKERS", "1"))
WORKER_WAIT = 1  # force a 1s wait before we start

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Download filings to the current working directory
dl = Downloader("Personal", "fixme@example.com", DATA_DIR)

refresh_sp500()

# CSV_DATA = pd.read_csv(f"{DATA_DIR}/500.csv", index_col="Symbol")
# SP500_LIST = [symbol[0] for symbol in CSV_DATA.iterrows()]
SP500_LIST = get_sp500_tickers()

# Trimming the list as we are grabbing too much data right now.
# FORMS = ["13F-HR", "13F-NT", "10-K", "10-Q", "8-K", "3", "4", "5", "144"]
FORMS = ["13F-HR", "10-K", "10-Q"]


def get_available_forms():
    """Get available forms from the SEC website."""
    # forms = []
    # for form in dl.supported_forms:
    #     forms.append(form)
    return FORMS


# Get the latest supported filings, if available, for Apple
for f in get_available_forms():
    logger.debug("Available Form: %s", f)


# def get_sec_data(ticker):
#     """Get SEC data."""
#     logger.info("Downloading %s data...", ticker)
#     for filing_type in FORMS:
#         logger.info("Downloading %s for %s", filing_type, ticker)
#         dl.get(filing_type, ticker, download_details=True, include_amends=True, limit=1)
#         logger.info("Got data for %s for %s", filing_type, ticker)

#     time.sleep(WORKER_WAIT)


def get_sec_filing(ticker, form, limit=4):
    """Get SEC data."""
    base = f"{DATA_DIR}/sec-edgar-filings/{ticker}/{form}/*"
    files = glob(base)
    print(files)
    if len(files) >= limit:
        logger.info("Form(s) %s already present for %s", form, ticker)
        return "OK"
    else:
        logger.info("Downloading %s for %s", form, ticker)

    try:
        time.sleep(WORKER_WAIT)
        dl.get(form, ticker, download_details=True, include_amends=True, limit=limit)
        logger.info("Got data for %s for %s", form, ticker)
    except Exception as e:
        logger.error("Error downloading %s for %s - %s", form, ticker, e)


def generate_list(tickers):
    """Generate list of tickers to download."""
    data = []
    for ticker in tickers:
        for form in get_available_forms():
            data.append((form, ticker))

    return data


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--shuffle",
        help="Shuffle the list of tickers and SEC forms.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--debug",
        help="Setup Debug Mode (Verbose logging)",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    # if args.debug is:
    #     logger.info("Args: ", args)
    return args


if __name__ == "__main__":
    # TICKERS = ['AAPL','RXT', 'ADBE', 'AMZN']
    args = parse_args()
    TICKERS = OTHER_STOCKS + SP500_LIST
    batch = generate_list(TICKERS)
    logger.info(len(batch))
    batch_count = len(batch)
    if args.shuffle:
        logger.info("Shuffling the batch to randomize things....")
        shuffle(batch)
    if len(batch) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            future_to_url = {
                executor.submit(get_sec_filing, job[1], job[0], limit=4): job
                for job in batch
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    logger.debug(data)
                    batch_count -= 1
                    logger.warning(
                        "Jobs left in batch - %s/%s", batch_count, len(batch)
                    )

                except RuntimeWarning as exc:
                    logger.error("%r generated an exception: %s", url, exc)

    logger.info(
        "Worker jobs done - sleeping for %s (%s h)",
        WORKER_POLL_FREQ,
        ((WORKER_POLL_FREQ) / 60 / 60),
    )
    time.sleep(WORKER_POLL_FREQ)
