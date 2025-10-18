from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
class DataExtractor(ABC):
    @abstractmethod
    def fetch_one(self, ticker: str, start: str, end: str, interval: str="1d") -> pd.DataFrame: ...
    @abstractmethod
    def fetch_series(self, tickers: List[str], start: str, end: str, interval: str="1d") -> Dict[str, pd.DataFrame]: ...
