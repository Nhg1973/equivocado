import pandas as pd
from collections import defaultdict
from config import TIMEFRAMES

# Diccionario para almacenar los datos históricos por par y marco temporal
historical_data = defaultdict(lambda: defaultdict(pd.DataFrame))

def fetch_data(client, pair, timeframe='1m'):
    """Fetch and update historical OHLCV data from Binance."""
    try:
        # Definir el número de registros a mantener
        max_limit = TIMEFRAMES[timeframe]

        # Obtener nuevos datos desde la API
        new_data = client.fetch_ohlcv(pair, timeframe=timeframe)

        # Convertir los nuevos datos a un DataFrame
        new_df = pd.DataFrame(new_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
        new_df.set_index('timestamp', inplace=True)

        # Actualizar los datos históricos almacenados
        if not historical_data[pair][timeframe].empty:
            historical_data[pair][timeframe] = pd.concat(
                [historical_data[pair][timeframe], new_df]
            ).drop_duplicates().sort_index()
        else:
            historical_data[pair][timeframe] = new_df

        # Mantener solo los datos más recientes hasta el máximo límite definido
        historical_data[pair][timeframe] = historical_data[pair][timeframe].iloc[-max_limit:]

        return historical_data[pair][timeframe]
    except Exception as e:
        print(f"Error fetching data for {pair} on timeframe {timeframe}: {e}")
        return None

def collect_data(client, pairs):
    """Collect data for all pairs and timeframes."""
    for pair in pairs:
        for timeframe in TIMEFRAMES:
            fetch_data(client, pair, timeframe)
    return historical_data
