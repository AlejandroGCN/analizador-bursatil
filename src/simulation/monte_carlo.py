"""
Módulo de simulación Monte Carlo para carteras de inversión.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt


@dataclass
class MonteCarloParams:
    """Parámetros de configuración para la simulación Monte Carlo."""
    n_simulations: int = 1000
    time_horizon: int = 252
    initial_value: float = 10000.0
    dynamic_volatility: bool = False
    random_seed: Optional[int] = None


class MonteCarloSimulation:
    """
    Clase para realizar simulaciones Monte Carlo de evolución de carteras.
    
    Usa el modelo de movimiento browniano geométrico para simular 
    trayectorias de precios.
    """
    
    @staticmethod
    def simulate_portfolio(
        portfolio_return: float,
        portfolio_volatility: float,
        n_simulations: int = 1000,
        time_horizon: int = 252,
        initial_value: float = 10000.0,
        dynamic_volatility: bool = False,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Simula la evolución de una cartera usando Monte Carlo (OPTIMIZADO con vectorización).
        
        Args:
            portfolio_return: Retorno esperado de la cartera (diario)
            portfolio_volatility: Volatilidad de la cartera (diaria)
            n_simulations: Número de simulaciones
            time_horizon: Horizonte temporal en días
            initial_value: Valor inicial de la cartera
            dynamic_volatility: Si True, usa volatilidad variable
            random_seed: Semilla para reproducibilidad
        
        Returns:
            DataFrame con las simulaciones (filas = simulaciones, columnas = días)
        """
        # Usar generator en lugar de numpy.random legacy API
        rng = default_rng(random_seed)
        
        dt = 1.0 / 252  # Paso temporal (un día en años)
        
        # OPTIMIZACIÓN: Generar todas las simulaciones de forma vectorizada
        # Forma: (n_simulations, time_horizon)
        if dynamic_volatility:
            # Volatilidad variable para cada paso de cada simulación
            vol_multipliers = rng.uniform(0.8, 1.2, size=(n_simulations, time_horizon))
            vols = portfolio_volatility * vol_multipliers
        else:
            vols = np.full((n_simulations, time_horizon), portfolio_volatility)
        
        # Generar shocks aleatorios para todas las simulaciones
        shocks = rng.normal(0, 1, size=(n_simulations, time_horizon))
        
        # Calcular retornos de forma vectorizada
        returns = portfolio_return * dt + vols * np.sqrt(dt) * shocks
        
        # Calcular trayectorias usando cumprod
        # Necesitamos convertir retornos a factores de crecimiento
        growth_factors = 1 + returns
        
        # Inicializar con valor inicial
        trajectories = np.full((n_simulations, time_horizon + 1), initial_value, dtype=float)
        
        # Multiplicar acumuladamente los factores de crecimiento
        trajectories[:, 1:] = initial_value * np.cumprod(growth_factors, axis=1)
        
        return pd.DataFrame(
            trajectories,
            index=range(n_simulations),
            columns=range(time_horizon + 1)
        )
    
    @staticmethod
    def simulate_asset(
        mean_return: float,
        volatility: float,
        n_simulations: int = 1000,
        time_horizon: int = 252,
        initial_price: float = 100.0,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Simula la evolución de un activo individual.
        
        Args:
            mean_return: Retorno medio esperado (diario)
            volatility: Volatilidad del activo (diaria)
            n_simulations: Número de simulaciones
            time_horizon: Horizonte temporal en días
            initial_price: Precio inicial
            random_seed: Semilla para reproducibilidad
        
        Returns:
            DataFrame con las simulaciones
        """
        return MonteCarloSimulation.simulate_portfolio(
            portfolio_return=mean_return,
            portfolio_volatility=volatility,
            n_simulations=n_simulations,
            time_horizon=time_horizon,
            initial_value=initial_price,
            dynamic_volatility=False,
            random_seed=random_seed
        )
    
    @staticmethod
    def calculate_percentiles(simulation_results: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula percentiles de los resultados de simulación.
        
        Args:
            simulation_results: DataFrame con resultados de simulación
        
        Returns:
            DataFrame con percentiles por cada período
        """
        percentiles = [5, 25, 50, 75, 95]
        results = simulation_results.quantile([p/100 for p in percentiles])
        results.index = [f"{p}%" for p in percentiles]
        return results
    
    @staticmethod
    def plot_simulation(
        simulation_results: pd.DataFrame,
        title: str = "Simulación Monte Carlo",
        figsize: Tuple[int, int] = (12, 6),
        max_paths: int = 100
    ) -> None:
        """
        Visualiza los resultados de una simulación Monte Carlo.
        
        Args:
            simulation_results: DataFrame con resultados
            title: Título del gráfico
            figsize: Tamaño de la figura
            max_paths: Número máximo de trayectorias a mostrar
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Mostrar subconjunto de trayectorias
        sample_paths = min(max_paths, len(simulation_results))
        rng = default_rng()
        sample_indices = rng.choice(
            len(simulation_results),
            sample_paths,
            replace=False
        )
        
        # Trayectorias individuales
        for idx in sample_indices:
            ax.plot(
                simulation_results.columns,
                simulation_results.iloc[idx],
                alpha=0.1,
                color='gray',
                linewidth=0.5
            )
        
        # Media
        mean_path = simulation_results.mean(axis=0)
        ax.plot(
            simulation_results.columns,
            mean_path,
            color='blue',
            linewidth=2,
            label='Media'
        )
        
        # Percentiles 5% y 95%
        upper = simulation_results.quantile(0.95, axis=0)
        lower = simulation_results.quantile(0.05, axis=0)
        ax.fill_between(
            simulation_results.columns,
            lower,
            upper,
            alpha=0.3,
            color='blue',
            label='Intervalo 90%'
        )
        
        ax.set_xlabel('Días')
        ax.set_ylabel('Valor de la cartera')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def get_final_statistics(simulation_results: pd.DataFrame) -> dict:
        """
        Obtiene estadísticas del valor final de la simulación.
        
        Args:
            simulation_results: DataFrame con resultados
        
        Returns:
            Diccionario con estadísticas
        """
        final_values = simulation_results.iloc[:, -1]
        
        return {
            "mean": final_values.mean(),
            "median": final_values.median(),
            "std": final_values.std(),
            "min": final_values.min(),
            "max": final_values.max(),
            "percentile_5": final_values.quantile(0.05),
            "percentile_95": final_values.quantile(0.95)
        }
