# 🎯 Guía de Uso - Sistema de Trading BTC/USDT

## 🚀 Inicio Rápido

### 1. Instalación
```bash
pip install -r requirements.txt
```

### 2. Entrenar el Modelo
```bash
python train_model.py
```
Esto descargará 180 días de datos históricos de BTC/USDT y entrenará el modelo (toma ~30-60 minutos).

### 3. Iniciar el Chat
```bash
python run_chat.py
```

## 💬 Cómo Usar el Chat

Una vez iniciado el chat, puedes hacer preguntas en español natural. Aquí tienes ejemplos:

### 📊 Consultar Precio y Análisis

**Precio actual:**
```
¿Cuál es el precio actual?
¿A cuánto está el BTC?
```

**Análisis de tendencia:**
```
¿Cuál es la tendencia?
¿Va a subir o bajar?
Muéstrame las predicciones
```

**Indicadores técnicos:**
```
¿Cómo están los indicadores?
Muéstrame el RSI
¿Qué dice el MACD?
```

### 🎯 Obtener Recomendaciones

```
¿Debería comprar ahora?
¿Recomiendas vender?
Dame una recomendación
Análisis completo
```

**Ejemplo de respuesta:**
```
🎯 RECOMENDACIÓN: COMPRAR

📊 Confianza: 78.5%
⚠️ Nivel de Riesgo: BAJO

💰 Precio Actual: $45,230.00
🎯 Precio Objetivo: $47,850.00
🛡️ Stop Loss: $43,850.00

📈 Cambio Esperado: +2.45%

💡 Razón: Tendencia alcista fuerte detectada. Se espera un incremento
promedio de 2.45% en las próximas 6 horas.
```

### 💰 Gestión de Riesgo

**Calcular tamaño de posición:**
```
¿Cuánto debería comprar?
Position size
¿Cuánto comprar?
```

**Ejemplo de respuesta:**
```
📊 CÁLCULO DE POSICIÓN

💰 Precio de Entrada: $45,230.00
🛡️ Stop Loss: $43,850.00

Tamaño de Posición:
  BTC: 0.14470000
  USDT: $6,545.00

Capital en Riesgo: $200.00 (2.00%)
Riesgo por Unidad: 3.05%
```

**Ver balance y capital:**
```
Balance
Capital
Portafolio
```

**Ver estadísticas:**
```
Performance
Rendimiento
Estadísticas
```

### 🔔 Gestión de Alertas

**Crear alertas:**
```
Crear alerta de precio 50000
Crear alerta de precio 40000
Crear alerta RSI bajo 30
```

**Ver alertas activas:**
```
Ver alertas
Mis alertas
```

### 🔄 Actualizar Datos

```
Actualizar
Refresh
Update
```

## 📋 Comandos Principales

| Comando | Qué hace |
|---------|----------|
| `precio` / `cuanto` | Muestra precio actual |
| `comprar` / `vender` | Da recomendación de trading |
| `tendencia` / `prediccion` | Análisis de tendencia |
| `indicadores` / `rsi` / `macd` | Indicadores técnicos |
| `analisis completo` | Reporte completo del mercado |
| `cuanto comprar` / `position size` | Cálculo de tamaño de posición |
| `balance` / `capital` | Estado del portafolio |
| `performance` / `estadisticas` | Métricas de rendimiento |
| `crear alerta` | Crear alertas |
| `ver alertas` | Ver alertas activas |
| `actualizar` | Actualizar datos |
| `ayuda` | Lista de comandos |
| `salir` | Cerrar chat |

## 🎓 Entender las Recomendaciones

### Niveles de Confianza

- **>70%**: Alta confianza, señal fuerte
- **50-70%**: Confianza media, señal moderada
- **<50%**: Baja confianza, mercado incierto

### Niveles de Riesgo

- **BAJO**: Tendencia clara, múltiples indicadores confirmando
- **MEDIO**: Tendencia moderada, algunos indicadores mixtos
- **ALTO**: Sin tendencia clara, espera mejor oportunidad

### Tipos de Recomendaciones

1. **COMPRAR**: Fuerte tendencia alcista (confianza >70%)
2. **COMPRAR (CAUTELOSO)**: Tendencia alcista moderada (confianza 60-70%)
3. **VENDER**: Fuerte tendencia bajista (confianza >70%)
4. **VENDER (CAUTELOSO)**: Tendencia bajista moderada (confianza 60-70%)
5. **MANTENER/ESPERAR**: Mercado lateral o sin tendencia clara

## 💼 Gestión de Riesgo

### Position Sizing Automático

El sistema calcula automáticamente cuánto comprar basándose en:

1. **Tu capital disponible**
2. **Distancia al stop loss** (cuánto puede caer antes de salir)
3. **Confianza de la predicción** (más confianza = posición más grande)
4. **Riesgo máximo por trade** (default: 2% del capital)

**Ejemplo:**

Si tienes $10,000 de capital:
- Riesgo por trade: 2% = $200
- Si el stop loss está a 3% de distancia
- Puedes comprar ~$6,666 de BTC

### Stop Loss y Take Profit

**Stop Loss:**
- Calculado automáticamente basado en volatilidad (ATR)
- Por defecto: 3% debajo del precio de entrada (long)
- Protege tu capital limitando pérdidas

**Take Profit (3 niveles):**
- TP1: 1.5x el riesgo
- TP2: 2.5x el riesgo
- TP3: 3.75x el riesgo

**Ejemplo:**
```
Entry: $45,000
Stop Loss: $43,650 (riesgo = $1,350)

Take Profit 1: $47,025 (+$2,025 = 1.5x)
Take Profit 2: $48,375 (+$3,375 = 2.5x)
Take Profit 3: $50,062 (+$5,062 = 3.75x)
```

### Protección de Capital

El sistema te protege con límites automáticos:

- **Máximo riesgo por trade**: 2% del capital
- **Pérdida diaria máxima**: 5% del capital
- **Drawdown máximo**: 20% del capital

Si alcanzas estos límites, el sistema te alertará y recomendará NO operar.

## 📊 Métricas de Performance

### Win Rate
Porcentaje de trades ganadores sobre total de trades.

**Ejemplo:** 15 ganadores de 20 trades = 75% win rate

### Profit Factor
Ganancias totales dividido pérdidas totales.

- **>2.0**: Excelente
- **1.5-2.0**: Muy bueno
- **1.0-1.5**: Bueno
- **<1.0**: Perdiendo dinero

### Sharpe Ratio
Retorno ajustado por riesgo. Mide si tus ganancias justifican el riesgo.

- **>2.0**: Excelente
- **1.0-2.0**: Bueno
- **<1.0**: Pobre

## 🔔 Sistema de Alertas

### Alertas de Precio

```
Crear alerta de precio 50000
```
Te notifica cuando BTC llegue a $50,000.

### Alertas de Indicadores

```
Crear alerta RSI bajo 30
```
Te notifica cuando RSI llegue a 30 (zona de sobreventa).

### Alertas de Predicción

```
Crear alerta confianza 80
```
Te notifica cuando el modelo tenga una predicción con >80% confianza.

## ⚙️ Configuración Avanzada

### Ajustar Capital Inicial

Edita `src/chat/chat_interface.py` línea ~24:

```python
self.advisor = TradingAdvisor(
    self.predictor,
    self.data_collector,
    self.feature_engineer,
    initial_capital=10000  # Cambia esto
)
```

### Ajustar Riesgo

Edita `src/utils/risk_manager.py` línea ~12:

```python
def __init__(self,
             initial_capital=10000,
             max_risk_per_trade=0.02,  # 2% - cambia esto
             max_portfolio_risk=0.06):  # 6% - cambia esto
```

### Reentrenar el Modelo

```bash
# Con más datos (mejor precisión)
python train_model.py --days 365 --epochs 150

# Más rápido (menos precisión)
python train_model.py --days 90 --epochs 50
```

## 🆘 Solución de Problemas

### "No se pudo obtener datos"
```bash
# Verifica conexión a internet
ping api.binance.com

# Reinicia el chat
python run_chat.py
```

### "Model not found"
```bash
# Entrena el modelo primero
python train_model.py
```

### Predicciones inconsistentes
```bash
# Actualiza datos en el chat
Actualizar

# O reentrena el modelo
python train_model.py --days 180
```

## 💡 Consejos de Uso

1. **Actualiza datos regularmente**: Usa "actualizar" cada hora
2. **No confíes solo en el modelo**: Úsalo como herramienta de análisis
3. **Respeta los stop loss**: Son tu protección principal
4. **Gestiona el tamaño**: Usa el cálculo automático de position size
5. **Revisa performance**: Verifica métricas regularmente
6. **Usa alertas**: Configura alertas para no estar pegado a la pantalla

## 📞 Soporte

Si tienes problemas:
1. Lee esta guía completa
2. Revisa el README.md
3. Abre un issue en GitHub

---

**¡Listo para empezar a usar el sistema profesionalmente!** 🚀📈
