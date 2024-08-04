import ccxt

def get_binance_client(api_key, api_secret):
    """Crea y devuelve un cliente de Binance utilizando ccxt."""
    return ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True,
        },
        'proxies': {
            'http': 'http://www-proxy.mrec.ar:8080',
            'https': 'http://www-proxy.mrec.ar:8080',
        }
    })

