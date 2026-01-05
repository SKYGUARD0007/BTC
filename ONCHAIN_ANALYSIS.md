# 🐋 Análisis On-Chain y Detección de Ballenas

## ¿Qué son los datos On-Chain?

Los datos on-chain son información extraída directamente de la blockchain de Bitcoin. A diferencia de los indicadores técnicos tradicionales (que solo miran precio y volumen en exchanges), los datos on-chain revelan **lo que realmente está pasando en la red**.

## 🎯 ¿Por qué son importantes?

Las **ballenas** (wallets con grandes cantidades de BTC) mueven el mercado. Cuando una ballena compra o vende, el precio responde. El análisis on-chain te permite:

1. **Ver antes que los demás** - Detectar acumulación antes de que suba el precio
2. **Seguir el dinero inteligente** - Las ballenas saben más que el trader promedio
3. **Evitar trampas** - Si el precio sube pero las ballenas están vendiendo, es una señal de alerta

## 🔍 Métricas On-Chain Implementadas

### 1. Detección de Ballenas
- **Transacciones > 100 BTC**: Detectamos movimientos grandes en tiempo real
- **Volumen Total**: Suma de todas las transacciones grandes
- **Frecuencia**: Cuántas ballenas están moviéndose

**Señales:**
- 10+ transacciones grandes = **ACUMULACIÓN FUERTE** (muy alcista)
- 5-10 transacciones grandes = **ACUMULACIÓN MODERADA** (alcista)
- < 5 transacciones = **NEUTRAL**

### 2. Métricas de Red
- **Hash Rate**: Poder de minado (seguridad de la red)
- **Dificultad**: Ajuste de dificultad de minado
- **Volumen de Trading**: Volumen real en blockchain vs exchanges

### 3. Mempool (Pool de Transacciones Pendientes)
- **Tamaño del Mempool**: Congestión de la red
- **Número de Transacciones**: Actividad de la red

**Interpretación:**
- Mempool grande (>50k tx) = Alta demanda = Alcista
- Mempool pequeño (<20k tx) = Baja demanda = Neutral/Bajista

## 🤖 Cómo el Sistema Usa Datos On-Chain

### Integración en Recomendaciones

Cuando pides una recomendación, el sistema:

1. **Analiza el modelo IA** → Confianza base (ej: 70%)
2. **Consulta datos on-chain** → Detecta ballenas
3. **Ajusta la confianza** → Añade boost on-chain

**Ejemplo Real:**

```
Modelo IA: ALCISTA (70% confianza)
+ Ballenas: 12 transacciones grandes detectadas (+15% boost)
= RECOMENDACIÓN FINAL: COMPRAR FUERTE (85% confianza)
```

### Boost On-Chain

El sistema añade confianza extra basándose en:

| Condición | Boost | Impacto |
|-----------|-------|---------|
| 10+ ballenas acumulando | +15% | Muy fuerte |
| 5-10 ballenas acumulando | +10% | Fuerte |
| Señal on-chain alcista | +10% | Moderado |

**Máximo boost:** +25% (no supera 95% confianza total)

### Casos Especiales

**Señales Contradictorias:**
- Modelo IA: BAJISTA
- On-chain: Ballenas acumulando fuerte

→ **Recomendación:** ESPERAR - Señales Mixtas

*Razón:* Las ballenas están comprando a pesar de la tendencia bajista (posible reversión)

## 💬 Comandos del Chat

### Ver Actividad de Ballenas

```
ballenas
whales
on-chain
on chain
```

**Respuesta incluye:**
- Número de transacciones grandes detectadas
- Volumen total en BTC
- Señal (ACUMULACIÓN / NEUTRAL)
- Confianza
- Recomendación
- Últimas 3 transacciones grandes con timestamp

**Ejemplo:**

```
🐋 ANÁLISIS DE BALLENAS Y ON-CHAIN

⚠️ ACTIVIDAD DE BALLENAS DETECTADA

Transacciones Grandes: 12
Volumen Total: 1,543.50 BTC
Señal: ACUMULACIÓN FUERTE
Confianza: 85%

💡 ⚠️ ALERTA: 12 transacciones grandes detectadas!
Volumen total: 1,543.50 BTC
Transacción más grande: 245.00 BTC
Señal: ACUMULACIÓN FUERTE

🎯 Recomendación: COMPRAR - Ballenas Acumulando

📊 ÚLTIMAS TRANSACCIONES GRANDES:
  1. 245.00 BTC - 14:23:45
  2. 187.30 BTC - 14:18:12
  3. 156.20 BTC - 14:05:33

⛓️ SEÑAL ON-CHAIN GENERAL

Acción: COMPRAR - Ballenas Acumulando
Confianza: 82.5%
Razón: Ballenas están acumulando BTC (transacciones grandes detectadas) | Alta congestión en mempool indica fuerte demanda
```

### Recomendaciones con On-Chain

Cuando pides una recomendación normal, **automáticamente** incluye análisis on-chain:

```
¿Debería comprar?
```

**Respuesta incluye:**

```
🎯 RECOMENDACIÓN: COMPRAR FUERTE

📊 Confianza: 85.0%
   ├─ IA: 70.0%
   └─ On-Chain Boost: +15.0%

⚠️ Nivel de Riesgo: BAJO

💰 Precio Actual: $45,230.00
🎯 Precio Objetivo: $47,850.00
🛡️ Stop Loss: $43,850.00

📈 Cambio Esperado: +2.45%

💡 Razón: Tendencia alcista fuerte detectada. Incremento esperado: 2.45% | 🐋 12 ballenas acumulando (1,543 BTC) | ⛓️ ACUMULACIÓN FUERTE
```

## 🎯 Estrategias Basadas en Ballenas

### 1. Seguir a las Ballenas

**Señal:** 10+ transacciones grandes + Volumen > 1,000 BTC

**Acción:** COMPRAR con confianza alta

**Por qué:** Las ballenas raramente se equivocan a corto plazo

### 2. Divergencia On-Chain

**Señal:** Precio cayendo + Ballenas acumulando

**Acción:** COMPRAR en la caída (bottom fishing)

**Por qué:** Las ballenas compran cuando el mercado tiene miedo

### 3. Distribución de Ballenas

**Señal:** Precio alto + Ballenas vendiendo (transacciones hacia exchanges)

**Acción:** VENDER o ESPERAR

**Por qué:** Las ballenas están tomando ganancias

## 📊 Fuentes de Datos

El sistema obtiene datos on-chain de:

1. **Blockchain.info** - Transacciones y métricas de red
2. **Mempool.space** - Estado del mempool y congestión
3. **Blockchair** - Datos adicionales de blockchain

**Actualización:** Datos en tiempo real (cada consulta)

## ⚙️ Configuración

### Umbral de Ballena

Por defecto: **100 BTC**

Para cambiar, edita `src/data/onchain_data.py`:

```python
class OnChainDataCollector:
    def __init__(self):
        self.whale_threshold = 100  # Cambiar aquí
```

Valores recomendados:
- **50 BTC** - Más sensible (más señales)
- **100 BTC** - Balanceado (recomendado)
- **200 BTC** - Conservador (solo ballenas muy grandes)

### Boost On-Chain

Para ajustar el impacto de señales on-chain, edita `src/chat/advisor.py` líneas 190-201:

```python
if 'ACUMULACIÓN' in whale_signal and whale_count > 10:
    onchain_boost += 15  # Cambiar aquí
elif 'ACUMULACIÓN' in whale_signal and whale_count > 5:
    onchain_boost += 10  # Cambiar aquí
```

## 🚀 Ventajas del Análisis On-Chain

### Tradicional (Solo Precio)
- Reacciona **después** de que el precio se mueve
- No ve lo que hacen los jugadores grandes
- Puede dar señales tardías

### Con On-Chain (Este Sistema)
- Ve lo que hacen las **ballenas ANTES** de que mueva el precio
- Detecta **acumulación temprana**
- Mayor **confianza** en las recomendaciones
- Evita **trampas** (precio sube pero ballenas venden)

## 📈 Casos de Uso Reales

### Caso 1: Acumulación Silenciosa

```
Precio: Lateral en $44,000
Indicadores: Neutral
On-Chain: 15 ballenas acumulando 2,000 BTC

→ Recomendación: COMPRAR (SEÑAL ON-CHAIN)
→ Resultado: Precio sube a $48,000 en 2 días
```

### Caso 2: Trampa Alcista

```
Precio: Subiendo rápido a $52,000
Indicadores: ALCISTA FUERTE
On-Chain: Ballenas moviendo BTC a exchanges (vendiendo)

→ Recomendación: ESPERAR - Señales Contradictorias
→ Resultado: Precio cae a $47,000
```

### Caso 3: Bottom Fishing

```
Precio: Cayendo a $40,000 (-8%)
Indicadores: BAJISTA
On-Chain: 20 ballenas acumulando 3,500 BTC

→ Recomendación: COMPRAR - Ballenas Aprovechando Caída
→ Resultado: Reversión, precio sube a $45,000
```

## 🎓 Aprende Más

### Recursos sobre On-Chain

- **Glassnode Academy**: Tutoriales de análisis on-chain
- **CryptoQuant**: Métricas on-chain profesionales
- **Whalemap**: Seguimiento de ballenas

### Métricas Avanzadas (Futuras Versiones)

- **SOPR** (Spent Output Profit Ratio): Rentabilidad de holders
- **MVRV** (Market Value to Realized Value): Sobrevaloración/Subvaloración
- **NVT** (Network Value to Transactions): Valuación vs actividad
- **Exchange Flows**: Entrada/salida neta de exchanges
- **Miner Flows**: Comportamiento de mineros

## 💡 Tips Profesionales

1. **Combina señales**: IA + On-Chain + Indicadores = Mayor precisión
2. **Más peso a ballenas**: En mercado lateral, sigue a las ballenas
3. **Volumen importa**: 10 ballenas con 100 BTC c/u < 5 ballenas con 500 BTC c/u
4. **Timeframes**: Ballenas piensan a mediano plazo (días/semanas)
5. **No ignores la IA**: Si IA y On-Chain coinciden = Señal muy fuerte

---

**El sistema ahora toma decisiones como una ballena profesional** 🐋📈

