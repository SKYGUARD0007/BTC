"""
Data Collector for BTC/USDT
Recopila datos históricos y en tiempo real de múltiples exchanges
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os


class BTCDataCollector:
    def __init__(self, symbol='BTC/USDT', exchange='binance'):
        """
        Inicializa el recopilador de datos

        Args:
            symbol: Par de trading (default: BTC/USDT)
            exchange: Exchange a usar (default: binance)
        """
        self.symbol = symbol
        self.exchange_name = exchange
        self.exchange = getattr(ccxt, exchange)({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def fetch_ohlcv(self, timeframe='1h', limit=1000, since=None):
        """
        Obtiene datos OHLCV históricos

        Args:
            timeframe: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número de velas a obtener
            since: Timestamp desde cuando obtener datos

        Returns:
            DataFrame con datos OHLCV
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol,
                timeframe=timeframe,
                limit=limit,
                since=since
            )

            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            print(f"Error fetching OHLCV data: {e}")
            return None

    def fetch_historical_data(self, timeframe='1h', days=365):
        """
        Obtiene datos históricos completos

        Args:
            timeframe: Intervalo de tiempo
            days: Número de días históricos

        Returns:
            DataFrame con datos históricos completos
        """
        all_data = []
        since = self.exchange.parse8601(
            (datetime.now() - timedelta(days=days)).isoformat()
        )

        print(f"Fetching {days} days of {timeframe} data...")

        while True:
            try:
                ohlcv = self.exchange.fetch_ohlcv(
                    self.symbol,
                    timeframe=timeframe,
                    limit=1000,
                    since=since
                )

                if not ohlcv:
                    break

                all_data.extend(ohlcv)
                since = ohlcv[-1][0] + 1

                # Check if we've reached the present
                if since >= self.exchange.milliseconds():
                    break

                print(f"Fetched {len(all_data)} candles...")
                time.sleep(self.exchange.rateLimit / 1000)

            except Exception as e:
                print(f"Error: {e}")
                break

        df = pd.DataFrame(
            all_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[~df.index.duplicated(keep='first')]

        print(f"Total candles fetched: {len(df)}")
        return df

    def get_current_price(self):
        """
        Obtiene el precio actual de BTC/USDT

        Returns:
            float: Precio actual
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None

    def get_order_book(self, limit=20):
        """
        Obtiene el order book actual

        Args:
            limit: Profundidad del order book

        Returns:
            dict: Order book con bids y asks
        """
        try:
            order_book = self.exchange.fetch_order_book(self.symbol, limit=limit)
            return order_book
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None

    def save_data(self, df, filename):
        """
        Guarda datos en archivo CSV

        Args:
            df: DataFrame a guardar
            filename: Nombre del archivo
        """
        os.makedirs('data/raw', exist_ok=True)
        filepath = f'data/raw/{filename}'
        df.to_csv(filepath)
        print(f"Data saved to {filepath}")
        return filepath


if __name__ == "__main__":
    # Test the data collector
    collector = BTCDataCollector()

    # Fetch 90 days of hourly data
    df = collector.fetch_historical_data(timeframe='1h', days=90)

    if df is not None:
        print(f"\nData shape: {df.shape}")
        print(f"\nFirst rows:\n{df.head()}")
        print(f"\nLast rows:\n{df.tail()}")

        # Save data
        collector.save_data(df, 'btc_usdt_1h.csv')

        # Get current price
        current_price = collector.get_current_price()
        print(f"\nCurrent BTC/USDT price: ${current_price:,.2f}")
