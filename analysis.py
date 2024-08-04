import datetime
import numpy as np
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import pandas as pd

def calculate_indicators(df):
    """Calculate Bollinger Bands, RSI, and SMA indicators."""
    bb_indicator = BollingerBands(df['close'])
    df['bb_lower'] = bb_indicator.bollinger_lband()
    df['bb_upper'] = bb_indicator.bollinger_hband()
    df['bb_middle'] = bb_indicator.bollinger_mavg()

    rsi_indicator = RSIIndicator(df['close'])
    df['rsi'] = rsi_indicator.rsi()

    sma_indicator = SMAIndicator(df['close'], window=15)
    df['sma'] = sma_indicator.sma_indicator()

    return df

def analyze_trends(data):
    """Analyze trends across multiple timeframes."""
    trends = {}
    for pair, timeframes in data.items():
        for timeframe, df in timeframes.items():
            df = calculate_indicators(df)
            last_close = df['close'].iloc[-1]
            last_sma = df['sma'].iloc[-1]
            trend_direction = 'Alcista' if last_close > last_sma else 'Bajista'
            trends[(pair, timeframe)] = {
                'trend': trend_direction,
                'last_close': last_close,
                'rsi': df['rsi'].iloc[-1],
                'bb_position': calculate_bb_position(df),
            }
    return trends

def calculate_bb_position(df):
    """Calculate position in Bollinger Bands."""
    last_close = df['close'].iloc[-1]
    lower_band = df['bb_lower'].iloc[-1]
    upper_band = df['bb_upper'].iloc[-1]
    middle_band = df['bb_middle'].iloc[-1]

    if last_close < lower_band:
        return 'Bajo el 1/4 inferior'
    elif lower_band <= last_close <= middle_band:
        return 'En el 2/4 inferior'
    elif middle_band < last_close <= upper_band:
        return 'En el 3/4 superior'
    else:
        return 'Sobre el 4/4 superior'

def analyze_candlestick_patterns(df):
    """Analyze candlestick patterns for buy/sell signals and calculate scores."""
    # Valores asignados a cada patrón
    pattern_scores = {
        'Doji': 0,  # Neutral
        'Hammer': 1,  # Alcista
        'Shooting Star': -1,  # Bajista
        'Bullish Engulfing': 1,  # Alcista
        'Bearish Engulfing': -1  # Bajista
    }

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
        pattern_count = {'Bullish': 0, 'Bearish': 0}
        for i in range(1, len(df)):
            candle = df.iloc[i]
            prev_candle = df.iloc[i - 1]
            
            if is_doji(candle):
                continue  # Neutral, no score
            elif is_hammer(candle):
                pattern_count['Bullish'] += 1
            elif is_shooting_star(candle):
                pattern_count['Bearish'] += 1
            elif is_bullish_engulfing(prev_candle, candle):
                pattern_count['Bullish'] += 1
            elif is_bearish_engulfing(prev_candle, candle):
                pattern_count['Bearish'] += 1
        
        return pattern_count

    pattern_count = detect_patterns()

    # Evaluar los patrones
    bullish_score = pattern_count['Bullish']
    bearish_score = pattern_count['Bearish']

    # Establecer señal basado en el puntaje
    if bullish_score > bearish_score:
        return 'Reversión Alcista'
    elif bearish_score > bullish_score:
        return 'Reversión Bajista'
    else:
        return 'Continuación o sin señal clara'
 
def assign_weights(trend_direction, bb_position, rsi, pattern):
    """Assign weights to each indicator."""
    weights = {'trend': 0, 'bb_position': 0, 'rsi': 0, 'pattern': 0}
    
    # Ponderaciones para tendencia
    if trend_direction == 'Alcista':
        weights['trend'] = 1
    elif trend_direction == 'Bajista':
        weights['trend'] = 0

    # Ponderaciones para posición en Bollinger Bands
    if bb_position == 'En el 1/4 inferior':
        weights['bb_position'] = 1
    elif bb_position == 'En el 2/4 inferior':
        weights['bb_position'] = 0.75
    elif bb_position == 'En el 3/4 superior':
        weights['bb_position'] = 0.5
    elif bb_position == 'Sobre el 4/4 superior':
        weights['bb_position'] = 0.25

    # Ponderaciones para RSI
    if rsi < 30:
        weights['rsi'] = 1
    elif rsi > 70:
        weights['rsi'] = 0
    else:
        weights['rsi'] = 0.5

    # Ponderaciones para patrones de velas
    if pattern == 'Reversión Alcista':
        weights['pattern'] = 1
    elif pattern == 'Reversión Bajista':
        weights['pattern'] = 0
    else:
        weights['pattern'] = 0.5

    return weights

def generate_signals(data):
    """Generate trading signals based on analyzed data."""
    signals = []
    trends = analyze_trends(data)
    
    # Inicializar el diccionario de puntuaciones con todos los posibles valores de acción
    all_scores = {'Comprar': [], 'Mantener o No Operar': [], 'Vender': []}

    for (pair, timeframe), trend_info in trends.items():
        df = data[pair][timeframe]
        pattern = analyze_candlestick_patterns(df)
        rsi = trend_info['rsi']
        bb_position = trend_info['bb_position']
        trend_direction = trend_info['trend']
        
        # Evaluar la puntuación de cada indicador
        score = 0
        
        if trend_direction == 'Alcista':
            score += 1
        elif trend_direction == 'Bajista':
            score -= 1
        
        if bb_position in ['En el 3/4 superior', 'Sobre el 4/4 superior']:
            score += 1
        elif bb_position in ['Bajo el 1/4 inferior', 'En el 2/4 inferior']:
            score -= 1
        
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1
        
        if pattern == 'Reversión Alcista':
            score += 1
        elif pattern == 'Reversión Bajista':
            score -= 1
        
        # Dividir la puntuación total por 4 para obtener el valor normalizado
        normalized_score = score / 4.0

        # Determinar la acción recomendada
        if normalized_score >= 0.5:
            action = 'Comprar'
        elif normalized_score <= -0.5:
            action = 'Vender'
        else:
            action = 'Mantener o No Operar'
        
        signals.append((pair, timeframe, trend_direction, rsi, bb_position, pattern, action, normalized_score))
        
        # Añadir la puntuación al análisis general
        all_scores[action].append(normalized_score)
    
    # Resumen del análisis general
    def analyze_overall_scores(scores):
        results = {}
        total_scores = {action: sum(score_list) for action, score_list in scores.items()}
        total_counts = {action: len(score_list) for action, score_list in scores.items()}
        
        for action in total_scores:
            if total_counts[action] > 0:
                avg_score = total_scores[action] / total_counts[action]
                results[action] = avg_score
            else:
                results[action] = 0
        return results

    overall_scores = analyze_overall_scores(all_scores)
    
    # Añadir análisis general al resultado
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    signals.append(('Resumen General', '', '', '', '', '', str(overall_scores), current_time))
    
    return signals
