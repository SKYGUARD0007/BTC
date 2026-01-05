# 🚀 BTC/USDT AI Prediction Model with Interactive Chat

Sistema avanzado de predicción de Bitcoin usando Deep Learning (LSTM con Atención) e interfaz de chat interactiva para asesoramiento de trading en tiempo real.

## 📋 Características

- 🤖 **Modelo de Deep Learning Avanzado**: LSTM bidireccional con mecanismo de atención
- 📊 **Análisis Técnico Completo**: Más de 100 indicadores técnicos (RSI, MACD, Bollinger Bands, etc.)
- 💬 **Chat Interactivo**: Interfaz conversacional para consultar predicciones y recomendaciones
- 📈 **Predicciones Multi-Horizonte**: Predice múltiples puntos en el futuro (configurable)
- 🎯 **Sistema de Recomendaciones**: Asesoramiento automático basado en predicciones (Comprar/Vender/Mantener)
- 🔄 **Datos en Tiempo Real**: Integración con Binance API para datos actualizados
- 📉 **Análisis de Riesgo**: Evaluación de confianza y niveles de riesgo

## 🏗️ Arquitectura del Proyecto

```
BTC/
├── src/
│   ├── data/
│   │   ├── data_collector.py       # Recopilación de datos de Binance
│   │   └── feature_engineering.py  # Creación de características técnicas
│   ├── models/
│   │   └── btc_predictor.py       # Modelo LSTM con atención
│   └── chat/
│       ├── advisor.py             # Sistema de asesoramiento
│       └── chat_interface.py      # Interfaz de chat interactiva
├── data/
│   ├── raw/                       # Datos crudos de mercado
│   └── processed/                 # Datos procesados con features
├── models/                        # Modelos entrenados
├── train_model.py                # Script de entrenamiento
├── run_chat.py                   # Script para ejecutar el chat
└── requirements.txt              # Dependencias
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd BTC

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Entrenamiento del Modelo

```bash
# Entrenamiento básico (180 días de datos históricos)
python train_model.py

# Entrenamiento personalizado
python train_model.py --days 365 --epochs 150 --batch-size 64
```

**Opciones disponibles:**
- `--days`: Días de datos históricos (default: 180)
- `--timeframe`: Intervalo de tiempo - 1h, 4h, 1d (default: 1h)
- `--sequence-length`: Longitud de secuencia (default: 48)
- `--prediction-horizon`: Horas a predecir (default: 6)
- `--epochs`: Épocas de entrenamiento (default: 100)
- `--batch-size`: Tamaño del batch (default: 32)

### 3. Usar el Chat Interactivo

```bash
python run_chat.py
```

## 💬 Comandos del Chat

Una vez iniciado el chat, puedes hacer preguntas en lenguaje natural:

### Consultas de Precio
```
¿Cuál es el precio actual?
¿A cuánto está el BTC?
```

### Recomendaciones de Trading
```
¿Debería comprar ahora?
¿Recomiendas vender?
Dame una recomendación
```

### Análisis de Tendencia
```
¿Cuál es la tendencia?
¿Va a subir o bajar?
Muéstrame las predicciones
```

### Indicadores Técnicos
```
¿Cómo están los indicadores?
Muéstrame el RSI
¿Qué dice el MACD?
```

### Análisis Completo
```
Dame un análisis completo
Reporte del mercado
```

### Otros Comandos
```
ayuda          # Muestra todos los comandos
actualizar     # Actualiza datos del mercado
salir          # Cierra el chat
```

## 🧠 Arquitectura del Modelo

### Modelo LSTM con Atención

El modelo utiliza una arquitectura avanzada de Deep Learning:

1. **Capas LSTM Bidireccionales**: Capturan patrones temporales en ambas direcciones
2. **Mecanismo de Atención**: Enfoca el modelo en las características más relevantes
3. **Batch Normalization**: Mejora la estabilidad del entrenamiento
4. **Dropout Layers**: Previene overfitting
5. **Dense Layers**: Transformación final para predicciones multi-horizonte

### Características Técnicas (100+)

#### Indicadores de Tendencia
- SMA (7, 14, 21, 50, 100, 200)
- EMA (7, 14, 21, 50, 100, 200)
- MACD y señales
- ADX (Average Directional Index)

#### Indicadores de Momentum
- RSI (6, 12, 14, 24)
- Stochastic Oscillator
- Rate of Change (ROC)

#### Indicadores de Volatilidad
- Bollinger Bands (20, 50)
- Average True Range (ATR)
- Volatilidad histórica

#### Indicadores de Volumen
- On-Balance Volume (OBV)
- Volume Weighted Average Price (VWAP)
- Ratios de volumen

#### Características de Precio
- Returns (1, 3, 6, 12, 24 períodos)
- Log returns
- Rangos de precio
- Momentum

#### Características Temporales
- Hora del día (encoding cíclico)
- Día de la semana
- Mes del año
- Quarter

## 📊 Sistema de Recomendaciones

El sistema analiza múltiples factores para generar recomendaciones:

### Niveles de Confianza
- **Alta (>70%)**: Señal fuerte, tendencia clara
- **Media (50-70%)**: Señal moderada, cierta incertidumbre
- **Baja (<50%)**: Mercado lateral, esperar

### Niveles de Riesgo
- **BAJO**: Tendencia fuerte confirmada por múltiples indicadores
- **MEDIO**: Tendencia moderada, algunos indicadores mixtos
- **ALTO**: Sin tendencia clara, alta volatilidad

### Tipos de Recomendaciones
1. **COMPRAR**: Tendencia alcista fuerte
2. **COMPRAR (CAUTELOSO)**: Tendencia alcista moderada
3. **VENDER**: Tendencia bajista fuerte
4. **VENDER (CAUTELOSO)**: Tendencia bajista moderada
5. **MANTENER/ESPERAR**: Sin tendencia clara

Cada recomendación incluye:
- Precio objetivo
- Stop loss sugerido
- Cambio esperado en porcentaje
- Análisis detallado de la razón

## 📈 Ejemplo de Uso

```python
from src.models.btc_predictor import BTCPredictor
from src.data.data_collector import BTCDataCollector
from src.data.feature_engineering import FeatureEngineer

# Cargar modelo entrenado
predictor = BTCPredictor()
predictor.load('models/btc_predictor')

# Obtener datos actuales
collector = BTCDataCollector()
df = collector.fetch_ohlcv(timeframe='1h', limit=100)

# Crear características
fe = FeatureEngineer()
df_features = fe.create_all_features(df)

# Hacer predicción
predictions = predictor.predict(df_features)
print(f"Predicciones: {predictions}")
```

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)

```bash
# API Keys de Binance (opcional)
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret

# Configuración del modelo
MODEL_UPDATE_INTERVAL=3600
PREDICTION_HORIZON=24
```

### Personalización del Modelo

Edita `src/models/btc_predictor.py` para ajustar:
- Número de capas LSTM
- Unidades por capa
- Tasa de dropout
- Función de pérdida
- Optimizador

## 📊 Métricas del Modelo

El modelo se evalúa con múltiples métricas:

- **MAE (Mean Absolute Error)**: Error absoluto promedio
- **MSE (Mean Squared Error)**: Error cuadrático medio
- **MAPE (Mean Absolute Percentage Error)**: Error porcentual promedio
- **Huber Loss**: Pérdida robusta a outliers

## ⚠️ Disclaimer

**IMPORTANTE**: Este sistema es para fines educativos y de investigación.

- ❌ **NO** es asesoramiento financiero profesional
- ❌ **NO** garantiza ganancias en trading
- ❌ Las criptomonedas son altamente volátiles
- ✅ Siempre haz tu propia investigación (DYOR)
- ✅ Invierte solo lo que puedas permitirte perder
- ✅ Consulta con profesionales financieros antes de tomar decisiones

## 🔧 Troubleshooting

### Error al conectar con Binance
```bash
# Verifica tu conexión a internet
# Binance API es pública, no requiere keys para datos de mercado
```

### Modelo no encontrado
```bash
# Entrena el modelo primero
python train_model.py
```

### Errores de memoria durante entrenamiento
```bash
# Reduce el batch size
python train_model.py --batch-size 16
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [CCXT](https://github.com/ccxt/ccxt) - Biblioteca de exchanges de criptomonedas
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Indicadores técnicos
- [TensorFlow](https://www.tensorflow.org/) - Framework de Deep Learning
- [Binance](https://www.binance.com/) - Exchange de criptomonedas

## 📧 Contacto

Para preguntas, sugerencias o reportar bugs, abre un issue en GitHub.

---

**Creado con ❤️ para la comunidad de trading de criptomonedas**
