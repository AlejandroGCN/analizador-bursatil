# Dockerfile para Analizador Bursátil
FROM python:3.12-slim

# Metadatos
LABEL maintainer="Alejandro García-Caro Nombela <alex_garci_17@gmail.com>"
LABEL description="Analizador bursátil con simulación Monte Carlo"
LABEL version="0.1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar el código fuente completo primero
COPY . .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .[dev]

# Exponer el puerto de Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "src/ui/dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
