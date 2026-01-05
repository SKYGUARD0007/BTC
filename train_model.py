#!/usr/bin/env python3
"""
Script de entrenamiento completo del modelo BTC/USDT
Ejecuta todo el pipeline: recopilación de datos, feature engineering y entrenamiento
"""
import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.append('src')

from data.data_collector import BTCDataCollector
from data.feature_engineering import FeatureEngineer
from models.btc_predictor import BTCPredictor


def main(args):
    """
    Ejecuta el pipeline completo de entrenamiento

    Args:
        args: Argumentos de línea de comandos
    """
    print("=" * 70)
    print("🚀 ENTRENAMIENTO DEL MODELO DE PREDICCIÓN BTC/USDT")
    print("=" * 70)

    # Paso 1: Recopilar datos
    print(f"\n{'='*70}")
    print("📊 PASO 1: Recopilando datos históricos")
    print("=" * 70)

    collector = BTCDataCollector()
    df_raw = collector.fetch_historical_data(
        timeframe=args.timeframe,
        days=args.days
    )

    if df_raw is None or len(df_raw) == 0:
        print("❌ Error: No se pudieron obtener datos")
        return False

    print(f"\n✅ Datos recopilados: {len(df_raw)} velas")
    print(f"Rango: {df_raw.index[0]} a {df_raw.index[-1]}")

    # Guardar datos crudos
    filepath_raw = collector.save_data(df_raw, f'btc_usdt_{args.timeframe}.csv')

    # Paso 2: Feature Engineering
    print(f"\n{'='*70}")
    print("🔧 PASO 2: Ingeniería de características")
    print("=" * 70)

    fe = FeatureEngineer()
    df_features = fe.create_all_features(df_raw)

    print(f"\n✅ Características creadas: {len(df_features.columns)} features")
    print(f"Datos procesados: {len(df_features)} filas")

    # Guardar datos procesados
    os.makedirs('data/processed', exist_ok=True)
    filepath_processed = 'data/processed/btc_usdt_features.csv'
    df_features.to_csv(filepath_processed)
    print(f"Datos guardados en: {filepath_processed}")

    # Paso 3: Entrenar modelo
    print(f"\n{'='*70}")
    print("🤖 PASO 3: Entrenando modelo de predicción")
    print("=" * 70)

    predictor = BTCPredictor(
        sequence_length=args.sequence_length,
        prediction_horizon=args.prediction_horizon
    )

    # Usar el 85% de datos para entrenamiento
    train_size = int(len(df_features) * 0.85)
    df_train = df_features.iloc[:train_size]
    df_test = df_features.iloc[train_size:]

    print(f"\nDatos de entrenamiento: {len(df_train)}")
    print(f"Datos de validación: {len(df_test)}")

    # Entrenar
    history = predictor.train(
        df_train,
        validation_split=args.validation_split,
        epochs=args.epochs,
        batch_size=args.batch_size
    )

    # Paso 4: Evaluar modelo
    print(f"\n{'='*70}")
    print("📈 PASO 4: Evaluando modelo")
    print("=" * 70)

    metrics = predictor.evaluate(df_test)

    print("\n📊 MÉTRICAS EN CONJUNTO DE TEST:")
    print(f"  Loss: {metrics['loss']:.4f}")
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  MSE: {metrics['mse']:.4f}")
    print(f"  MAPE: {metrics['mape']:.2f}%")

    # Paso 5: Guardar modelo
    print(f"\n{'='*70}")
    print("💾 PASO 5: Guardando modelo")
    print("=" * 70)

    predictor.save('models/btc_predictor')

    # Hacer predicción de ejemplo
    print(f"\n{'='*70}")
    print("🔮 PREDICCIÓN DE EJEMPLO")
    print("=" * 70)

    current_price = df_features['close'].iloc[-1]
    predictions = predictor.predict(df_features)

    print(f"\nPrecio actual: ${current_price:,.2f}")
    print(f"\nPredicciones para las próximas {args.prediction_horizon} horas:")

    for i, pred in enumerate(predictions, 1):
        change = (pred - current_price) / current_price * 100
        print(f"  {i}h: ${pred:,.2f} ({change:+.2f}%)")

    # Resumen final
    print(f"\n{'='*70}")
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"\n📁 Archivos generados:")
    print(f"  - Datos crudos: {filepath_raw}")
    print(f"  - Datos procesados: {filepath_processed}")
    print(f"  - Modelo: models/btc_predictor_model.h5")
    print(f"  - Scalers: models/btc_predictor_scaler_*.pkl")
    print(f"  - Config: models/btc_predictor_config.json")

    print(f"\n🚀 Para usar el chat interactivo, ejecuta:")
    print(f"  python run_chat.py")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Entrena el modelo de predicción BTC/USDT'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=180,
        help='Días de datos históricos a recopilar (default: 180)'
    )

    parser.add_argument(
        '--timeframe',
        type=str,
        default='1h',
        help='Intervalo de tiempo (1h, 4h, 1d) (default: 1h)'
    )

    parser.add_argument(
        '--sequence-length',
        type=int,
        default=48,
        help='Longitud de secuencia para el modelo (default: 48)'
    )

    parser.add_argument(
        '--prediction-horizon',
        type=int,
        default=6,
        help='Horizonte de predicción en horas (default: 6)'
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        help='Número de épocas de entrenamiento (default: 100)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Tamaño del batch (default: 32)'
    )

    parser.add_argument(
        '--validation-split',
        type=float,
        default=0.2,
        help='Proporción de datos para validación (default: 0.2)'
    )

    args = parser.parse_args()

    success = main(args)
    sys.exit(0 if success else 1)
