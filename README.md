# 🚀 BTC/USDT Professional AI Trading System

Sistema profesional de predicción y trading de Bitcoin con Deep Learning (LSTM + Atención), gestión avanzada de riesgo e interfaz de chat interactiva para operaciones en tiempo real.

## 📋 Características Principales

### 🤖 Modelo de IA de Producción
- **LSTM Bidireccional con Atención**: Arquitectura avanzada de Deep Learning
- **Predicciones Multi-Horizonte**: Hasta 24 horas adelante configurables
- **Alta Precisión**: Entrenado con más de 100 indicadores técnicos
- **Actualización Continua**: Reentrenamiento automático con datos recientes

### 💼 Gestión de Riesgo Profesional
- **Position Sizing Automático**: Cálculo basado en volatilidad y confianza
- **Stop Loss Dinámico**: Ajustado a ATR y volatilidad del mercado
- **Take Profit Multi-Nivel**: 3 niveles con ratios risk/reward optimizados
- **Límites de Drawdown**: Protección automática del capital
- **Gestión de Capital**: Control de riesgo por trade y diario

### 📊 Análisis Técnico Completo
- **100+ Indicadores**: RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, OBV, VWAP
- **Análisis de Tendencia**: Identificación automática de tendencias
- **Momentum y Volatilidad**: Evaluación en tiempo real
- **Volumen y Liquidez**: Análisis de flujos de mercado

### 💬 Interfaz de Chat Interactiva
- **Comandos en Lenguaje Natural**: Pregunta en español lo que necesites
- **Recomendaciones Instantáneas**: Respuestas en tiempo real
- **Análisis Completo**: Reportes detallados del mercado
- **Gestión de Alertas**: Notificaciones personalizadas

### 📈 Tracking y Métricas
- **Win Rate y Profit Factor**: Métricas de rendimiento en tiempo real
- **Sharpe Ratio**: Evaluación de performance ajustada por riesgo
- **Historial de Trades**: Registro completo de operaciones
- **P&L Tracking**: Seguimiento de ganancias y pérdidas

### 🔔 Sistema de Alertas
- **Alertas de Precio**: Notificaciones cuando BTC alcance niveles específicos
- **Alertas de Indicadores**: RSI, MACD y otros indicadores técnicos
- **Alertas de Predicción**: Basadas en confianza del modelo
- **Historial Completo**: Registro de todas las alertas disparadas

## 🏗️ Arquitectura del Sistema

```
BTC/
├── src/
│   ├── data/
│   │   ├── data_collector.py       # Recopilación de Binance API
│   │   └── feature_engineering.py  # Feature engineering (100+ indicators)
│   ├── models/
│   │   └── btc_predictor.py       # LSTM con atención
│   ├── utils/
│   │   ├── risk_manager.py        # Gestión de riesgo avanzada
│   │   └── alert_system.py        # Sistema de alertas
│   └── chat/
│       ├── advisor.py             # Sistema de asesoramiento
│       └── chat_interface.py      # Interfaz de chat
├── data/                          # Datos de mercado
├── models/                        # Modelos entrenados
├── train_model.py                # Pipeline de entrenamiento
└── run_chat.py                   # Ejecutar sistema de trading
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd BTC

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Entrenar el Modelo

```bash
# Entrenamiento estándar (180 días)
python train_model.py

# Entrenamiento avanzado
python train_model.py --days 365 --epochs 150 --batch-size 64
```

**Opciones de Entrenamiento:**
- `--days 365`: Días de datos históricos
- `--timeframe 1h`: Intervalo (1h, 4h, 1d)
- `--sequence-length 48`: Ventana de entrada
- `--prediction-horizon 6`: Horas a predecir
- `--epochs 150`: Épocas de entrenamiento
- `--batch-size 64`: Tamaño de batch

### 3. Iniciar Sistema de Trading

```bash
python run_chat.py
```

## 💬 Comandos del Chat

### Análisis y Predicciones
```
¿Cuál es el precio actual?
¿Debería comprar ahora?
¿Cuál es la tendencia?
¿Va a subir o bajar?
Dame un análisis completo
¿Cómo están los indicadores?
```

### Gestión de Riesgo
```
¿Cuánto debería comprar?
Position size
Balance
Capital
Performance
Estadísticas
```

### Alertas
```
Crear alerta de precio 50000
Crear alerta RSI bajo 30
Ver alertas
```

### Otros
```
Actualizar    # Actualiza datos del mercado
Ayuda         # Lista todos los comandos
Salir         # Cierra el chat
```

## 🧠 Arquitectura del Modelo

### Red Neuronal LSTM con Atención

```python
Input (48 timesteps, 100+ features)
    ↓
Bidirectional LSTM (128 units) + Dropout
    ↓
Batch Normalization
    ↓
Bidirectional LSTM (64 units) + Dropout
    ↓
Batch Normalization
    ↓
Attention Layer (mecanismo de atención)
    ↓
Dense (64 units, ReLU) + Dropout
    ↓
Dense (32 units, ReLU) + Dropout
    ↓
Output (6 predicciones)
```

**Optimización:**
- Loss Function: Huber (robusta a outliers)
- Optimizer: Adam con learning rate adaptativo
- Callbacks: Early Stopping, ReduceLROnPlateau, Model Checkpoint

## 💰 Gestión de Riesgo

### Cálculo Automático de Position Size

El sistema calcula automáticamente el tamaño óptimo de posición basado en:
- Capital disponible
- Distancia al stop loss
- Nivel de confianza de la predicción
- Riesgo máximo por trade (default: 2%)

```python
# Ejemplo de respuesta
Tamaño de Posición:
  BTC: 0.04500000
  USDT: $2,000.00

Capital en Riesgo: $200.00 (2.00%)
Stop Loss: $44,100.00
Take Profit: $47,500.00
```

### Protección de Capital

- **Riesgo por Trade**: Máximo 2% del capital
- **Pérdida Diaria Máxima**: 5% del capital
- **Drawdown Máximo**: 20% del capital
- **Bloqueo Automático**: Suspende trading si se alcanzan límites

## 📊 Indicadores Técnicos Implementados

### Tendencia (Trend)
- SMA: 7, 14, 21, 50, 100, 200 periodos
- EMA: 7, 14, 21, 50, 100, 200 periodos
- MACD + Señal + Histograma
- ADX (Average Directional Index)

### Momentum
- RSI: 6, 12, 14, 24 periodos
- Stochastic Oscillator
- Rate of Change (ROC)

### Volatilidad
- Bollinger Bands: 20, 50 periodos
- Average True Range (ATR): 14, 21 periodos
- Volatilidad histórica

### Volumen
- On-Balance Volume (OBV)
- Volume Weighted Average Price (VWAP)
- Ratios de volumen

### Características de Precio
- Returns: 1, 3, 6, 12, 24 periodos
- Log Returns
- High/Low Ranges
- Price Position in Range

### Características Temporales
- Hora (encoding cíclico sin/cos)
- Día de la semana
- Mes
- Quarter

## 📈 Métricas de Performance

El sistema trackea automáticamente:

- **Win Rate**: Porcentaje de trades ganadores
- **Profit Factor**: Ganancias totales / Pérdidas totales
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Average Win**: Ganancia promedio por trade ganador
- **Average Loss**: Pérdida promedio por trade perdedor
- **Total P&L**: Ganancia/pérdida neta
- **Drawdown**: Caída máxima desde pico de capital

## 🔔 Sistema de Alertas

### Tipos de Alertas

1. **Alertas de Precio**
   - Notifica cuando BTC alcanza precio objetivo
   - Direcciones: above/below

2. **Alertas de Indicadores**
   - RSI en sobrecompra/sobreventa
   - MACD cruza señal
   - Cualquier indicador técnico

3. **Alertas de Predicción**
   - Alta confianza (>75%)
   - Tendencia específica (alcista/bajista)

### Ejemplo de Uso

```python
# En el chat
"Crear alerta de precio 50000"
→ Alerta creada: Te notificaremos cuando BTC llegue a $50,000

"Ver alertas"
→ Lista de todas tus alertas activas
```

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)

```bash
# Binance API (opcional - no requerido para datos públicos)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Configuración del modelo
MODEL_UPDATE_INTERVAL=3600
PREDICTION_HORIZON=24

# Gestión de riesgo
INITIAL_CAPITAL=10000
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05
MAX_DRAWDOWN=0.20
```

### Personalización del Modelo

Edita `src/models/btc_predictor.py`:
```python
# Arquitectura
- Número de capas LSTM
- Unidades por capa (128, 64)
- Dropout rate (0.2, 0.3)

# Entrenamiento
- Learning rate (0.001)
- Loss function (huber)
- Batch size (32)
```

## 📊 Ejemplo de Uso Programático

```python
from src.models.btc_predictor import BTCPredictor
from src.data.data_collector import BTCDataCollector
from src.data.feature_engineering import FeatureEngineer
from src.utils.risk_manager import RiskManager

# Cargar modelo
predictor = BTCPredictor()
predictor.load('models/btc_predictor')

# Obtener datos
collector = BTCDataCollector()
df = collector.fetch_ohlcv(timeframe='1h', limit=100)

# Feature engineering
fe = FeatureEngineer()
df_features = fe.create_all_features(df)

# Predicción
predictions = predictor.predict(df_features)
print(f"Predicciones: {predictions}")

# Calcular position size
rm = RiskManager(initial_capital=10000)
current_price = collector.get_current_price()
stop_loss = rm.calculate_stop_loss(current_price, 'long')
position = rm.calculate_position_size(current_price, stop_loss)

print(f"Position Size: {position}")
```

## 🔧 Troubleshooting

### Error de Conexión a Binance
```bash
# Verifica conexión a internet
ping api.binance.com

# Binance API pública no requiere keys
# Solo necesitas keys para trading real
```

### Modelo No Encontrado
```bash
# Entrena el modelo primero
python train_model.py
```

### Errores de Memoria
```bash
# Reduce batch size
python train_model.py --batch-size 16

# Reduce días de entrenamiento
python train_model.py --days 90
```

### Actualizar Modelo
```bash
# Reentrenar con datos frescos
python train_model.py --days 180 --epochs 100
```

## 📝 Roadmap

- [ ] Integración con exchange para trading automático
- [ ] Soporte para múltiples pares (ETH, BNB, etc.)
- [ ] Dashboard web con gráficos en vivo
- [ ] Backtesting histórico completo
- [ ] Optimización de hiperparámetros automática
- [ ] Ensemble de múltiples modelos
- [ ] Sentimiento de redes sociales
- [ ] API REST para integración

## 🤝 Contribuciones

Contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre Pull Request

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 🙏 Tecnologías

- [TensorFlow/Keras](https://www.tensorflow.org/) - Deep Learning Framework
- [CCXT](https://github.com/ccxt/ccxt) - Exchange API
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Indicadores Técnicos
- [Pandas](https://pandas.pydata.org/) - Data Analysis
- [NumPy](https://numpy.org/) - Numerical Computing
- [Binance](https://www.binance.com/) - Exchange de Criptomonedas

## 📧 Soporte

Para issues, sugerencias o reportar bugs, abre un issue en GitHub.

---

**Desarrollado para traders profesionales de criptomonedas** 📈💰

