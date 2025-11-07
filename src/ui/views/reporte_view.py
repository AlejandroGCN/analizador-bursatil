from __future__ import annotations
from typing import Any, Optional
import streamlit as st
import pandas as pd
import logging
from ui.sidebars import ReporteParams
from ui.views.montecarlo_view import _get_prices_from_data_map

logger = logging.getLogger(__name__)


def _check_prerequisites() -> bool:
    """Verifica que existan los prerrequisitos para generar el reporte."""
    missing_steps = []
    
    # Verificar si hay una simulación individual activa
    sim_type = st.session_state.get("montecarlo_sim_type")
    individual_symbol = st.session_state.get("montecarlo_symbol")
    
    # Si es simulación individual, solo verificar datos
    if sim_type == "individual" and individual_symbol:
        if "last_data_map" not in st.session_state:
            missing_steps.append("📊 Descarga datos en la pestaña 'Datos'")
    else:
        # Para cartera completa, verificar cartera configurada
        if "portfolio_symbols" not in st.session_state or "portfolio_weights" not in st.session_state:
            missing_steps.append("💼 Configura una cartera en la pestaña 'Cartera'")
        
        if "last_data_map" not in st.session_state:
            missing_steps.append("📊 Descarga datos en la pestaña 'Datos'")
    
    # Validar que los datos sean precios históricos (no retornos)
    last_kind = st.session_state.get("last_kind", "ohlcv")
    if last_kind != "ohlcv":
        missing_steps.append(f"📊 Cambia el tipo de datos a 'Precios Históricos' (actualmente: '{last_kind}')")
    
    if missing_steps:
        st.warning("⚠️ **Faltan pasos previos para generar el reporte:**")
        for step in missing_steps:
            st.markdown(f"- {step}")
        st.info("💡 Completa los pasos anteriores y regresa aquí para ver el reporte completo.")
        return False
    
    return True


def _adjust_weights_for_available_symbols(
    portfolio_symbols: list[str], 
    portfolio_weights: list[float], 
    available_symbols: list[str]
) -> Optional[tuple[list[str], list[float]]]:
    """
    Ajusta los pesos si faltan algunos símbolos en los datos.
    
    Utiliza funciones compartidas de ui.utils para evitar duplicación de código.
    
    Args:
        portfolio_symbols: Lista de símbolos de la cartera
        portfolio_weights: Lista de pesos de la cartera
        available_symbols: Lista de símbolos disponibles en los datos
    
    Returns:
        Tuple con (símbolos ajustados, pesos ajustados) o None si faltan símbolos críticos
    """
    from ui.utils import (
        normalize_symbol,
        create_normalized_symbol_dicts,
        get_symbols_mapped_to_data_format
    )
    
    # Crear diccionarios normalizados
    available_symbols_dict, portfolio_symbols_dict = create_normalized_symbol_dicts(
        available_symbols, portfolio_symbols
    )
    
    available_symbols_normalized = set(available_symbols_dict.keys())
    portfolio_symbols_set_normalized = set(portfolio_symbols_dict.keys())
    
    # Verificar si faltan símbolos
    if not portfolio_symbols_set_normalized.issubset(available_symbols_normalized):
        missing = portfolio_symbols_set_normalized - available_symbols_normalized
        missing_original = [
            portfolio_symbols_dict[norm] 
            for norm in missing 
            if norm in portfolio_symbols_dict
        ]
        st.error(
            f"⚠️ La cartera configurada no coincide con los datos descargados. "
            f"Símbolos faltantes: {', '.join(missing_original)}"
        )
        return None
    
    # Mapear símbolos al formato de datos
    symbols_in_data = get_symbols_mapped_to_data_format(
        portfolio_symbols, available_symbols_dict
    )
    
    # Si todos los símbolos están disponibles y coinciden, retornar directamente
    if len(symbols_in_data) == len(portfolio_symbols):
        return symbols_in_data, portfolio_weights
    
    # Ajustar pesos si faltan algunos símbolos
    symbol_to_weight = dict(zip(portfolio_symbols, portfolio_weights))
    filtered_weights = [symbol_to_weight[s] for s in symbols_in_data if s in symbol_to_weight]
    total_weight = sum(filtered_weights)
    
    if total_weight > 0:
        weights = [w / total_weight for w in filtered_weights]
    else:
        # Si no hay peso, usar pesos iguales
        n_assets = len(symbols_in_data)
        weights = [1.0 / n_assets] * n_assets
    
    return symbols_in_data, weights


@st.cache_data(ttl=300, show_spinner=False)
def _create_portfolio_from_data_cached(
    portfolio_symbols_tuple: tuple,
    portfolio_weights_tuple: tuple,
    data_map_hash: str
) -> tuple:
    """
    Crea un objeto Portfolio a partir de los datos disponibles (cacheado).
    
    Retorna tupla serializable para el cache.
    """
    from simulation import Portfolio
    
    logger.info("📋 Creando portfolio para reporte")
    
    data_map = st.session_state["last_data_map"]
    prices_dict = _get_prices_from_data_map(data_map)
    
    logger.debug(f"  Precios extraídos: {len(prices_dict)} símbolos")
    logger.debug(f"  Símbolos en precios: {list(prices_dict.keys())}")
    
    if not prices_dict:
        logger.error("No se pudieron extraer precios de los datos")
        return None, None, None
    
    prices_df = pd.DataFrame(prices_dict)
    portfolio_symbols = list(portfolio_symbols_tuple)
    portfolio_weights = list(portfolio_weights_tuple)
    available_symbols = list(prices_dict.keys())
    
    logger.debug(f"  Símbolos de cartera: {portfolio_symbols}")
    logger.debug(f"  Pesos de cartera: {portfolio_weights}")
    logger.debug(f"  Símbolos disponibles en datos: {available_symbols}")
    
    result = _adjust_weights_for_available_symbols(
        portfolio_symbols, portfolio_weights, available_symbols
    )
    
    if result is None:
        logger.info("No se pudo ajustar cartera - símbolos no coinciden (mostrado en UI)")
        return None, None, None
    
    symbols, weights = result
    
    logger.debug(f"  Símbolos ajustados: {symbols}")
    logger.debug(f"  Pesos ajustados: {weights}")
    logger.debug(f"  Suma de pesos: {sum(weights):.6f}")
    
    # Filtrar prices_df para que solo contenga los símbolos del portfolio
    logger.debug(f"  ANTES del filtrado:")
    logger.debug(f"    prices_df.columns: {list(prices_df.columns)}")
    logger.debug(f"    symbols del portfolio: {symbols}")
    logger.debug(f"    weights del portfolio: {weights}")
    
    available_columns = [col for col in symbols if col in prices_df.columns]
    if available_columns:
        prices_df_filtered = prices_df[available_columns]
        logger.debug(f"  DESPUÉS del filtrado:")
        logger.debug(f"    prices_df_filtered.columns: {list(prices_df_filtered.columns)}")
        logger.debug(f"    prices_df_filtered.shape: {prices_df_filtered.shape}")
    else:
        prices_df_filtered = prices_df
        logger.debug(f"  ⚠️ No se pudieron filtrar columnas, usando DataFrame completo")
    
    portfolio = Portfolio(name="Mi Cartera", symbols=symbols, weights=weights)
    logger.debug(f"  Portfolio creado con {len(symbols)} símbolos: {symbols}")
    logger.debug(f"  A punto de llamar set_prices con DataFrame shape: {prices_df_filtered.shape}")
    portfolio.set_prices(prices_df_filtered)
    
    logger.info(f"✅ Portfolio creado exitosamente con {len(symbols)} activos")
    
    # Retornar datos serializables para recrear el portfolio
    return tuple(symbols), tuple(weights), prices_df_filtered.to_dict()


def _create_portfolio_from_data():
    """Wrapper para crear portfolio usando cache."""
    # Verificar si la última simulación fue de un activo individual
    sim_type = st.session_state.get("montecarlo_sim_type")
    individual_symbol = st.session_state.get("montecarlo_symbol")
    
    if sim_type == "individual" and individual_symbol:
        # Usar el activo individual simulado
        logger.info(f"📊 Generando reporte para activo individual: {individual_symbol}")
        portfolio_symbols = [individual_symbol]
        portfolio_weights = [1.0]
    else:
        # Usar la cartera configurada
        portfolio_symbols = st.session_state.get("portfolio_symbols", [])
        portfolio_weights = st.session_state.get("portfolio_weights", [])
    
    data_map = st.session_state.get("last_data_map", {})
    
    # Crear hash único que incluya los símbolos del portfolio para invalidar cache
    data_map_hash = str(hash(str(sorted(data_map.keys())) + str(portfolio_symbols)))
    
    logger.debug(f"📋 _create_portfolio_from_data:")
    logger.debug(f"  portfolio_symbols: {portfolio_symbols}")
    logger.debug(f"  portfolio_weights: {portfolio_weights}")
    logger.debug(f"  data_map keys: {list(data_map.keys())}")
    logger.debug(f"  cache hash: {data_map_hash}")
    
    symbols_tuple, weights_tuple, prices_dict = _create_portfolio_from_data_cached(
        tuple(portfolio_symbols),
        tuple(portfolio_weights),
        data_map_hash
    )
    
    if symbols_tuple is None:
        st.error("No se pudieron extraer precios de los datos.")
        return None
    
    # Recrear portfolio desde datos cacheados (ya filtrados en la función cacheada)
    from simulation import Portfolio
    name = f"Activo: {individual_symbol}" if sim_type == "individual" else "Mi Cartera"
    
    logger.debug(f"📋 Recreando portfolio desde caché:")
    logger.debug(f"  symbols_tuple: {symbols_tuple}")
    logger.debug(f"  weights_tuple: {weights_tuple}")
    logger.debug(f"  prices_dict keys: {list(prices_dict.keys()) if isinstance(prices_dict, dict) else 'N/A'}")
    
    portfolio = Portfolio(name=name, symbols=list(symbols_tuple), weights=list(weights_tuple))
    
    # Asegurar que prices_dict solo tenga las columnas del portfolio
    prices_df_from_cache = pd.DataFrame(prices_dict)
    logger.debug(f"  prices_df_from_cache.columns: {list(prices_df_from_cache.columns)}")
    logger.debug(f"  prices_df_from_cache.shape: {prices_df_from_cache.shape}")
    
    # Filtrar solo las columnas que corresponden a los símbolos del portfolio
    portfolio_symbols_list = list(symbols_tuple)
    if set(portfolio_symbols_list) != set(prices_df_from_cache.columns):
        logger.debug(f"  ⚠️ Mismatch entre símbolos del portfolio y columnas del DataFrame")
        logger.debug(f"     Portfolio symbols: {portfolio_symbols_list}")
        logger.debug(f"     DataFrame columns: {list(prices_df_from_cache.columns)}")
        prices_df_final = prices_df_from_cache[portfolio_symbols_list]
        logger.debug(f"  Filtrado aplicado, shape final: {prices_df_final.shape}")
    else:
        prices_df_final = prices_df_from_cache
        logger.debug(f"  No es necesario filtrar, símbolos coinciden")
    
    portfolio.set_prices(prices_df_final)
    
    return portfolio


def tab_reporte(submit: bool, params: ReporteParams | None) -> None:
    """Contenido central de la pestaña 📋 Reporte."""
    st.subheader("📋 Reporte de Análisis")
    
    if not _check_prerequisites():
        return
    
    if submit and params is not None:
        try:
            # Limpiar reporte anterior antes de generar uno nuevo
            if "reporte_portfolio" in st.session_state:
                logger.debug("Limpiando reporte anterior antes de generar nuevo")
                del st.session_state["reporte_portfolio"]
            
            # Verificar si es simulación individual
            sim_type = st.session_state.get("montecarlo_sim_type")
            individual_symbol = st.session_state.get("montecarlo_symbol")
            
            if sim_type == "individual" and individual_symbol:
                spinner_text = f"📊 Generando reporte para {individual_symbol}..."
            else:
                spinner_text = "📊 Generando reporte completo de la cartera..."
            
            with st.spinner(spinner_text):
                portfolio = _create_portfolio_from_data()
                if portfolio:
                    st.session_state["reporte_portfolio"] = portfolio
                    
                    if sim_type == "individual" and individual_symbol:
                        st.success(f"✅ **Reporte generado exitosamente** para el activo **{individual_symbol}**")
                    else:
                        num_symbols = len(portfolio.symbols)
                        st.success(f"✅ **Reporte generado exitosamente** para cartera con {num_symbols} activo(s)")
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    if "reporte_portfolio" in st.session_state:
        _show_portfolio_report(st.session_state["reporte_portfolio"])
    else:
        st.info("💡 Configura los parámetros del reporte en el panel lateral y pulsa el botón **'📄 Generar reporte'** situado al final del panel lateral (haz scroll si es necesario).")


def _show_portfolio_report(portfolio: Any) -> None:
    """
    Muestra el reporte completo de la cartera.
    
    Args:
        portfolio: Objeto Portfolio con los datos de la cartera
    """
    logger.info("📊 Generando reporte de cartera")
    
    # Log de estadísticas antes de generar reporte
    try:
        stats = portfolio.get_statistics()
        logger.debug("  Estadísticas de cartera:")
        logger.debug(f"    Retorno: {stats['return']:.6f} (diario), {stats['return']*252:.4%} (anualizado)")
        logger.debug(f"    Volatilidad: {stats['volatility']:.4%}")
        logger.debug(f"    Sharpe Ratio: {stats['sharpe_ratio']:.4f}")
        logger.debug(f"    Número de activos: {stats['num_assets']}")
    except Exception as e:
        logger.warning(f"Error obteniendo estadísticas: {e}")
    
    from reporting import MonteCarloReporter
    
    # Usar el generador de reportes del módulo reporting
    MonteCarloReporter.show_portfolio_report(portfolio)
    
    logger.info("✅ Reporte generado y mostrado")

