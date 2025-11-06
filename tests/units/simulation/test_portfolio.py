# -*- coding: utf-8 -*-
"""Tests unitarios para Portfolio."""
import pytest
import numpy as np
import pandas as pd
from simulation import Portfolio


@pytest.fixture
def sample_prices():
    """Fixture con precios de muestra."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    prices = pd.DataFrame({
        'AAPL': 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, 100))),
        'MSFT': 150 * np.exp(np.cumsum(np.random.normal(0.0004, 0.018, 100))),
        'GOOGL': 120 * np.exp(np.cumsum(np.random.normal(0.0006, 0.022, 100)))
    }, index=dates)
    
    return prices


@pytest.fixture
def sample_portfolio(sample_prices):
    """Fixture con portfolio de muestra."""
    portfolio = Portfolio(
        name="Test Portfolio",
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        weights=[0.4, 0.3, 0.3]
    )
    portfolio.set_prices(sample_prices)
    return portfolio


class TestPortfolioCreation:
    """Tests de creación y validación de Portfolio."""
    
    def test_portfolio_creation_valid(self):
        """Test creación de portfolio válido."""
        portfolio = Portfolio(
            name="Tech Portfolio",
            symbols=['AAPL', 'MSFT'],
            weights=[0.6, 0.4]
        )
        
        assert portfolio.name == "Tech Portfolio"
        assert portfolio.symbols == ['AAPL', 'MSFT']
        assert portfolio.weights == [0.6, 0.4]
    
    def test_portfolio_auto_normalize_weights(self):
        """Test que normaliza pesos automáticamente si no suman 1.0."""
        portfolio = Portfolio(
            name="Test",
            symbols=['A', 'B'],
            weights=[60, 40]  # Suman 100, no 1.0
        )
        
        # Debería normalizarlos
        assert abs(sum(portfolio.weights) - 1.0) < 0.001
        assert abs(portfolio.weights[0] - 0.6) < 0.001
        assert abs(portfolio.weights[1] - 0.4) < 0.001
    
    def test_portfolio_invalid_weights_length(self):
        """Test que falla si símbolos y pesos no coinciden."""
        with pytest.raises(ValueError, match="Longitud de símbolos"):
            Portfolio(
                name="Test",
                symbols=['A', 'B', 'C'],
                weights=[0.5, 0.5]  # Solo 2 pesos para 3 símbolos
            )


class TestPortfolioPrices:
    """Tests relacionados con set_prices y cálculo de retornos."""
    
    def test_set_prices_calculates_returns(self, sample_prices):
        """Test que set_prices calcula retornos logarítmicos."""
        portfolio = Portfolio(
            name="Test",
            symbols=['AAPL', 'MSFT', 'GOOGL'],
            weights=[0.4, 0.3, 0.3]
        )
        
        portfolio.set_prices(sample_prices)
        
        # Verificar que se calcularon retornos
        assert portfolio.returns is not None
        assert isinstance(portfolio.returns, pd.DataFrame)
        
        # Verificar que son logarítmicos
        # retornos = log(P_t / P_{t-1})
        expected_returns = np.log(sample_prices / sample_prices.shift(1)).dropna()
        pd.testing.assert_frame_equal(portfolio.returns, expected_returns)
    
    def test_set_prices_empty_dataframe_raises(self):
        """Test que falla con DataFrame vacío."""
        portfolio = Portfolio(
            name="Test",
            symbols=['A'],
            weights=[1.0]
        )
        
        with pytest.raises(ValueError, match="vacío"):
            portfolio.set_prices(pd.DataFrame())


class TestPortfolioMetrics:
    """Tests de métricas de portfolio."""
    
    def test_portfolio_return(self, sample_portfolio):
        """Test cálculo de retorno esperado."""
        ret = sample_portfolio.portfolio_return()
        
        # Debe ser un número
        assert isinstance(ret, (int, float, np.number))
        
        # Retorno diario razonable (-1% a +1%)
        assert -0.01 < ret < 0.01
    
    def test_portfolio_volatility(self, sample_portfolio):
        """Test cálculo de volatilidad."""
        vol = sample_portfolio.portfolio_volatility()
        
        # Debe ser positivo
        assert vol > 0
        
        # Volatilidad anualizada razonable (5% a 100%)
        assert 0.05 < vol < 1.0
    
    def test_sharpe_ratio(self, sample_portfolio):
        """Test cálculo de ratio de Sharpe."""
        sharpe = sample_portfolio.sharpe_ratio(risk_free_rate=0.02)
        
        # Debe ser un número
        assert isinstance(sharpe, (int, float, np.number))
    
    def test_sharpe_ratio_zero_volatility(self):
        """Test Sharpe ratio con volatilidad cero."""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        prices = pd.DataFrame({
            'A': [100] * 10  # Precio constante
        }, index=dates)
        
        portfolio = Portfolio(name="Test", symbols=['A'], weights=[1.0])
        portfolio.set_prices(prices)
        
        # Con volatilidad 0, Sharpe debería ser 0
        sharpe = portfolio.sharpe_ratio()
        assert sharpe == 0.0
    
    def test_get_statistics(self, sample_portfolio):
        """Test obtención de estadísticas completas."""
        stats = sample_portfolio.get_statistics()
        
        assert 'return' in stats
        assert 'volatility' in stats
        assert 'sharpe_ratio' in stats
        assert 'num_assets' in stats
        assert stats['num_assets'] == 3
    
    def test_metrics_without_prices_raise(self):
        """Test que métricas fallan sin prices."""
        portfolio = Portfolio(
            name="Test",
            symbols=['A'],
            weights=[1.0]
        )
        
        with pytest.raises(ValueError, match="retornos"):
            portfolio.portfolio_return()
        
        with pytest.raises(ValueError, match="retornos"):
            portfolio.portfolio_volatility()


class TestPortfolioMonteCarlo:
    """Tests de simulación Monte Carlo en Portfolio."""
    
    def test_monte_carlo_simulation(self, sample_portfolio):
        """Test simulación Monte Carlo de cartera completa."""
        results = sample_portfolio.monte_carlo_simulation(
            n_simulations=100,
            time_horizon=50,
            initial_value=10000,
            random_seed=42
        )
        
        assert isinstance(results, pd.DataFrame)
        assert results.shape == (100, 51)
        assert (results > 0).all().all()
    
    def test_monte_carlo_simulation_individual(self, sample_portfolio):
        """Test simulación Monte Carlo de activo individual."""
        results = sample_portfolio.monte_carlo_simulation_individual(
            symbol='AAPL',
            n_simulations=100,
            time_horizon=50,
            random_seed=42
        )
        
        assert isinstance(results, pd.DataFrame)
        assert results.shape == (100, 51)
    
    def test_monte_carlo_individual_invalid_symbol(self, sample_portfolio):
        """Test que falla con símbolo inválido."""
        with pytest.raises(ValueError, match="no está en la cartera"):
            sample_portfolio.monte_carlo_simulation_individual(
                symbol='INVALID',
                n_simulations=10,
                time_horizon=10
            )
    
    def test_monte_carlo_individual_uses_current_price(self, sample_portfolio):
        """Test que usa precio actual si initial_value es None."""
        results = sample_portfolio.monte_carlo_simulation_individual(
            symbol='AAPL',
            n_simulations=10,
            time_horizon=5,
            initial_value=None,  # Debería usar precio actual
            random_seed=42
        )
        
        # Verificar que el valor inicial es cercano al último precio de AAPL
        last_price = sample_portfolio.prices['AAPL'].iloc[-1]
        initial_sim = results.iloc[0, 0]
        
        assert abs(initial_sim - last_price) < 0.01


class TestPortfolioReporting:
    """Tests de generación de reportes."""
    
    def test_report_generation(self, sample_portfolio):
        """Test generación de reporte en markdown."""
        report = sample_portfolio.report()
        
        assert isinstance(report, str)
        assert '# Reporte de Análisis' in report
        assert 'Test Portfolio' in report
        assert 'AAPL' in report
        assert 'MSFT' in report
        assert 'GOOGL' in report
    
    def test_report_with_custom_risk_free_rate(self, sample_portfolio):
        """Test reporte con tasa libre de riesgo personalizada."""
        report = sample_portfolio.report(risk_free_rate=0.03)
        
        assert isinstance(report, str)
        assert 'Sharpe' in report
    
    def test_report_without_warnings(self, sample_portfolio):
        """Test reporte sin advertencias."""
        report = sample_portfolio.report(include_warnings=False)
        
        assert isinstance(report, str)
        # No debería tener sección de advertencias
        assert '⚠️ Advertencias' not in report or 'Recomendaciones' not in report
    
    def test_plots_report_returns_figure(self, sample_portfolio):
        """Test que plots_report retorna figura."""
        fig = sample_portfolio.plots_report(return_figure=True)
        
        assert fig is not None
        
        # Limpiar
        import matplotlib.pyplot as plt
        plt.close(fig)

