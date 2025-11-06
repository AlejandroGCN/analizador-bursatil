# -*- coding: utf-8 -*-
"""
Script de Benchmarking para Analizador Bursátil
Mide el rendimiento de las operaciones principales del sistema.
"""

import time
import tracemalloc
from datetime import datetime, timedelta
from typing import Callable, Any
import pandas as pd
import numpy as np

from src.data_extractor import DataExtractor, ExtractorConfig
from src.data_cleaner import DataCleaner
from src.simulation.portfolio import Portfolio
from src.simulation.monte_carlo import MonteCarloParams


class PerformanceBenchmark:
    """Clase para medir el rendimiento del sistema."""
    
    def __init__(self):
        self.results = []
    
    def measure_time_and_memory(self, func: Callable, name: str, *args, **kwargs) -> Any:
        """
        Mide tiempo de ejecución y uso de memoria de una función.
        
        Args:
            func: Función a medir
            name: Nombre descriptivo de la operación
            *args, **kwargs: Argumentos para la función
        
        Returns:
            Resultado de la función
        """
        print(f"\n{'='*60}")
        print(f"[*] Midiendo: {name}")
        print(f"{'='*60}")
        
        # Iniciar medición de memoria
        tracemalloc.start()
        
        # Medir tiempo
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error_msg = None
        except Exception as e:
            result = None
            success = False
            error_msg = str(e)
            print(f"[ERROR] {error_msg}")
        
        end_time = time.perf_counter()
        
        # Obtener uso de memoria
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calcular métricas
        elapsed_time = end_time - start_time
        memory_mb = peak / 1024 / 1024
        
        # Guardar resultados
        self.results.append({
            'Operacion': name,
            'Tiempo (s)': round(elapsed_time, 4),
            'Memoria (MB)': round(memory_mb, 2),
            'Exito': '[OK]' if success else '[FAIL]',
            'Error': error_msg
        })
        
        # Mostrar resultados
        print(f"Tiempo: {elapsed_time:.4f} segundos")
        print(f"Memoria pico: {memory_mb:.2f} MB")
        print(f"{'[COMPLETADO]' if success else '[FALLO]'}")
        
        return result
    
    def print_summary(self):
        """Imprime un resumen de todos los benchmarks."""
        print(f"\n\n{'='*80}")
        print("RESUMEN DE RENDIMIENTO")
        print(f"{'='*80}\n")
        
        df = pd.DataFrame(self.results)
        print(df.to_string(index=False))
        
        # Estadisticas
        successful = df[df['Exito'] == '[OK]']
        if not successful.empty:
            print(f"\n{'='*80}")
            print("ESTADISTICAS")
            print(f"{'='*80}")
            print(f"Operaciones exitosas: {len(successful)} / {len(df)}")
            print(f"Tiempo total: {successful['Tiempo (s)'].sum():.4f} segundos")
            print(f"Memoria total (pico): {successful['Memoria (MB)'].sum():.2f} MB")
            print(f"Operacion mas rapida: {successful.loc[successful['Tiempo (s)'].idxmin(), 'Operacion']}")
            print(f"Operacion mas lenta: {successful.loc[successful['Tiempo (s)'].idxmax(), 'Operacion']}")


def benchmark_data_extraction():
    """Benchmark de extracción de datos desde diferentes fuentes."""
    benchmark = PerformanceBenchmark()
    
    # Definir parámetros de prueba
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 año de datos
    symbols_small = ['AAPL', 'MSFT', 'GOOGL']
    symbols_medium = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    
    print("\n" + "=" * 60)
    print(" " * 10 + "BENCHMARK: EXTRACCION DE DATOS")
    print("=" * 60)
    
    # 1. Yahoo Finance - 3 símbolos
    def extract_yahoo_small():
        config = ExtractorConfig(source='yahoo', timeout=30)
        extractor = DataExtractor(config)
        return extractor.get_market_data(
            tickers=symbols_small,
            start=start_date,
            end=end_date,
            interval='1d'
        )
    
    data_small = benchmark.measure_time_and_memory(
        extract_yahoo_small,
        "Yahoo Finance - 3 símbolos (1 año, 1d)"
    )
    
    # 2. Yahoo Finance - 8 símbolos
    def extract_yahoo_medium():
        config = ExtractorConfig(source='yahoo', timeout=30)
        extractor = DataExtractor(config)
        return extractor.get_market_data(
            tickers=symbols_medium,
            start=start_date,
            end=end_date,
            interval='1d'
        )
    
    data_medium = benchmark.measure_time_and_memory(
        extract_yahoo_medium,
        "Yahoo Finance - 8 símbolos (1 año, 1d)"
    )
    
    # 3. Datos a corto plazo (7 días, 1h)
    def extract_yahoo_shortterm():
        config = ExtractorConfig(source='yahoo', timeout=30)
        extractor = DataExtractor(config)
        return extractor.get_market_data(
            tickers=symbols_small,
            start=end_date - timedelta(days=7),
            end=end_date,
            interval='1h'
        )
    
    data_shortterm = benchmark.measure_time_and_memory(
        extract_yahoo_shortterm,
        "Yahoo Finance - 3 símbolos (7 días, 1h intradiario)"
    )
    
    benchmark.print_summary()
    return data_small, data_medium, data_shortterm, benchmark


def benchmark_data_processing(prices_df: pd.DataFrame):
    """Benchmark de procesamiento de datos."""
    benchmark = PerformanceBenchmark()
    
    print("\n" + "=" * 60)
    print(" " * 10 + "BENCHMARK: PROCESAMIENTO DE DATOS")
    print("=" * 60)
    
    # 1. Limpieza de datos
    def clean_data():
        cleaner = DataCleaner()
        return cleaner.clean_dataframe(prices_df.copy())
    
    cleaned_data = benchmark.measure_time_and_memory(
        clean_data,
        "Limpieza de DataFrame"
    )
    
    # 2. Cálculo de retornos logarítmicos
    def calculate_log_returns():
        return np.log(prices_df / prices_df.shift(1)).dropna()
    
    returns = benchmark.measure_time_and_memory(
        calculate_log_returns,
        "Cálculo de retornos logarítmicos"
    )
    
    # 3. Cálculo de matriz de correlación
    def calculate_correlation():
        return returns.corr()
    
    benchmark.measure_time_and_memory(
        calculate_correlation,
        "Matriz de correlación"
    )
    
    # 4. Cálculo de matriz de covarianza
    def calculate_covariance():
        return returns.cov()
    
    benchmark.measure_time_and_memory(
        calculate_covariance,
        "Matriz de covarianza"
    )
    
    benchmark.print_summary()
    return cleaned_data, returns, benchmark


def benchmark_portfolio_operations(prices_df: pd.DataFrame):
    """Benchmark de operaciones de portfolio."""
    benchmark = PerformanceBenchmark()
    
    print("\n" + "=" * 60)
    print(" " * 10 + "BENCHMARK: OPERACIONES DE PORTFOLIO")
    print("=" * 60)
    
    symbols = prices_df.columns.tolist()
    n_assets = len(symbols)
    weights = [1/n_assets] * n_assets  # Pesos iguales
    
    # 1. Crear portfolio
    def create_portfolio():
        portfolio = Portfolio(
            name="Test Portfolio",
            symbols=symbols,
            weights=weights
        )
        portfolio.set_prices(prices_df)
        return portfolio
    
    portfolio = benchmark.measure_time_and_memory(
        create_portfolio,
        f"Crear portfolio ({n_assets} activos)"
    )
    
    if portfolio is None:
        print("[WARNING] No se pudo crear el portfolio, saltando benchmarks restantes")
        return None, benchmark
    
    # 2. Calcular retorno del portfolio
    def calc_return():
        return portfolio.portfolio_return()
    
    benchmark.measure_time_and_memory(
        calc_return,
        "Calcular retorno del portfolio"
    )
    
    # 3. Calcular volatilidad del portfolio
    def calc_volatility():
        return portfolio.portfolio_volatility()
    
    benchmark.measure_time_and_memory(
        calc_volatility,
        "Calcular volatilidad del portfolio"
    )
    
    # 4. Calcular Sharpe Ratio
    def calc_sharpe():
        return portfolio.sharpe_ratio()
    
    benchmark.measure_time_and_memory(
        calc_sharpe,
        "Calcular Sharpe Ratio"
    )
    
    # 5. Generar reporte
    def generate_report():
        return portfolio.report(include_warnings=False)
    
    benchmark.measure_time_and_memory(
        generate_report,
        "Generar reporte de portfolio"
    )
    
    benchmark.print_summary()
    return portfolio, benchmark


def benchmark_monte_carlo(portfolio: Portfolio):
    """Benchmark de simulaciones Monte Carlo."""
    benchmark = PerformanceBenchmark()
    
    print("\n" + "=" * 60)
    print(" " * 10 + "BENCHMARK: SIMULACIONES MONTE CARLO")
    print("=" * 60)
    
    if portfolio is None:
        print("[WARNING] Portfolio no disponible, saltando benchmarks de Monte Carlo")
        return benchmark
    
    # 1. Simulación pequeña (1000 simulaciones, 30 días)
    def small_simulation():
        return portfolio.monte_carlo_simulation(
            n_simulations=1000,
            time_horizon=30,
            initial_value=10000.0,
            dynamic_volatility=False,
            random_seed=42
        )
    
    benchmark.measure_time_and_memory(
        small_simulation,
        "Monte Carlo - 1,000 simulaciones × 30 días (volatilidad constante)"
    )
    
    # 2. Simulación mediana (5000 simulaciones, 90 días)
    def medium_simulation():
        return portfolio.monte_carlo_simulation(
            n_simulations=5000,
            time_horizon=90,
            initial_value=10000.0,
            dynamic_volatility=False,
            random_seed=42
        )
    
    benchmark.measure_time_and_memory(
        medium_simulation,
        "Monte Carlo - 5,000 simulaciones × 90 días (volatilidad constante)"
    )
    
    # 3. Simulación grande (10000 simulaciones, 252 días)
    def large_simulation():
        return portfolio.monte_carlo_simulation(
            n_simulations=10000,
            time_horizon=252,
            initial_value=10000.0,
            dynamic_volatility=False,
            random_seed=42
        )
    
    results_large = benchmark.measure_time_and_memory(
        large_simulation,
        "Monte Carlo - 10,000 simulaciones × 252 días (volatilidad constante)"
    )
    
    # 4. Simulación con volatilidad dinámica
    def dynamic_simulation():
        return portfolio.monte_carlo_simulation(
            n_simulations=5000,
            time_horizon=90,
            initial_value=10000.0,
            dynamic_volatility=True,
            random_seed=42
        )
    
    benchmark.measure_time_and_memory(
        dynamic_simulation,
        "Monte Carlo - 5,000 simulaciones × 90 días (volatilidad DINÁMICA)"
    )
    
    # 5. Simulación individual de un activo
    if portfolio.symbols:
        symbol = portfolio.symbols[0]
        
        def individual_simulation():
            return portfolio.monte_carlo_simulation_individual(
                symbol=symbol,
                n_simulations=5000,
                time_horizon=90
            )
        
        benchmark.measure_time_and_memory(
            individual_simulation,
            f"Monte Carlo Individual - {symbol} (5,000 × 90 días)"
        )
    
    benchmark.print_summary()
    return benchmark


def main():
    """Ejecuta todos los benchmarks."""
    print("\n" + "="*80)
    print(" " * 15 + "ANALIZADOR BURSATIL - BENCHMARK DE RENDIMIENTO")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: pandas {pd.__version__}, numpy {np.__version__}")
    print("="*80)
    
    all_benchmarks = []
    
    # 1. Benchmark de extracción
    print("\n" + ">" * 60)
    print("FASE 1: EXTRACCION DE DATOS")
    print(">" * 60)
    data_small, data_medium, data_shortterm, bench1 = benchmark_data_extraction()
    all_benchmarks.append(('Extracción', bench1))
    
    # 2. Benchmark de procesamiento (usar datos medianos)
    if data_medium is not None and 'AAPL' in data_medium:
        print("\n" + ">" * 60)
        print("FASE 2: PROCESAMIENTO DE DATOS")
        print(">" * 60)
        # Extraer DataFrame de PriceSeries
        prices_df = data_medium['AAPL'].data if hasattr(data_medium['AAPL'], 'data') else data_medium['AAPL']
        cleaned, returns, bench2 = benchmark_data_processing(prices_df)
        all_benchmarks.append(('Procesamiento', bench2))
        
        # 3. Benchmark de portfolio
        print("\n" + ">" * 60)
        print("FASE 3: OPERACIONES DE PORTFOLIO")
        print(">" * 60)
        # Crear DataFrame con todos los precios de cierre
        all_prices = pd.DataFrame({
            symbol: series.data['Close'] if hasattr(series, 'data') else series['Close']
            for symbol, series in data_medium.items()
        })
        portfolio, bench3 = benchmark_portfolio_operations(all_prices)
        all_benchmarks.append(('Portfolio', bench3))
        
        # 4. Benchmark de Monte Carlo
        if portfolio is not None:
            print("\n" + ">" * 60)
            print("FASE 4: SIMULACIONES MONTE CARLO")
            print(">" * 60)
            bench4 = benchmark_monte_carlo(portfolio)
            all_benchmarks.append(('Monte Carlo', bench4))
    
    # Resumen global
    print("\n\n" + "="*80)
    print(" " * 20 + "RESUMEN GLOBAL DE RENDIMIENTO")
    print("="*80 + "\n")
    
    for phase_name, bench in all_benchmarks:
        print(f"\n[{phase_name.upper()}]")
        print("-" * 80)
        df = pd.DataFrame(bench.results)
        successful = df[df['Exito'] == '[OK]']
        if not successful.empty:
            print(f"  Tiempo total: {successful['Tiempo (s)'].sum():.4f} s")
            print(f"  Memoria total: {successful['Memoria (MB)'].sum():.2f} MB")
            print(f"  Exitosas: {len(successful)}/{len(df)}")
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETADO")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

