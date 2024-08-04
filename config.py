API_KEY ="XolZH0sgMhMFb5sm7TtTglDwu3TgsrLLW0YSrxLGRd7CnetwGsaP3kMuhnTKeFeV"
API_SECRET ="EijlyRietMq5wy2srxevwGbg4R3Jnjtorr3RPYNPkzzMbv4hYGnJwzO1gNxjxEee"

# Pares de criptomonedas a monitorear
PAIRS = ['BOME/USDT']

# Períodos de tiempo a analizar
TIMEFRAMES = {
    '1m': 100,   # 100 registros para el marco temporal de 1 minuto
    '3m': 80,    # 80 registros para el marco temporal de 3 minutos
    '5m': 60,    # 60 registros para el marco temporal de 5 minutos
    '15m': 40    # 40 registros para el marco temporal de 15 minutos
}

# Otros parámetros de configuración
SLEEP_TIME_BETWEEN_PAIRS = 5   # Tiempo de espera entre cada par en segundos
SLEEP_TIME_BETWEEN_CYCLES = 30 # Tiempo de espera entre cada ciclo completo en segundos
