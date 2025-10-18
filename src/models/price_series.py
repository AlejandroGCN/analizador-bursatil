import pandas as pd
class PriceSeries:
    def __init__(self, ticker: str, data: pd.DataFrame, source: str="unknown"):
        self.ticker=ticker; self.data=data; self.source=source
        self.returns = data["close"].pct_change().dropna() if "close" in data.columns else pd.Series(dtype=float)
        self.mean_return = float(self.returns.mean()) if not self.returns.empty else 0.0
        self.volatility = float(self.returns.std()) if not self.returns.empty else 0.0
    def summary(self)->dict:
        return {"ticker":self.ticker,"source":self.source,"n_points":int(len(self.data)),
                "mean_return":self.mean_return,"volatility":self.volatility}
