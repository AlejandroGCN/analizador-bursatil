"""
Clase Portfolio para gestionar carteras de activos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Constantes
ERR_NO_RETURNS = "No hay datos de retornos. Ejecuta set_prices primero."

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


@dataclass
class Portfolio:
    """
    Representa una cartera de inversión con análisis de riesgo y rendimiento.
    
    Esta clase encapsula una cartera de activos financieros, proporcionando métodos
    para calcular métricas de riesgo y rendimiento, así como para realizar simulaciones
    Monte Carlo. Es el componente central para el análisis cuantitativo de carteras.
    
    Características principales:
    - Gestión de pesos y composición de activos
    - Cálculo automático de métricas de riesgo/rendimiento
    - Simulación Monte Carlo integrada
    - Generación de reportes en markdown
    - Visualizaciones avanzadas de análisis
    
    Attributes:
        name (str): Nombre identificativo de la cartera
        symbols (list[str]): Lista de símbolos de activos
        weights (list[float]): Pesos de cada activo (deben sumar 1.0)
        prices (Optional[pd.DataFrame]): Precios históricos de cierre
        returns (Optional[pd.DataFrame]): Retornos logarítmicos calculados
    
    Example:
        >>> # Crear cartera básica
        >>> portfolio = Portfolio(
        ...     name="Tech Portfolio",
        ...     symbols=['AAPL', 'MSFT', 'GOOGL'],
        ...     weights=[0.4, 0.3, 0.3]
        ... )
        
        >>> # Establecer datos de precios
        >>> portfolio.set_prices(price_dataframe)
        
        >>> # Calcular métricas
        >>> ret = portfolio.portfolio_return()
        >>> vol = portfolio.portfolio_volatility()
        >>> sharpe = portfolio.sharpe_ratio()
        
        >>> # Simulación Monte Carlo
        >>> simulation = portfolio.monte_carlo_simulation(
        ...     n_simulations=1000,
        ...     time_horizon=252
        ... )
        
        >>> # Generar reportes
        >>> report = portfolio.report()
        >>> portfolio.plots_report()
    
    Note:
        Los pesos se normalizan automáticamente si no suman 1.0.
        Los retornos se calculan como logarítmicos tras establecer precios.
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
            raise ValueError(ERR_NO_RETURNS)
        
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
            raise ValueError(ERR_NO_RETURNS)
        
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
            raise ValueError(ERR_NO_RETURNS)
        
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
    
    def _build_risk_analysis(self, stats: dict) -> str:
        """Construye la sección de análisis de riesgo del reporte."""
        md = "## ⚠️ Análisis de Riesgo\n\n"
        volatility = stats['volatility']
        
        if volatility > 0.3:
            md += "- **Nivel de riesgo**: 🔴 ALTO\n"
            md += "- La volatilidad es elevada. Considera diversificar más.\n\n"
        elif volatility > 0.15:
            md += "- **Nivel de riesgo**: 🟡 MEDIO\n\n"
        else:
            md += "- **Nivel de riesgo**: 🟢 BAJO\n\n"
        
        sharpe = stats['sharpe_ratio']
        if sharpe > 1.0:
            md += "- ✅ **Ratio de Sharpe excelente** (>1.0)\n"
        elif sharpe > 0.5:
            md += "- ⚠️ Ratio de Sharpe aceptable (>0.5)\n"
        else:
            md += "- ⚠️ **Ratio de Sharpe bajo** (<0.5). Considera rebalancear la cartera.\n"
        md += "\n"
        return md
    
    def _build_warnings_section(self) -> str:
        """Construye la sección de advertencias del reporte."""
        md = "## ⚠️ Advertencias y Recomendaciones\n\n"
        
        # Concentración de riesgo
        max_weight = max(self.weights)
        if max_weight > 0.4:
            md += f"- ⚠️ **Alta concentración**: El activo más grande representa {max_weight:.1%} de la cartera.\n"
        
        # Número de activos
        if len(self.symbols) < 5:
            md += "- 💡 **Diversificación limitada**: Considera añadir más activos para reducir el riesgo no sistemático.\n"
        
        # Calidad de datos
        if self.returns is not None:
            missing_returns = self.returns.isna().sum().sum()
            total_returns = self.returns.size
            missing_pct = (missing_returns / total_returns) * 100
            if missing_pct > 5:
                md += f"- ⚠️ **Datos incompletos**: {missing_pct:.1f}% de los datos están faltantes.\n"
        
        md += "\n"
        return md

    def report(
        self,
        risk_free_rate: float = 0.0,
        include_warnings: bool = True
    ) -> str:
        """
        Genera un reporte en markdown con análisis de la cartera.
        
        Args:
            risk_free_rate: Tasa libre de riesgo para cálculos
            include_warnings: Si True, incluye advertencias sobre la cartera
        
        Returns:
            Cadena markdown con el reporte
        """
        if self.returns is None:
            raise ValueError(ERR_NO_RETURNS)
        
        # Obtener estadísticas con tasa libre de riesgo personalizada
        stats = {
            "return": self.portfolio_return(),
            "volatility": self.portfolio_volatility(),
            "sharpe_ratio": self.sharpe_ratio(risk_free_rate=risk_free_rate),
            "num_assets": len(self.symbols)
        }
        
        md = f"""# Reporte de Análisis - {self.name}

## 📊 Composición de la Cartera

La cartera está compuesta por **{len(self.symbols)} activos**:

"""
        
        # Tabla de composición
        composition = "| Activo | Peso |\n|--------|------|\n"
        for symbol, weight in zip(self.symbols, self.weights):
            composition += f"| {symbol} | {weight:.2%} |\n"
        md += composition + "\n"
        
        # Métricas principales
        md += f"""## 📈 Métricas Principales

- **Retorno esperado (anualizado)**: {stats['return'] * 252:.2%}
- **Volatilidad (anualizada)**: {stats['volatility']:.2%}
- **Ratio de Sharpe**: {stats['sharpe_ratio']:.2f}
- **Número de activos**: {stats['num_assets']}

"""
        
        # Análisis de riesgo usando función auxiliar
        md += self._build_risk_analysis(stats)
        
        # Advertencias usando función auxiliar
        if include_warnings:
            md += self._build_warnings_section()
        
        # Correlaciones
        if self.returns is not None and len(self.symbols) > 1:
            md += "## 🔗 Matriz de Correlación\n\n"
            corr_matrix = self.returns.corr()
            md += "```\n"
            md += corr_matrix.to_string()
            md += "\n```\n\n"
        
        # Información de datos
        if self.prices is not None:
            md += f"""## 📅 Información de Datos

- **Periodo**: {self.prices.index.min().strftime('%Y-%m-%d')} a {self.prices.index.max().strftime('%Y-%m-%d')}
- **Número de observaciones**: {len(self.prices)}

"""
        
        md += "---\n\n"
        md += f"*Reporte generado el {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return md
    
    def _plot_prices_evolution(self, fig, gs):
        """Grafica la evolución temporal de precios."""
        ax1 = fig.add_subplot(gs[0, :])
        if self.prices is not None:
            for symbol in self.prices.columns:
                ax1.plot(self.prices.index, self.prices[symbol], label=symbol, alpha=0.7)
            ax1.set_title("Evolución Temporal de Precios", fontsize=14, fontweight='bold')
            ax1.set_xlabel("Fecha")
            ax1.set_ylabel("Precio de Cierre")
            ax1.legend()
            ax1.grid(True, alpha=0.3)
    
    def _plot_weights_distribution(self, fig, gs):
        """Grafica la distribución de pesos."""
        ax2 = fig.add_subplot(gs[1, 0])
        colors = plt.cm.tab10(range(len(self.symbols)))
        bars = ax2.bar(self.symbols, [w*100 for w in self.weights], color=colors)
        ax2.set_title("Distribución de Pesos", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Peso (%)")
        ax2.tick_params(axis='x', rotation=45)
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    def _plot_correlation_matrix(self, fig, gs):
        """Grafica la matriz de correlación."""
        ax3 = fig.add_subplot(gs[1, 1])
        corr_matrix = self.returns.corr()
        if HAS_SEABORN:
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, ax=ax3, fmt='.2f', cbar_kws={'shrink': 0.8})
        else:
            im = ax3.imshow(corr_matrix.values, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
            ax3.set_xticks(range(len(corr_matrix.columns)))
            ax3.set_yticks(range(len(corr_matrix.index)))
            ax3.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
            ax3.set_yticklabels(corr_matrix.index)
            plt.colorbar(im, ax=ax3)
            for i in range(len(corr_matrix.index)):
                for j in range(len(corr_matrix.columns)):
                    ax3.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                            ha='center', va='center', color='black' if abs(corr_matrix.iloc[i, j]) < 0.5 else 'white')
        ax3.set_title("Matriz de Correlación", fontsize=12, fontweight='bold')
    
    def _plot_returns_distribution(self, fig, gs):
        """Grafica la distribución de retornos."""
        ax4 = fig.add_subplot(gs[2, 0])
        portfolio_returns = self.returns @ self.weights
        ax4.hist(portfolio_returns * 252, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
        ax4.axvline(portfolio_returns.mean() * 252, color='red', linestyle='--', linewidth=2, label='Media')
        ax4.set_title("Distribución de Retornos Anualizados", fontsize=12, fontweight='bold')
        ax4.set_xlabel("Retorno Anualizado")
        ax4.set_ylabel("Frecuencia")
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    def _plot_key_metrics(self, fig, gs):
        """Grafica las métricas clave."""
        ax5 = fig.add_subplot(gs[2, 1])
        stats = self.get_statistics()
        metrics = ['Retorno\n(anual)', 'Volatilidad\n(anual)', 'Sharpe\nRatio']
        values = [
            stats['return'] * 252,
            stats['volatility'],
            stats['sharpe_ratio']
        ]
        bars = ax5.bar(metrics, values, color=['green', 'orange', 'blue'])
        ax5.set_title("Métricas Clave", fontsize=12, fontweight='bold')
        ax5.set_ylabel("Valor")
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Añadir valores en las barras
        for bar, val in zip(bars, values):
            height = bar.get_height()
            if bar == bars[0]:
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.2%}', ha='center', va='bottom', fontweight='bold')
            elif bar == bars[2]:
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
            else:
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.2%}', ha='center', va='bottom', fontweight='bold')

    def plots_report(
        self,
        figsize: Tuple[int, int] = (16, 10),
        save_path: Optional[str] = None
    ) -> None:
        """
        Genera y muestra visualizaciones relevantes de la cartera.
        
        Args:
            figsize: Tamaño de las figuras
            save_path: Si se proporciona, guarda las figuras en esta ruta
        """
        if self.returns is None or self.prices is None:
            raise ValueError("No hay datos. Ejecuta set_prices primero.")
        
        # Configurar estilo
        if HAS_SEABORN:
            sns.set_style("whitegrid")
        else:
            plt.style.use('default')
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Generar todos los subplots usando funciones auxiliares
        self._plot_prices_evolution(fig, gs)
        self._plot_weights_distribution(fig, gs)
        self._plot_correlation_matrix(fig, gs)
        self._plot_returns_distribution(fig, gs)
        self._plot_key_metrics(fig, gs)
        
        plt.suptitle(f"Análisis Completo - {self.name}", fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figura guardada en: {save_path}")
        
        plt.show()
