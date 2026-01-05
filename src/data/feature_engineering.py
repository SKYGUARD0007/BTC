"""
Feature Engineering for BTC/USDT Prediction
Crea características técnicas avanzadas para el modelo
"""
import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice


class FeatureEngineer:
    def __init__(self):
        """Inicializa el ingeniero de características"""
        pass

    def add_technical_indicators(self, df):
        """
        Agrega indicadores técnicos al DataFrame

        Args:
            df: DataFrame con columnas OHLCV

        Returns:
            DataFrame con indicadores técnicos agregados
        """
        df = df.copy()

        # Moving Averages
        for period in [7, 14, 21, 50, 100, 200]:
            df[f'sma_{period}'] = SMAIndicator(
                close=df['close'], window=period
            ).sma_indicator()
            df[f'ema_{period}'] = EMAIndicator(
                close=df['close'], window=period
            ).ema_indicator()

        # RSI
        for period in [6, 12, 14, 24]:
            df[f'rsi_{period}'] = RSIIndicator(
                close=df['close'], window=period
            ).rsi()

        # MACD
        macd = MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()

        # Bollinger Bands
        for period in [20, 50]:
            bb = BollingerBands(close=df['close'], window=period)
            df[f'bb_high_{period}'] = bb.bollinger_hband()
            df[f'bb_mid_{period}'] = bb.bollinger_mavg()
            df[f'bb_low_{period}'] = bb.bollinger_lband()
            df[f'bb_width_{period}'] = bb.bollinger_wband()
            df[f'bb_pband_{period}'] = bb.bollinger_pband()

        # ATR (Average True Range)
        for period in [14, 21]:
            df[f'atr_{period}'] = AverageTrueRange(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=period
            ).average_true_range()

        # Stochastic Oscillator
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        # ADX (Average Directional Index)
        adx = ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()

        # OBV (On Balance Volume)
        df['obv'] = OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()

        # VWAP
        df['vwap'] = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        ).volume_weighted_average_price()

        return df

    def add_price_features(self, df):
        """
        Agrega características basadas en precio

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            DataFrame con características de precio
        """
        df = df.copy()

        # Returns
        for period in [1, 3, 6, 12, 24]:
            df[f'return_{period}'] = df['close'].pct_change(period)

        # Log returns
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))

        # Price ranges
        df['high_low_range'] = df['high'] - df['low']
        df['close_open_range'] = df['close'] - df['open']

        # Price position within range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)

        # Volume features
        df['volume_change'] = df['volume'].pct_change()
        df['volume_ma_7'] = df['volume'].rolling(window=7).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_ma_7'] + 1e-10)

        # Volatility
        for period in [7, 14, 30]:
            df[f'volatility_{period}'] = df['return_1'].rolling(window=period).std()

        # Price momentum
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = df['close'] - df['close'].shift(period)

        return df

    def add_time_features(self, df):
        """
        Agrega características temporales

        Args:
            df: DataFrame con índice de tiempo

        Returns:
            DataFrame con características temporales
        """
        df = df.copy()

        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter

        # Cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

        return df

    def add_lagged_features(self, df, lags=[1, 2, 3, 6, 12, 24]):
        """
        Agrega características con lag

        Args:
            df: DataFrame
            lags: Lista de lags a aplicar

        Returns:
            DataFrame con características lagged
        """
        df = df.copy()

        important_features = ['close', 'volume', 'rsi_14', 'macd', 'volatility_7']

        for feature in important_features:
            if feature in df.columns:
                for lag in lags:
                    df[f'{feature}_lag_{lag}'] = df[feature].shift(lag)

        return df

    def create_all_features(self, df):
        """
        Crea todas las características

        Args:
            df: DataFrame con datos OHLCV

        Returns:
            DataFrame con todas las características
        """
        print("Adding technical indicators...")
        df = self.add_technical_indicators(df)

        print("Adding price features...")
        df = self.add_price_features(df)

        print("Adding time features...")
        df = self.add_time_features(df)

        print("Adding lagged features...")
        df = self.add_lagged_features(df)

        # Remove NaN values
        initial_rows = len(df)
        df = df.dropna()
        removed_rows = initial_rows - len(df)
        print(f"Removed {removed_rows} rows with NaN values")

        print(f"Total features created: {len(df.columns)}")

        return df


if __name__ == "__main__":
    # Test feature engineering
    import os

    # Load sample data
    if os.path.exists('data/raw/btc_usdt_1h.csv'):
        df = pd.read_csv('data/raw/btc_usdt_1h.csv', index_col='timestamp', parse_dates=True)

        print(f"Original data shape: {df.shape}")

        # Create features
        fe = FeatureEngineer()
        df_features = fe.create_all_features(df)

        print(f"Data with features shape: {df_features.shape}")
        print(f"\nFeatures:\n{df_features.columns.tolist()}")

        # Save processed data
        os.makedirs('data/processed', exist_ok=True)
        df_features.to_csv('data/processed/btc_usdt_features.csv')
        print("\nProcessed data saved to data/processed/btc_usdt_features.csv")
    else:
        print("No data found. Run data_collector.py first.")
