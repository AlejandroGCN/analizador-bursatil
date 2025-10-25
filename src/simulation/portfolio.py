"""
Clase Portfolio para gestionar carteras de activos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class Portfolio:
    """
    Clase para representar una cartera de activos.
    
    Attributes:
        name: Nombre de la cartera
        symbols: Lista de símbolos de activos
        weights: Pesos de cada activo en la cartera (deben sumar 1.0)
        prices: DataFrame con precios históricos de cierre
        returns: DataFrame con retornos de los activos
    """
    name: str
    symbols: list[str]
    weights: list[float]
    prices: Optional[pd.DataFrame] = None
    returns: Optional[pd.DataFrame] = None
    
    def __post_init__(self) -> None:
        """Validar los pesos y asegurarse de que sumen 1.0"""
        if len(self.symbols) != len(self.weights):
            raise ValueError(f"Longitud de símbolos ({len(self.symbols)}) no coincide con pesos ({len(self.weights)})")
        
        total_weight = sum(self.weights)
        if not (0.99 <= total_weight <= 1.01):
            # Normalizar pesos si no suman 1.0
            self.weights = [w / total_weight for w in self.weights]
    
    def set_prices(self, prices_df: pd.DataFrame) -> None:
        """
        Establece los precios de la cartera y calcula los retornos.
        
        Args:
            prices_df: DataFrame con precios históricos (columnas = símbolos)
        """
        self.prices = prices_df
        
        # Calcular retornos logarítmicos
        if prices_df.empty:
            raise ValueError("DataFrame de precios vacío")
        
        self.returns = np.log(prices_df / prices_df.shift(1)).dropna()
    
    def portfolio_return(self) -> float:
        """
        Retorna el retorno esperado de la cartera.
        
        Returns:
            Retorno esperado (media ponderada)
        """
        if self.returns is None:
            raise ValueError("No hay datos de retornos. Ejecuta set_prices primero.")
        
        # Retorno medio de cada activo
        mean_returns = self.returns.mean()
        
        # Retorno ponderado de la cartera
        return np.dot(self.weights, mean_returns)
    
    def portfolio_volatility(self) -> float:
        """
        Retorna la volatilidad de la cartera.
        
        Returns:
            Volatilidad anualizada de la cartera
        """
        if self.returns is None:
            raise ValueError("No hay datos de retornos. Ejecuta set_prices primero.")
        
        # Matriz de covarianza
        cov_matrix = self.returns.cov()
        
        # Volatilidad de la cartera
        portfolio_variance = np.dot(self.weights, np.dot(cov_matrix.values, self.weights))
        
        # Anualizar (asumiendo 252 días de trading)
        return np.sqrt(portfolio_variance * 252)
    
    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calcula el ratio de Sharpe de la cartera.
        
        Args:
            risk_free_rate: Tasa libre de riesgo anualizada (default: 0.0)
        
        Returns:
            Ratio de Sharpe
        """
        ret = self.portfolio_return() * 252  # Anualizar
        vol = self.portfolio_volatility()
        
        if vol == 0:
            return 0.0
        
        return (ret - risk_free_rate) / vol
    
    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas básicas de la cartera.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "return": self.portfolio_return(),
            "volatility": self.portfolio_volatility(),
            "sharpe_ratio": self.sharpe_ratio(),
            "num_assets": len(self.symbols)
        }
    
    def monte_carlo_simulation(
        self,
        n_simulations: int = 1000,
        time_horizon: int = 252,
        initial_value: float = 10000.0,
        dynamic_volatility: bool = False,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Ejecuta una simulación Monte Carlo de la cartera.
        
        Args:
            n_simulations: Número de simulaciones
            time_horizon: Horizonte temporal en días
            initial_value: Valor inicial de la cartera
            dynamic_volatility: Si True, usa volatilidad variable
            random_seed: Semilla para reproducibilidad
        
        Returns:
            DataFrame con las simulaciones
        """
        if self.returns is None:
            raise ValueError("No hay datos de retornos. Ejecuta set_prices primero.")
        
        from .monte_carlo import MonteCarloSimulation
        
        portfolio_return = self.portfolio_return()
        portfolio_volatility = self.portfolio_volatility()
        
        return MonteCarloSimulation.simulate_portfolio(
            portfolio_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            n_simulations=n_simulations,
            time_horizon=time_horizon,
            initial_value=initial_value,
            dynamic_volatility=dynamic_volatility,
            random_seed=random_seed
        )
    
    def visualize_monte_carlo(
        self,
        simulation_results: pd.DataFrame,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 6),
        max_paths: int = 100
    ) -> None:
        """
        Visualiza los resultados de una simulación Monte Carlo.
        
        Args:
            simulation_results: DataFrame con los resultados de la simulación
            title: Título del gráfico
            figsize: Tamaño de la figura
            max_paths: Número máximo de caminos a mostrar
        """
        if title is None:
            title = f"Simulación Monte Carlo - {self.name}"
        
        from .monte_carlo import MonteCarloSimulation
        MonteCarloSimulation.plot_simulation(
            simulation_results=simulation_results,
            title=title,
            figsize=figsize,
            max_paths=max_paths
        )
