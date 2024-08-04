
import os
from data_collector import collect_data
from analysis import generate_signals
from utils import get_binance_client
from config import API_KEY, API_SECRET, PAIRS, SLEEP_TIME_BETWEEN_PAIRS, SLEEP_TIME_BETWEEN_CYCLES
import time

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    client = get_binance_client(API_KEY, API_SECRET)

    try:
        while True:
            clear_screen()
            print("Recolección de datos en curso...")
            data = collect_data(client, PAIRS)
            print("Datos recolectados. Iniciando análisis...")

            signals = generate_signals(data)
            for pair, timeframe, trend_direction, rsi, bb_position, pattern, action, score in signals:
                if isinstance(score, (int, float)):
                    print(f"Par: {pair}")
                    print(f"Periodo: {timeframe}")
                    print(f"Tendencia: {trend_direction}")
                    print(f"RSI: {rsi:.2f}")
                    print(f"Posición en Bollinger Bands: {bb_position}")
                    print(f"Patrón de vela: {pattern}")
                    print(f"Análisis: {action}")
                    print(f"Puntuación: {score:.2f}")
                    print()
                else:
                    print(f"Par: {pair}")
                    print(f"Periodo: {timeframe}")
                    print(f"Tendencia: {trend_direction}")
                    print(f"RSI: {rsi}")
                    print(f"Posición en Bollinger Bands: {bb_position}")
                    print(f"Patrón de vela: {pattern}")
                    print(f"Análisis: {action}")
                    print(f"Puntuación: {score}")
                    print()

            print(f"Esperando {SLEEP_TIME_BETWEEN_CYCLES} segundos antes de la siguiente revisión...")
            time.sleep(SLEEP_TIME_BETWEEN_CYCLES)

    except KeyboardInterrupt:
        print("\nInterrupción detectada. Saliendo del programa...")
        print("Programa terminado correctamente. Adiós.")


if __name__ == "__main__":
    main()







