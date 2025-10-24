import pandas as pd

# Crear DataFrame con símbolos
data = {
    'symbol': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC'],
    'company': ['Apple Inc.', 'Microsoft Corporation', 'Alphabet Inc.', 'Tesla Inc.', 
                'Amazon.com Inc.', 'NVIDIA Corporation', 'Meta Platforms Inc.', 
                'Netflix Inc.', 'Advanced Micro Devices', 'Intel Corporation'],
    'sector': ['Technology', 'Technology', 'Technology', 'Automotive', 'Technology',
               'Technology', 'Technology', 'Technology', 'Technology', 'Technology'],
    'price': [150.00, 300.00, 2500.00, 800.00, 3000.00, 400.00, 200.00, 400.00, 100.00, 50.00]
}

df = pd.DataFrame(data)

# Guardar como Excel
df.to_excel('ejemplos/symbols.xlsx', index=False)
print("Archivo Excel creado: ejemplos/symbols.xlsx")
