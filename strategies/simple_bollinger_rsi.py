import pandas as pd
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

def fetch_data(client, pair, timeframe='1m', limit=100):
    """Fetch historical OHLCV data from Binance."""
    try:
        ohlcv = client.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_indicators(df):
    """Calculate Bollinger Bands, RSI, and SMA indicators."""
    # Bollinger Bands
    bb_indicator = BollingerBands(df['close'])
    df['bb_lower'] = bb_indicator.bollinger_lband()
    df['bb_upper'] = bb_indicator.bollinger_hband()
    df['bb_middle'] = bb_indicator.bollinger_mavg()

    # RSI
    rsi_indicator = RSIIndicator(df['close'])
    df['rsi'] = rsi_indicator.rsi()

    # SMA (Simple Moving Average) for trend analysis
    sma_indicator = SMAIndicator(df['close'], window=15)
    df['sma'] = sma_indicator.sma_indicator()

    return df

def analyze_trends(client, pair):
    """Analyze trends across multiple timeframes."""
    trends = {}
    timeframes = ['1m', '3m', '5m', '15m']
    
    for tf in timeframes:
        df_tf = fetch_data(client, pair, timeframe=tf)
        if df_tf is not None:
            df_tf = calculate_indicators(df_tf)
            last_close = df_tf['close'].iloc[-1]
            last_sma = df_tf['sma'].iloc[-1]
            trends[tf] = last_close > last_sma
    
    return trends

def analyze_candlestick_patterns(df):
    """Analyze candlestick patterns for buy/sell signals."""
    signals = []

    def is_doji(candle):
        return abs(candle['open'] - candle['close']) < 0.1 * (candle['high'] - candle['low'])

    def is_hammer(candle):
        body = abs(candle['open'] - candle['close'])
        candle_range = candle['high'] - candle['low']
        return body < 0.3 * candle_range and (candle['low'] + 0.1 * candle_range < candle['open'] < candle['low'] + 0.3 * candle_range)

    def is_shooting_star(candle):
        body = abs(candle['open'] - candle['close'])
        candle_range = candle['high'] - candle['low']
        return body < 0.3 * candle_range and (candle['high'] - 0.1 * candle_range > candle['close'] > candle['high'] - 0.3 * candle_range)
    
    def is_bullish_engulfing(candle1, candle2):
        return (candle2['open'] < candle2['close'] and 
                candle1['open'] > candle1['close'] and
                candle2['open'] < candle1['close'] and 
                candle2['close'] > candle1['open'])

    def is_bearish_engulfing(candle1, candle2):
        return (candle2['open'] > candle2['close'] and 
                candle1['open'] < candle1['close'] and
                candle2['open'] > candle1['close'] and 
                candle2['close'] < candle1['open'])
    
    def detect_patterns():
        for i in range(1, len(df)):
            candle = df.iloc[i]
            prev_candle = df.iloc[i - 1]
            
            if is_doji(candle):
                signals.append('Doji')
            elif is_hammer(candle):
                signals.append('Hammer')
            elif is_shooting_star(candle):
                signals.append('Shooting Star')
            elif is_bullish_engulfing(prev_candle, candle):
                signals.append('Bullish Engulfing')
            elif is_bearish_engulfing(prev_candle, candle):
                signals.append('Bearish Engulfing')
        
        return signals

    patterns = detect_patterns()

    # Evaluar los patrones
    bullish_patterns = {'Hammer', 'Bullish Engulfing'}
    bearish_patterns = {'Shooting Star', 'Bearish Engulfing'}
    
    if any(pattern in bullish_patterns for pattern in patterns):
        return 'Reversión Alcista'
    elif any(pattern in bearish_patterns for pattern in patterns):
        return 'Reversión Bajista'
    else:
        return 'Continuation or No Clear Signal'
    


def execute_trade(client, pair):
    print(f"Conectando a Binance para el par {pair}...")

    try:
        # Fetch and calculate indicators
        df = fetch_data(client, pair, timeframe='1m', limit=100)
        if df is None:
            return
        
        df = calculate_indicators(df)

        # Analyze trends across multiple timeframes
        trends = analyze_trends(client, pair)
        print("Tendencias en distintos marcos temporales:", trends)

        # Analyze candlestick patterns
        patterns = analyze_candlestick_patterns(df)
        print(f"Patrones de velas identificados: {patterns}")

        # Lógica de compra/venta
        last_close = df['close'].iloc[-1]
        last_rsi = df['rsi'].iloc[-1]
        last_bb_lower = df['bb_lower'].iloc[-1]
        
        if all(trends.values()) and last_close < last_bb_lower and last_rsi < 50 and patterns:
            print(f"Comprar {pair} a {last_close}")
            # Implementar orden de compra aquí
        else:
            print(f"No se cumplen las condiciones para comprar {pair}.")

    except Exception as e:
        print(f"Error al obtener datos o calcular indicadores: {e}")
