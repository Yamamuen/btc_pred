# Bibliotecas Necessárias:
import requests
import datetime
import pandas as pd


def hourly_price_historical(cripto, moeda, limit, aggregate, exchange=''):
    """Essa função gera os preços históricos por HORA

    Args:
        cripto ([str]): Criptomoeda em sigla (ex: 'BTC')
        moeda ([str]): Moeda em sigla (ex: 'USD')
        limit ([int]): Limite de coleta
        aggregate ([type]): [description]
        exchange (str, optional): [description]. Defaults to ''.

    Returns:
        [type]: [description]
    """
    url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit={}&aggregate={}'\
            .format(cripto.upper(), moeda.upper(), limit, aggregate)
    if exchange:
        url += '&e={}'.format(exchange)
    page = requests.get(url)
    data = page.json()['Data']
    df = pd.DataFrame(data)
    df['timestamp'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
    return df

# Chamando a API com critérios:
incremento = 1 # de 1 em 1 hora
df = hourly_price_historical('BTC','USD', limit = 1000, aggregate = incremento) #Bitcoin em USD
df.head()
df.to_csv('cryptocompare.csv')
