"""
Predicción Semanal de BTC/USDT
Usa métricas profesionales de ballenas + análisis técnico
"""
import sys
sys.path.append('src')

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 70)
print("🔮 PREDICCIÓN SEMANAL BTC/USDT")
print("=" * 70)
print("\n📊 Obteniendo datos en tiempo real de Binance...\n")

# Obtener precio actual de Binance
try:
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    response = requests.get(url, timeout=10)
    data = response.json()

    current_price = float(data['lastPrice'])
    price_change_24h = float(data['priceChangePercent'])
    high_24h = float(data['highPrice'])
    low_24h = float(data['lowPrice'])
    volume_24h = float(data['volume'])

    print(f"💰 PRECIO ACTUAL: ${current_price:,.2f}")
    print(f"📈 Cambio 24h: {price_change_24h:+.2f}%")
    print(f"📊 Rango 24h: ${low_24h:,.2f} - ${high_24h:,.2f}")
    print(f"📦 Volumen 24h: {volume_24h:,.0f} BTC\n")

except Exception as e:
    print(f"❌ Error obteniendo datos: {e}")
    current_price = 95000  # Fallback
    price_change_24h = 0

# Obtener datos históricos para análisis
print("📊 Obteniendo datos históricos...\n")
try:
    klines_url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1d',
        'limit': 30
    }
    response = requests.get(klines_url, params=params, timeout=10)
    klines = response.json()

    # Crear DataFrame
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])

    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['volume'] = df['volume'].astype(float)

    # Calcular métricas técnicas simples
    df['sma_7'] = df['close'].rolling(window=7).mean()
    df['sma_14'] = df['close'].rolling(window=14).mean()
    df['volatility'] = df['close'].pct_change().rolling(window=7).std()

    last_sma7 = df['sma_7'].iloc[-1]
    last_sma14 = df['sma_14'].iloc[-1]
    avg_volatility = df['volatility'].iloc[-1]

    print(f"📊 SMA 7 días: ${last_sma7:,.2f}")
    print(f"📊 SMA 14 días: ${last_sma14:,.2f}")
    print(f"📊 Volatilidad: {avg_volatility*100:.2f}%\n")

except Exception as e:
    print(f"⚠️ Error en análisis técnico: {e}\n")
    last_sma7 = current_price
    last_sma14 = current_price
    avg_volatility = 0.03

# Análisis de métricas profesionales de ballenas
print("=" * 70)
print("🐋 ANÁLISIS DE MÉTRICAS PROFESIONALES DE BALLENAS")
print("=" * 70)

from data.professional_whale_metrics import ProfessionalWhaleMetrics

metrics = ProfessionalWhaleMetrics()
signals = metrics.get_professional_signals(current_price)

if signals:
    overall = signals['overall_signal']

    print(f"\n🎯 SEÑAL INSTITUCIONAL: {overall['action']}")
    print(f"📊 Confianza: {overall['confidence']:.1f}%")
    print(f"📈 Buy Score: {overall['buy_score']:.1f}")
    print(f"📉 Sell Score: {overall['sell_score']:.1f}\n")

    print("💡 RAZONES PRINCIPALES:")
    for reason in overall.get('reasons', []):
        print(f"  • {reason}")

    # MVRV
    if signals.get('mvrv'):
        mvrv = signals['mvrv']
        print(f"\n📊 MVRV: {mvrv['value']:.2f}")
        print(f"   Señal: {mvrv['signal']}")
        print(f"   Acción: {mvrv['action']}")

    # SOPR
    if signals.get('sopr'):
        sopr = signals['sopr']
        print(f"\n💎 SOPR: {sopr['value']:.3f}")
        print(f"   Señal: {sopr['signal']}")
        print(f"   {sopr['interpretation']}")

    # Large Transactions
    if signals.get('large_transactions'):
        large_tx = signals['large_transactions']
        print(f"\n🐋 BALLENAS: {large_tx['whale_count']} detectadas")
        print(f"   Volumen: {large_tx['total_volume_btc']:,.0f} BTC")
        print(f"   Señal: {large_tx['signal']}")

# PREDICCIÓN PARA LA SEMANA
print("\n" + "=" * 70)
print("🔮 PREDICCIÓN PARA LA PRÓXIMA SEMANA (7 DÍAS)")
print("=" * 70)

# Calcular tendencia basada en señales
if signals:
    buy_score = overall.get('buy_score', 0)
    sell_score = overall.get('sell_score', 0)

    # Determinar dirección
    if buy_score > sell_score + 20:
        trend_direction = 1  # Alcista
        trend_strength = "FUERTE"
    elif buy_score > sell_score:
        trend_direction = 0.5  # Alcista moderado
        trend_strength = "MODERADA"
    elif sell_score > buy_score + 20:
        trend_direction = -1  # Bajista
        trend_strength = "FUERTE"
    elif sell_score > buy_score:
        trend_direction = -0.5  # Bajista moderado
        trend_strength = "MODERADA"
    else:
        trend_direction = 0  # Lateral
        trend_strength = "LATERAL"
else:
    trend_direction = 0
    trend_strength = "NEUTRAL"

# Calcular proyección
base_change = trend_direction * 0.05  # 5% base por dirección
volatility_factor = avg_volatility * 10  # Factor de volatilidad

# Predicciones diarias
predictions = []
for day in range(1, 8):
    # Proyección con algo de aleatoriedad
    daily_change = base_change + (np.random.randn() * volatility_factor * 0.5)
    predicted_price = current_price * (1 + daily_change * day / 7)

    date = datetime.now() + timedelta(days=day)
    predictions.append({
        'day': day,
        'date': date.strftime('%d/%m/%Y'),
        'price': predicted_price,
        'change': ((predicted_price - current_price) / current_price) * 100
    })

# Precio final (promedio de proyecciones)
final_prediction = sum([p['price'] for p in predictions]) / len(predictions)
final_change = ((final_prediction - current_price) / current_price) * 100

print(f"\n📅 PREDICCIÓN DÍA A DÍA:\n")
for pred in predictions:
    print(f"  Día {pred['day']} ({pred['date']}): ${pred['price']:,.2f} ({pred['change']:+.2f}%)")

print(f"\n🎯 PRECIO OBJETIVO (7 días): ${final_prediction:,.2f}")
print(f"📊 Cambio esperado: {final_change:+.2f}%")

# Niveles clave
support = current_price * 0.95
resistance = current_price * 1.05

print(f"\n📌 NIVELES CLAVE:")
print(f"   🛡️ Soporte: ${support:,.2f}")
print(f"   ⚡ Resistencia: ${resistance:,.2f}")

# Recomendación final
print("\n" + "=" * 70)
print("💡 RECOMENDACIÓN DE TRADING")
print("=" * 70)

if trend_direction > 0.3:
    action = "COMPRAR"
    reason = f"Tendencia alcista {trend_strength.lower()} con señales institucionales positivas"
    entry = current_price
    target = final_prediction
    stop_loss = current_price * 0.97
    risk_reward = abs((target - entry) / (entry - stop_loss))

elif trend_direction < -0.3:
    action = "VENDER / NO COMPRAR"
    reason = f"Tendencia bajista {trend_strength.lower()} con señales institucionales negativas"
    entry = current_price
    target = final_prediction
    stop_loss = current_price * 1.03
    risk_reward = abs((entry - target) / (stop_loss - entry))

else:
    action = "ESPERAR / MANTENER"
    reason = f"Mercado {trend_strength.lower()} sin tendencia clara"
    entry = current_price
    target = final_prediction
    stop_loss = current_price * 0.97
    risk_reward = 1.0

print(f"\n🎯 ACCIÓN: {action}")
print(f"💡 Razón: {reason}")
print(f"\n📊 SETUP DE TRADING:")
print(f"   💰 Entrada: ${entry:,.2f}")
print(f"   🎯 Objetivo: ${target:,.2f}")
print(f"   🛡️ Stop Loss: ${stop_loss:,.2f}")
print(f"   📈 Risk/Reward: {risk_reward:.2f}x")

if signals:
    print(f"\n🏦 Confianza institucional: {overall['confidence']:.1f}%")

print("\n" + "=" * 70)
print("⚠️ DISCLAIMER")
print("=" * 70)
print("""
Esta predicción se basa en:
- Métricas profesionales de ballenas (SOPR, MVRV, Exchange Flows)
- Análisis técnico de tendencia
- Datos en tiempo real de Binance

El mercado crypto es altamente volátil. Esta predicción es una estimación
basada en datos actuales y puede cambiar. Usa stop loss y gestión de riesgo.
""")

print("✅ Predicción completada!\n")
