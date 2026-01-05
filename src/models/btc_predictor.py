"""
Advanced BTC/USDT Prediction Model
Modelo LSTM con mecanismo de atención para predicción de precios
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import json


class AttentionLayer(layers.Layer):
    """Capa de atención personalizada"""

    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], input_shape[-1]),
            initializer='glorot_uniform',
            trainable=True
        )
        self.b = self.add_weight(
            name='attention_bias',
            shape=(input_shape[-1],),
            initializer='zeros',
            trainable=True
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs):
        e = keras.activations.tanh(tf.matmul(inputs, self.W) + self.b)
        a = keras.activations.softmax(e, axis=1)
        output = inputs * a
        return tf.reduce_sum(output, axis=1)


class BTCPredictor:
    def __init__(self, sequence_length=48, prediction_horizon=6):
        """
        Inicializa el modelo de predicción

        Args:
            sequence_length: Longitud de la secuencia de entrada
            prediction_horizon: Horizonte de predicción (horas adelante)
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = MinMaxScaler()
        self.feature_columns = None
        self.history = None

    def build_model(self, input_shape):
        """
        Construye el modelo LSTM con atención

        Args:
            input_shape: Forma de entrada (sequence_length, num_features)

        Returns:
            Modelo compilado
        """
        inputs = layers.Input(shape=input_shape)

        # Primera capa LSTM bidireccional
        x = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True, dropout=0.2)
        )(inputs)
        x = layers.BatchNormalization()(x)

        # Segunda capa LSTM bidireccional
        x = layers.Bidirectional(
            layers.LSTM(64, return_sequences=True, dropout=0.2)
        )(x)
        x = layers.BatchNormalization()(x)

        # Capa de atención
        attention_output = AttentionLayer()(x)

        # Capas densas
        x = layers.Dense(64, activation='relu')(attention_output)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(32, activation='relu')(x)
        x = layers.Dropout(0.2)(x)

        # Salida - predecir múltiples horizontes
        outputs = layers.Dense(self.prediction_horizon)(x)

        model = Model(inputs=inputs, outputs=outputs)

        # Compilar con optimizador personalizado
        optimizer = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(
            optimizer=optimizer,
            loss='huber',
            metrics=['mae', 'mse']
        )

        return model

    def prepare_sequences(self, data, target_col='close'):
        """
        Prepara secuencias para entrenamiento

        Args:
            data: DataFrame con características
            target_col: Columna objetivo

        Returns:
            X, y: Arrays de entrada y salida
        """
        X, y = [], []

        for i in range(len(data) - self.sequence_length - self.prediction_horizon):
            X.append(data.iloc[i:i + self.sequence_length].values)
            # Predecir múltiples puntos futuros
            future_prices = data[target_col].iloc[
                i + self.sequence_length:i + self.sequence_length + self.prediction_horizon
            ].values
            y.append(future_prices)

        return np.array(X), np.array(y)

    def train(self, df, validation_split=0.2, epochs=100, batch_size=32):
        """
        Entrena el modelo

        Args:
            df: DataFrame con características
            validation_split: Proporción de datos para validación
            epochs: Número de épocas
            batch_size: Tamaño del batch

        Returns:
            Historia del entrenamiento
        """
        # Guardar columnas de características
        self.feature_columns = df.columns.tolist()

        # Preparar datos
        print("Preparing sequences...")
        X, y = self.prepare_sequences(df)

        print(f"X shape: {X.shape}, y shape: {y.shape}")

        # Split train/validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # Escalar datos
        print("Scaling data...")
        X_train_reshaped = X_train.reshape(-1, X_train.shape[-1])
        self.scaler_X.fit(X_train_reshaped)
        X_train_scaled = self.scaler_X.transform(X_train_reshaped).reshape(X_train.shape)
        X_val_scaled = self.scaler_X.transform(
            X_val.reshape(-1, X_val.shape[-1])
        ).reshape(X_val.shape)

        self.scaler_y.fit(y_train)
        y_train_scaled = self.scaler_y.transform(y_train)
        y_val_scaled = self.scaler_y.transform(y_val)

        # Construir modelo
        print("Building model...")
        self.model = self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        print(self.model.summary())

        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                'models/best_model.h5',
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]

        # Entrenar
        print("Training model...")
        self.history = self.model.fit(
            X_train_scaled, y_train_scaled,
            validation_data=(X_val_scaled, y_val_scaled),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )

        return self.history

    def predict(self, data):
        """
        Hace predicción

        Args:
            data: DataFrame con las últimas sequence_length filas

        Returns:
            Array con predicciones
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        # Preparar datos
        if len(data) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} rows of data")

        # Tomar últimas sequence_length filas
        X = data.tail(self.sequence_length)[self.feature_columns].values
        X = X.reshape(1, self.sequence_length, -1)

        # Escalar
        X_scaled = self.scaler_X.transform(
            X.reshape(-1, X.shape[-1])
        ).reshape(X.shape)

        # Predecir
        y_pred_scaled = self.model.predict(X_scaled, verbose=0)

        # Des-escalar
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)

        return y_pred[0]

    def evaluate(self, df):
        """
        Evalúa el modelo

        Args:
            df: DataFrame de test

        Returns:
            Métricas de evaluación
        """
        X, y = self.prepare_sequences(df)

        X_scaled = self.scaler_X.transform(
            X.reshape(-1, X.shape[-1])
        ).reshape(X.shape)
        y_scaled = self.scaler_y.transform(y)

        results = self.model.evaluate(X_scaled, y_scaled, verbose=0)

        metrics = {
            'loss': results[0],
            'mae': results[1],
            'mse': results[2]
        }

        # Calcular MAPE
        y_pred_scaled = self.model.predict(X_scaled, verbose=0)
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)

        mape = np.mean(np.abs((y - y_pred) / y)) * 100
        metrics['mape'] = mape

        return metrics

    def save(self, model_path='models/btc_predictor'):
        """Guarda el modelo y los scalers"""
        os.makedirs('models', exist_ok=True)

        # Guardar modelo
        self.model.save(f'{model_path}_model.h5')

        # Guardar scalers y configuración
        config = {
            'sequence_length': self.sequence_length,
            'prediction_horizon': self.prediction_horizon,
            'feature_columns': self.feature_columns
        }

        joblib.dump(self.scaler_X, f'{model_path}_scaler_X.pkl')
        joblib.dump(self.scaler_y, f'{model_path}_scaler_y.pkl')
        with open(f'{model_path}_config.json', 'w') as f:
            json.dump(config, f)

        print(f"Model saved to {model_path}")

    def load(self, model_path='models/btc_predictor'):
        """Carga el modelo y los scalers"""
        # Cargar configuración
        with open(f'{model_path}_config.json', 'r') as f:
            config = json.load(f)

        self.sequence_length = config['sequence_length']
        self.prediction_horizon = config['prediction_horizon']
        self.feature_columns = config['feature_columns']

        # Cargar modelo
        self.model = keras.models.load_model(
            f'{model_path}_model.h5',
            custom_objects={'AttentionLayer': AttentionLayer}
        )

        # Cargar scalers
        self.scaler_X = joblib.load(f'{model_path}_scaler_X.pkl')
        self.scaler_y = joblib.load(f'{model_path}_scaler_y.pkl')

        print(f"Model loaded from {model_path}")


if __name__ == "__main__":
    # Test the model
    if os.path.exists('data/processed/btc_usdt_features.csv'):
        print("Loading data...")
        df = pd.read_csv(
            'data/processed/btc_usdt_features.csv',
            index_col='timestamp',
            parse_dates=True
        )

        print(f"Data shape: {df.shape}")

        # Crear y entrenar modelo
        predictor = BTCPredictor(sequence_length=48, prediction_horizon=6)

        # Entrenar con los primeros 80% de datos
        train_size = int(len(df) * 0.8)
        df_train = df.iloc[:train_size]

        predictor.train(df_train, epochs=50, batch_size=32)

        # Evaluar con los últimos 20%
        df_test = df.iloc[train_size:]
        metrics = predictor.evaluate(df_test)

        print(f"\nTest Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value:.4f}")

        # Guardar modelo
        predictor.save()

        # Hacer una predicción de ejemplo
        print("\nMaking sample prediction...")
        predictions = predictor.predict(df)
        print(f"Predictions for next {predictor.prediction_horizon} hours:")
        print(predictions)
    else:
        print("No processed data found. Run data_collector.py and feature_engineering.py first.")
