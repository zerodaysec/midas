"""api.py"""

from fastapi import FastAPI
from datetime import datetime
import pandas as pd

# import pandas_datareader as pdr
import json
import os

# import yfinance as yf

app = FastAPI()

DATA_DIR = os.getenv("DATA_DIR", "/data")


@app.get("/")
async def root():
    return {"message": "OK"}


@app.get("/ticker/{ticker}")
async def get_ticker(ticker):
    print(f"Getting stock data for {ticker}")

    # IF DATA FOUND - RETURN THIS
    try:
        with open(f"{DATA_DIR}/{ticker}.json", "w") as file:
            file.write(json.dumps(data))

        return data
    except:
        logger.info("No ticker found")
