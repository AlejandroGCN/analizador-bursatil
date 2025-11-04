# 🔑 Configuración de API Keys

Guía para configurar las claves de API necesarias para acceder a diferentes fuentes de datos financieros.

---

## Resumen de Fuentes

| Fuente | Requiere API Key | Dificultad | Registro |
|--------|-----------------|------------|----------|
| **Yahoo Finance** | No | - | No |
| **Binance** | No | - | No |
| **Tiingo** | Sí (gratuita) | Fácil | [tiingo.com](https://www.tiingo.com) |

---

## Configuración de Tiingo

### 1. Obtener API Key

1. Crear cuenta en [tiingo.com](https://www.tiingo.com/)
2. Acceder a [https://www.tiingo.com/account/api/token](https://www.tiingo.com/account/api/token)
3. Copiar el API Token (40 caracteres alfanuméricos)

### 2. Configurar Localmente

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

Editar el archivo `.env` y reemplazar `tu_api_key_aqui` con tu token:

```bash
TIINGO_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 3. Verificar Configuración

Ejecutar la aplicación:
```bash
python run_app.py
```

Debe aparecer el mensaje:
```
✓ API key de Tiingo cargada desde .env
```

---

## Características por Fuente

### Yahoo Finance
- **Cobertura:** Global (acciones, índices, ETFs, fondos)
- **Datos históricos:** 
  - Intervalos intraday (1m, 5m, 15m, 30m): Solo **7 días**
  - Intervalo horario (1h): Solo **60 días**
  - Intervalos diarios (1d, 1wk, 1mo): Hasta **50+ años**
- **Intervalos disponibles:** 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
- **Límites:** Sin límites estrictos (uso razonable)
- **Nota:** Los intervalos de minutos están limitados por Yahoo para trading reciente

### Binance
- **Cobertura:** Criptomonedas
- **Datos históricos:** Según disponibilidad del exchange
- **Intervalos:** 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
- **Límites:** 1200 requests/minuto

### Tiingo
- **Cobertura:** Global (70+ exchanges)
- **Datos históricos:** Hasta 30+ años
- **Intervalos:** Solo 1d (EOD) en plan gratuito
- **Límites Free Tier:**
  - 1000 símbolos únicos/día
  - 500 requests/hora
  - Datos end-of-day únicamente
- **Ventajas:** Calidad institucional, datos ajustados por splits/dividendos

---

## Uso en Código

### Con DataExtractor

```python
from data_extractor import DataExtractor
from data_extractor.config import ExtractorConfig

# Yahoo Finance (sin configuración)
config = ExtractorConfig(source="yahoo")
extractor = DataExtractor(config)

# Binance (sin configuración)
config = ExtractorConfig(source="binance")
extractor = DataExtractor(config)

# Tiingo (lee API key de .env automáticamente)
config = ExtractorConfig(source="tiingo")
extractor = DataExtractor(config)

# Descargar datos
data = extractor.get_market_data(
    ['AAPL', 'MSFT'], 
    start='2023-01-01', 
    end='2024-01-01'
)
```

### Con Adapter Directo

```python
from data_extractor.adapters.tiingo_adapter import TiingoAdapter

# Lee TIINGO_API_KEY del ambiente
adapter = TiingoAdapter()
df = adapter.download_symbol('AAPL', '2023-01-01', '2024-01-01')
```

---

## Solución de Problemas

### Error: "API key de Tiingo requerida"
- Verificar que existe el archivo `.env` en la raíz del proyecto
- Confirmar que contiene la línea: `TIINGO_API_KEY=tu_token`
- Reiniciar la aplicación

### Error: "API key de Tiingo inválida"
- Verificar que el token es correcto (40 caracteres)
- Confirmar que no hay espacios antes/después del token
- Regenerar token en [tiingo.com/account/api/token](https://www.tiingo.com/account/api/token)

### Warning: "Archivo .env no encontrado"
- Copiar `.env.example` a `.env`
- Asegurarse de estar en la raíz del proyecto

### Python-dotenv no instalado
```bash
pip install python-dotenv
```

---

## Notas para Colaboradores

- El archivo `.env` contiene credenciales privadas y está excluido del control de versiones
- Cada desarrollador debe crear su propio archivo `.env` a partir de `.env.example`
- Nunca commitear archivos `.env` al repositorio
- El archivo `.env.example` sirve como plantilla y debe mantenerse actualizado

---

## Referencias

- [Documentación de Tiingo](https://www.tiingo.com/documentation)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [README Principal](README.md)
- [Guía de Inicio Rápido](QUICKSTART.md)
