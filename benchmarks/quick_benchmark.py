# -*- coding: utf-8 -*-
"""
Benchmark rapido para medir rendimiento de operaciones clave
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_extractor import DataExtractor, ExtractorConfig
from src.data_cleaner import DataCleaner
from src.simulation.portfolio import Portfolio


def measure_time(func, *args, **kwargs):
    """Mide el tiempo de ejecucion de una funcion"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def main():
    print("\n" + "="*70)
    print(" " * 15 + "BENCHMARK RAPIDO DE RENDIMIENTO")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Extraccion de datos
    print("[1/4] Extraccion de datos...")
    config = ExtractorConfig(source='yahoo', timeout=30)
    extractor = DataExtractor(config)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    data, t_extract = measure_time(
        extractor.get_market_data,
        tickers=symbols,
        start=start_date,
        end=end_date,
        interval='1d'
    )
    print(f"   -> Tiempo: {t_extract:.2f}s")
    print(f"   -> Simbolos extraidos: {len(data)}")
    print(f"   -> Filas por simbolo: {len(data[symbols[0]].data) if hasattr(data[symbols[0]], 'data') else 'N/A'}")
    
    # 2. Procesamiento de datos
    print("\n[2/4] Procesamiento de datos...")
    cleaner = DataCleaner()
    df_sample = data[symbols[0]].data if hasattr(data[symbols[0]], 'data') else data[symbols[0]]
    
    cleaned, t_clean = measure_time(cleaner.clean_dataframe, df_sample.copy())
    print(f"   -> Tiempo limpieza: {t_clean:.4f}s")
    print(f"   -> Columnas: {list(df_sample.columns)}")
    
    # 3. Creacion de portfolio
    print("\n[3/4] Creacion de portfolio...")
    # Crear DataFrame de precios de cierre
    # PriceSeries.data ya es un DataFrame con las columnas OHLCV
    prices_df = pd.DataFrame()
    for symbol in symbols:
        series_data = data[symbol].data if hasattr(data[symbol], 'data') else data[symbol]
        # Buscar columna de precio de cierre (puede ser 'Close', 'Adj Close', etc.)
        for col in ['Adj Close', 'Close', 'close', 'adj_close']:
            if col in series_data.columns:
                prices_df[symbol] = series_data[col]
                break
    
    weights = [1/len(symbols)] * len(symbols)
    portfolio, t_portfolio = measure_time(
        lambda: Portfolio(name="Benchmark Portfolio", symbols=symbols, weights=weights)
    )
    portfolio.set_prices(prices_df)
    
    print(f"   -> Tiempo creacion: {t_portfolio:.4f}s")
    print(f"   -> Activos: {len(symbols)}")
    print(f"   -> Retorno anual: {portfolio.portfolio_return() * 252:.2%}")
    print(f"   -> Volatilidad: {portfolio.portfolio_volatility():.2%}")
    
    # 4. Simulacion Monte Carlo
    print("\n[4/4] Simulacion Monte Carlo...")
    
    # Simulacion pequeña
    results_small, t_small = measure_time(
        portfolio.monte_carlo_simulation,
        n_simulations=1000,
        time_horizon=30,
        initial_value=10000.0,
        dynamic_volatility=False,
        random_seed=42
    )
    print(f"   -> 1,000 sims x 30 dias: {t_small:.2f}s")
    
    # Simulacion mediana
    results_medium, t_medium = measure_time(
        portfolio.monte_carlo_simulation,
        n_simulations=5000,
        time_horizon=90,
        initial_value=10000.0,
        dynamic_volatility=False,
        random_seed=42
    )
    print(f"   -> 5,000 sims x 90 dias: {t_medium:.2f}s")
    
    # Simulacion grande
    results_large, t_large = measure_time(
        portfolio.monte_carlo_simulation,
        n_simulations=10000,
        time_horizon=252,
        initial_value=10000.0,
        dynamic_volatility=False,
        random_seed=42
    )
    print(f"   -> 10,000 sims x 252 dias: {t_large:.2f}s")
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Extraccion de datos:     {t_extract:.2f}s")
    print(f"Procesamiento:           {t_clean:.4f}s")
    print(f"Portfolio:               {t_portfolio:.4f}s")
    print(f"Monte Carlo (total):     {t_small + t_medium + t_large:.2f}s")
    print(f"  - Pequeño (1K x 30):   {t_small:.2f}s")
    print(f"  - Mediano (5K x 90):   {t_medium:.2f}s")
    print(f"  - Grande (10K x 252):  {t_large:.2f}s")
    print("="*70)
    print(f"\nTIEMPO TOTAL: {t_extract + t_clean + t_portfolio + t_small + t_medium + t_large:.2f}s")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

