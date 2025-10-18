import pandas as pd
import yfinance as yf
from .base_extractor import DataExtractor
class YahooExtractor(DataExtractor):
    source = "YahooFinance"
    def fetch_one(self, ticker: str, start: str, end: str, interval: str="1d") -> pd.DataFrame:
        df = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
        df.index = pd.to_datetime(df.index); df = df.rename(columns=str.lower); df["ticker"] = ticker; return df
    def fetch_series(self, tickers, start, end, interval="1d"):
        return {t: self.fetch_one(t, start, end, interval) for t in tickers}
