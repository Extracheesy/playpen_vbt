from ohlcv import OhlcvPlus
import ccxt

client = ccxt.binance()
ohlcvp = OhlcvPlus(client, database_path='my_data.db')
ohlcv1 = ohlcvp.load(market='BTC/USDT', timeframe='1m', since='2023-01-01 00:00:00', limit=1000, update=True, verbose=True, workers=100)