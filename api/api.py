"""api.py"""

from fastapi import FastAPI
from datetime import datetime
import pandas as pd
import logging
from glob import glob

logger = logging.getLogger(__name__)

# import pandas_datareader as pdr
import json
import os

# import yfinance as yf

TODAY = datetime.today().strftime("%Y-%m-%d")
app = FastAPI()

DATA_DIR = os.getenv("DATA_DIR", "/data")


@app.get("/")
async def root():
    return {"message": "OK"}


@app.get("/symbol/{symbol}")
async def get_symbol(symbol):
    print(f"Getting symbol data for {symbol}")
    # symbol = symbol.strip().replace("/", "").upper()
    try:
        fname = f"{DATA_DIR}/MIDAS/{TODAY}-{symbol}.json"
        print(f"Looking for {fname}")
        with open(fname, "r") as file:
            data = json.load(file)

        return data
    except Exception as err:
        logger.info("No symbol found")
        return {"message": f"No symbol found {err}"}


@app.get("/files")
async def get_files():
    files = glob(f"{DATA_DIR}/MIDAS/*")
    return json.dumps(files)
