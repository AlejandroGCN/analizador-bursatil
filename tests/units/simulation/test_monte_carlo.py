# -*- coding: utf-8 -*-
"""Tests unitarios para MonteCarloSimulation."""
import pytest
import numpy as np
import pandas as pd
from simulation import MonteCarloSimulation, MonteCarloParams


class TestMonteCarloSimulation:
    """Tests para la clase MonteCarloSimulation."""
    
    def test_simulate_portfolio_basic(self):
        """Test simulación básica con parámetros válidos."""
        result = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=0.0005,
            portfolio_volatility=0.20,
            n_simulations=100,
            time_horizon=10,
            initial_value=10000,
            random_seed=42
        )
        
        # Verificar estructura
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (100, 11)  # 100 sims, 11 columnas (0 a 10)
        
        # Verificar valor inicial
        assert (result.iloc[:, 0] == 10000).all()
        
        # Verificar precios positivos
        assert (result > 0).all().all()
    
    def test_log_returns_guarantee_positive_prices(self):
        """Test que retornos logarítmicos garantizan precios positivos."""
        # Con volatilidad muy alta
        result = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=0.0005,
            portfolio_volatility=0.80,  # 80% volatilidad!
            n_simulations=1000,
            time_horizon=252,
            initial_value=10000,
            random_seed=42
        )
        
        # Incluso con volatilidad extrema, todos los precios son positivos
        min_price = result.min().min()
        assert min_price > 0, f"Precio negativo encontrado: {min_price}"
    
    def test_ito_correction_works(self):
        """Test que la corrección de Itô funciona correctamente."""
        mu_daily = 0.0003
        sigma_annual = 0.20
        t = 252
        S0 = 10000
        
        # Valor esperado teórico: S_0 * e^(μ * t)
        expected = S0 * np.exp(mu_daily * t)
        
        # Simular
        result = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=mu_daily,
            portfolio_volatility=sigma_annual,
            n_simulations=5000,
            time_horizon=t,
            initial_value=S0,
            random_seed=42
        )
        
        actual = result.iloc[:, -1].mean()
        error = abs(actual - expected) / expected
        
        # Error debe ser menor al 2% (Monte Carlo noise)
        assert error < 0.02, f"Error: {error:.4%} > 2%"
    
    def test_dynamic_volatility(self):
        """Test simulación con volatilidad dinámica."""
        result = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=0.0005,
            portfolio_volatility=0.25,
            n_simulations=100,
            time_horizon=50,
            initial_value=10000,
            dynamic_volatility=True,
            random_seed=42
        )
        
        # Verificar que funciona
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (100, 51)
        
        # Con volatilidad dinámica debería haber más dispersión
        std_dynamic = result.iloc[:, -1].std()
        assert std_dynamic > 0
    
    def test_random_seed_reproducibility(self):
        """Test que random_seed produce resultados reproducibles."""
        result1 = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=0.0005,
            portfolio_volatility=0.20,
            n_simulations=100,
            time_horizon=10,
            initial_value=10000,
            random_seed=42
        )
        
        result2 = MonteCarloSimulation.simulate_portfolio(
            portfolio_return=0.0005,
            portfolio_volatility=0.20,
            n_simulations=100,
            time_horizon=10,
            initial_value=10000,
            random_seed=42
        )
        
        # Resultados deben ser idénticos
        pd.testing.assert_frame_equal(result1, result2)
    
    def test_simulate_asset(self):
        """Test simulación de activo individual."""
        result = MonteCarloSimulation.simulate_asset(
            mean_return=0.0004,
            volatility=0.18,
            n_simulations=50,
            time_horizon=20,
            initial_price=100.0,
            random_seed=42
        )
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (50, 21)
        assert (result.iloc[:, 0] == 100.0).all()
    
    def test_calculate_percentiles(self):
        """Test cálculo de percentiles."""
        # Crear datos de simulación simple
        data = pd.DataFrame({
            0: [100] * 100,
            1: range(100, 200),
            2: range(200, 300)
        })
        
        result = MonteCarloSimulation.calculate_percentiles(data)
        
        # Verificar estructura
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (5, 3)  # 5 percentiles, 3 columnas
        assert list(result.index) == ['5%', '25%', '50%', '75%', '95%']
    
    def test_get_final_statistics(self):
        """Test estadísticas del valor final."""
        # Crear datos de simulación
        data = pd.DataFrame({
            0: [10000] * 100,
            1: [10500] * 100,
            2: np.random.uniform(9000, 12000, 100)
        })
        
        stats = MonteCarloSimulation.get_final_statistics(data)
        
        # Verificar claves
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'percentile_5' in stats
        assert 'percentile_95' in stats
        
        # Verificar valores razonables
        assert 9000 <= stats['mean'] <= 12000
        assert stats['min'] < stats['mean'] < stats['max']
    
    def test_plot_simulation_returns_figure(self):
        """Test que plot_simulation retorna figura."""
        data = pd.DataFrame({
            0: [10000] * 10,
            1: np.random.uniform(9500, 10500, 10),
            2: np.random.uniform(9000, 11000, 10)
        })
        
        fig = MonteCarloSimulation.plot_simulation(
            simulation_results=data,
            title="Test",
            return_figure=True
        )
        
        assert fig is not None
        
        # Limpiar
        import matplotlib.pyplot as plt
        plt.close(fig)


class TestMonteCarloParams:
    """Tests para MonteCarloParams dataclass."""
    
    def test_params_default_values(self):
        """Test valores por defecto de MonteCarloParams."""
        params = MonteCarloParams()
        
        assert params.n_simulations == 1000
        assert params.time_horizon == 252
        assert params.initial_value == 10000.0
        assert params.dynamic_volatility is False
        assert params.random_seed is None
    
    def test_params_custom_values(self):
        """Test valores personalizados."""
        params = MonteCarloParams(
            n_simulations=500,
            time_horizon=126,
            initial_value=5000.0,
            dynamic_volatility=True,
            random_seed=123
        )
        
        assert params.n_simulations == 500
        assert params.time_horizon == 126
        assert params.initial_value == 5000.0
        assert params.dynamic_volatility is True
        assert params.random_seed == 123

