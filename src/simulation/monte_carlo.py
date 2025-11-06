# -*- coding: utf-8 -*-
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
import os
import logging

logger = logging.getLogger(__name__)


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
    
    Implementa el modelo de Movimiento Browniano Geométrico (GBM) usando
    retornos logarítmicos para simular trayectorias de precios.
    
    El modelo matemático es:
        log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt × Z
    
    donde:
        - μ: retorno logarítmico medio (drift)
        - σ: volatilidad
        - Δt: incremento de tiempo (1 día)
        - Z ~ N(0,1): shock aleatorio normal estándar
    
    El término -σ²/2 es la corrección de Itô que asegura que E[S_t] = S_0 * e^(μt).
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
        Simula la evolución de una cartera usando Monte Carlo con retornos logarítmicos.
        
        Implementa el modelo de Movimiento Browniano Geométrico (GBM):
            log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt × Z
        
        donde el término -σ²/2 es la corrección de Itô que asegura que la media
        de los precios simulados sea consistente con el drift esperado.
        
        Args:
            portfolio_return: Retorno logarítmico medio diario de la cartera (drift μ)
            portfolio_volatility: Volatilidad de la cartera (anualizada)
            n_simulations: Número de simulaciones a realizar
            time_horizon: Horizonte temporal en días
            initial_value: Valor inicial de la cartera
            dynamic_volatility: Si True, usa volatilidad variable entre [0.8σ, 1.2σ]
            random_seed: Semilla para reproducibilidad de resultados
        
        Returns:
            DataFrame con las simulaciones (filas = simulaciones, columnas = días)
            La columna 0 contiene el valor inicial, las columnas 1 a time_horizon
            contienen los valores simulados para cada día.
        """
        logger.debug("🎲 MonteCarloSimulation.simulate_portfolio")
        logger.debug(f"  Inputs: ret={portfolio_return:.8f}, vol={portfolio_volatility:.6f}")
        logger.debug(f"  n_sims={n_simulations}, horizon={time_horizon}, init_val={initial_value}")
        
        # Usar generator en lugar de numpy.random legacy API
        rng = default_rng(random_seed)
        
        # Convertir volatilidad anualizada a diaria
        # Si volatilidad anual = σ_anual, entonces volatilidad diaria = σ_anual / √252
        vol_daily = portfolio_volatility / np.sqrt(252)
        logger.debug(f"  Volatilidad anualizada: {portfolio_volatility:.6f}")
        logger.debug(f"  Volatilidad diaria: {vol_daily:.8f}")
        
        # OPTIMIZACIÓN: Generar todas las simulaciones de forma vectorizada
        # Forma: (n_simulations, time_horizon)
        if dynamic_volatility:
            # Volatilidad variable para cada paso de cada simulación
            vol_multipliers = rng.uniform(0.8, 1.2, size=(n_simulations, time_horizon))
            vols_daily = vol_daily * vol_multipliers
            logger.debug(f"  Volatilidad dinámica diaria: rango {vols_daily.min():.6f} - {vols_daily.max():.6f}")
        else:
            vols_daily = vol_daily  # Constante para todas las simulaciones
            logger.debug("  Volatilidad diaria constante: %.6f", vol_daily)
        
        # Generar shocks aleatorios para todas las simulaciones
        shocks = rng.normal(0, 1, size=(n_simulations, time_horizon))
        logger.debug(f"  Shocks generados: media={shocks.mean():.6f}, std={shocks.std():.6f}")
        
        # Calcular retornos LOGARÍTMICOS de forma vectorizada
        # Modelo de Movimiento Browniano Geométrico (GBM):
        # log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt × Z
        # donde Δt = 1 día, μ es el drift, σ es volatilidad, Z ~ N(0,1)
        #
        # Nota: portfolio_return ya es el retorno logarítmico medio diario calculado
        # de los datos históricos, así que representa el drift estimado μ
        
        if dynamic_volatility:
            # Término de drift ajustado por volatilidad (corrección de Itô)
            drift = portfolio_return - 0.5 * (vols_daily ** 2)
            # Término de difusión (shock estocástico)
            diffusion = vols_daily * shocks
            # Retorno logarítmico total
            log_returns = drift + diffusion
        else:
            # Término de drift ajustado por volatilidad (corrección de Itô)
            drift = portfolio_return - 0.5 * (vol_daily ** 2)
            # Término de difusión (shock estocástico)
            diffusion = vol_daily * shocks
            # Retorno logarítmico total
            log_returns = drift + diffusion
        
        logger.debug(f"  Retornos logarítmicos simulados: media={log_returns.mean():.8f}, std={log_returns.std():.8f}")
        logger.debug(f"  Retornos log - min={log_returns.min():.8f}, max={log_returns.max():.8f}")
        
        # Convertir retornos logarítmicos a factores de crecimiento
        # S_t / S_{t-1} = exp(log_return)
        growth_factors = np.exp(log_returns)
        logger.debug(f"  Factores de crecimiento: media={growth_factors.mean():.6f}")
        logger.debug(f"  Factores - min={growth_factors.min():.6f}, max={growth_factors.max():.6f}")
        
        # Inicializar con valor inicial
        trajectories = np.full((n_simulations, time_horizon + 1), initial_value, dtype=float)
        
        # Multiplicar acumuladamente los factores de crecimiento
        trajectories[:, 1:] = initial_value * np.cumprod(growth_factors, axis=1)
        
        logger.debug(f"  Trayectorias generadas: shape={trajectories.shape}")
        logger.debug(f"  Valor final medio: ${trajectories[:, -1].mean():,.2f}")
        logger.debug(f"  Valor final std: ${trajectories[:, -1].std():,.2f}")
        
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
        max_paths: int = 100,
        return_figure: bool = False
    ):
        """
        Visualiza los resultados de una simulación Monte Carlo.
        
        Args:
            simulation_results: DataFrame con resultados
            title: Título del gráfico
            figsize: Tamaño de la figura
            max_paths: Número máximo de trayectorias a mostrar
            return_figure: Si True, retorna la figura en lugar de mostrarla
        
        Returns:
            None o matplotlib.figure.Figure dependiendo de return_figure
        """
        # Detectar si estamos en Streamlit
        is_streamlit = 'STREAMLIT_SERVER_PORT' in os.environ
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Mostrar subconjunto de trayectorias
        sample_paths = min(max_paths, len(simulation_results))
        rng = default_rng(seed=42)  # Seed para reproducibilidad
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
        
        # En Streamlit o si se solicita retornar la figura, no llamar plt.show()
        if is_streamlit or return_figure:
            return fig
        
        plt.show()
        return None
    
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
