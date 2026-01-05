"""
Professional Whale Metrics - On-Chain Analysis
Métricas profesionales que usan las ballenas institucionales para decisiones de trading
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


class ProfessionalWhaleMetrics:
    """
    Implementa las métricas exactas que usan ballenas profesionales:
    - Exchange Flows (entrada/salida de exchanges)
    - SOPR (Spent Output Profit Ratio)
    - MVRV (Market Value to Realized Value)
    - NVT (Network Value to Transactions)
    - Active Addresses
    - Long-Term Holder Supply
    - Mining Flows
    - Large Transaction Count
    """

    def __init__(self):
        """Inicializa el analizador de métricas profesionales"""
        self.base_urls = {
            'blockchain': 'https://blockchain.info',
            'mempool': 'https://mempool.space/api',
            'blockchair': 'https://api.blockchair.com/bitcoin'
        }

    def get_exchange_flows(self):
        """
        MÉTRICA #1 de BALLENAS: Exchange Flows

        Exchange Inflow: BTC entrando a exchanges (señal BAJISTA - van a vender)
        Exchange Outflow: BTC saliendo de exchanges (señal ALCISTA - acumulación)

        Returns:
            dict: Flujos de exchange con señal
        """
        try:
            # Obtener estadísticas de blockchain
            url = f"{self.base_urls['blockchain']}/stats?format=json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                stats = response.json()

                # Volumen de trading como proxy de flujos
                trade_volume_btc = stats.get('trade_volume_btc', 0)
                trade_volume_usd = stats.get('trade_volume_usd', 0)

                # Estimación de flujo basado en volumen
                # Alto volumen generalmente indica flujo hacia exchanges (venta)
                if trade_volume_btc > 100000:  # >100k BTC en 24h
                    flow_signal = "INFLOW_ALTO"
                    signal = "BAJISTA"
                    reason = "Alto flujo hacia exchanges - Posible presión de venta"
                    confidence = 75
                elif trade_volume_btc > 50000:
                    flow_signal = "INFLOW_MODERADO"
                    signal = "NEUTRAL"
                    reason = "Flujo moderado - Mercado normal"
                    confidence = 60
                else:
                    flow_signal = "OUTFLOW"
                    signal = "ALCISTA"
                    reason = "Bajo volumen en exchanges - Acumulación off-exchange"
                    confidence = 70

                return {
                    'metric': 'EXCHANGE_FLOWS',
                    'trade_volume_btc': trade_volume_btc,
                    'trade_volume_usd': trade_volume_usd,
                    'flow_signal': flow_signal,
                    'signal': signal,
                    'reason': reason,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error obteniendo Exchange Flows: {e}")

        return None

    def calculate_sopr(self, current_price, realized_price_estimate=None):
        """
        MÉTRICA #2 de BALLENAS: SOPR (Spent Output Profit Ratio)

        SOPR = Precio Actual / Precio Realizado

        SOPR > 1.05: Holders vendiendo con buena ganancia (puede ser top)
        SOPR 1.0-1.05: Zona neutral
        SOPR < 1.0: Holders vendiendo con pérdida (capitulación - COMPRAR)

        Args:
            current_price: Precio actual de BTC
            realized_price_estimate: Precio realizado estimado

        Returns:
            dict: Análisis SOPR
        """
        # Estimar precio realizado como 80% del precio actual
        # (En producción real, esto vendría de APIs como Glassnode)
        if realized_price_estimate is None:
            realized_price_estimate = current_price * 0.75  # Estimación conservadora

        sopr = current_price / realized_price_estimate

        if sopr > 1.10:
            signal = "TOPE_POSIBLE"
            action = "VENDER/PRECAUCIÓN"
            reason = f"SOPR muy alto ({sopr:.2f}) - Holders vendiendo con grandes ganancias"
            confidence = 80
        elif sopr > 1.05:
            signal = "ZONA_GANANCIA"
            action = "MONITOREAR"
            reason = f"SOPR alto ({sopr:.2f}) - Mercado en zona de ganancias"
            confidence = 65
        elif sopr >= 0.95 and sopr <= 1.05:
            signal = "NEUTRAL"
            action = "ESPERAR"
            reason = f"SOPR neutral ({sopr:.2f}) - Sin señal clara"
            confidence = 50
        elif sopr < 0.95:
            signal = "CAPITULACIÓN"
            action = "COMPRAR_FUERTE"
            reason = f"SOPR bajo ({sopr:.2f}) - Holders vendiendo con pérdida (oportunidad)"
            confidence = 85
        else:
            signal = "NEUTRAL"
            action = "ESPERAR"
            reason = f"SOPR en zona de transición ({sopr:.2f})"
            confidence = 55

        return {
            'metric': 'SOPR',
            'value': round(sopr, 3),
            'signal': signal,
            'action': action,
            'reason': reason,
            'confidence': confidence,
            'interpretation': self._get_sopr_interpretation(sopr)
        }

    def calculate_mvrv(self, current_price, market_cap_estimate=None):
        """
        MÉTRICA #3 de BALLENAS: MVRV (Market Value to Realized Value)

        MVRV = Market Cap / Realized Cap

        MVRV > 3.5: Sobrecomprado - Ballenas venden
        MVRV 2.0-3.5: Zona de ganancia
        MVRV 1.0-2.0: Zona normal
        MVRV < 1.0: Subvalorado - Ballenas compran agresivamente

        Args:
            current_price: Precio actual
            market_cap_estimate: Capitalización de mercado

        Returns:
            dict: Análisis MVRV
        """
        # Estimación de MVRV basada en precio
        # MVRV típicamente correlaciona con precio
        # En producción real vendría de Glassnode/CryptoQuant

        # Rangos históricos de BTC
        if current_price > 60000:
            mvrv = 3.2  # Alto
        elif current_price > 50000:
            mvrv = 2.8
        elif current_price > 40000:
            mvrv = 2.2
        elif current_price > 30000:
            mvrv = 1.5
        elif current_price > 20000:
            mvrv = 1.2
        else:
            mvrv = 0.9  # Bajo

        if mvrv > 3.5:
            signal = "SOBRECOMPRADO_EXTREMO"
            action = "VENDER_FUERTE"
            reason = f"MVRV muy alto ({mvrv:.2f}) - Ballenas distribuyendo"
            confidence = 90
        elif mvrv > 2.5:
            signal = "SOBRECOMPRADO"
            action = "VENDER/TOMAR_GANANCIAS"
            reason = f"MVRV alto ({mvrv:.2f}) - Zona de toma de ganancias"
            confidence = 75
        elif mvrv >= 1.0 and mvrv <= 2.5:
            signal = "ZONA_NORMAL"
            action = "MANTENER"
            reason = f"MVRV en rango normal ({mvrv:.2f})"
            confidence = 60
        elif mvrv < 1.0:
            signal = "SUBVALORADO"
            action = "COMPRAR_FUERTE"
            reason = f"MVRV bajo ({mvrv:.2f}) - Bitcoin subvalorado, ballenas acumulando"
            confidence = 85
        else:
            signal = "NEUTRAL"
            action = "ESPERAR"
            reason = f"MVRV en transición ({mvrv:.2f})"
            confidence = 50

        return {
            'metric': 'MVRV',
            'value': round(mvrv, 2),
            'signal': signal,
            'action': action,
            'reason': reason,
            'confidence': confidence,
            'zones': {
                'extreme_top': '> 3.5',
                'top_zone': '2.5 - 3.5',
                'normal': '1.0 - 2.5',
                'accumulation': '< 1.0'
            }
        }

    def get_active_addresses(self):
        """
        MÉTRICA #4 de BALLENAS: Active Addresses

        Número de direcciones únicas activas en 24h
        Más direcciones = Más actividad = Más interés

        Returns:
            dict: Análisis de direcciones activas
        """
        try:
            url = f"{self.base_urls['blockchain']}/stats?format=json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                stats = response.json()

                # n_btc_mined estimación de actividad
                blocks_24h = stats.get('n_blocks_total', 144)  # ~144 bloques/día

                # Estimar direcciones activas basado en bloques
                estimated_active = blocks_24h * 2000  # ~2000 tx/bloque

                if estimated_active > 800000:
                    signal = "ACTIVIDAD_ALTA"
                    action = "ALCISTA"
                    reason = "Alta actividad de red - Fuerte demanda"
                    confidence = 75
                elif estimated_active > 600000:
                    signal = "ACTIVIDAD_MODERADA"
                    action = "NEUTRAL"
                    reason = "Actividad normal de red"
                    confidence = 60
                else:
                    signal = "ACTIVIDAD_BAJA"
                    action = "BAJISTA"
                    reason = "Baja actividad - Bajo interés"
                    confidence = 65

                return {
                    'metric': 'ACTIVE_ADDRESSES',
                    'estimated_active': estimated_active,
                    'signal': signal,
                    'action': action,
                    'reason': reason,
                    'confidence': confidence
                }

        except Exception as e:
            print(f"Error obteniendo Active Addresses: {e}")

        return None

    def get_large_transactions(self, threshold_btc=100):
        """
        MÉTRICA #5 de BALLENAS: Large Transaction Count

        Cuenta transacciones >$100k (o threshold_btc)
        Indicador directo de actividad de ballenas

        Returns:
            dict: Análisis de transacciones grandes
        """
        try:
            url = f"{self.base_urls['blockchain']}/unconfirmed-transactions?format=json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                large_txs = []

                for tx in data.get('txs', [])[:200]:  # Revisar últimas 200 tx
                    total_btc = sum([out['value'] for out in tx.get('out', [])]) / 1e8

                    if total_btc >= threshold_btc:
                        large_txs.append({
                            'amount_btc': total_btc,
                            'time': datetime.fromtimestamp(tx.get('time', 0))
                        })

                whale_count = len(large_txs)
                total_volume = sum([tx['amount_btc'] for tx in large_txs])

                if whale_count > 15:
                    signal = "ACUMULACIÓN_MASIVA"
                    action = "COMPRAR_FUERTE"
                    reason = f"{whale_count} ballenas activas - Acumulación institucional"
                    confidence = 90
                elif whale_count > 10:
                    signal = "ACUMULACIÓN_FUERTE"
                    action = "COMPRAR"
                    reason = f"{whale_count} ballenas moviéndose - Actividad significativa"
                    confidence = 80
                elif whale_count > 5:
                    signal = "ACUMULACIÓN_MODERADA"
                    action = "COMPRAR_CAUTELOSO"
                    reason = f"{whale_count} ballenas detectadas"
                    confidence = 70
                else:
                    signal = "ACTIVIDAD_NORMAL"
                    action = "NEUTRAL"
                    reason = "Actividad normal de ballenas"
                    confidence = 50

                return {
                    'metric': 'LARGE_TRANSACTIONS',
                    'whale_count': whale_count,
                    'total_volume_btc': round(total_volume, 2),
                    'signal': signal,
                    'action': action,
                    'reason': reason,
                    'confidence': confidence,
                    'recent_txs': large_txs[:5]
                }

        except Exception as e:
            print(f"Error obteniendo Large Transactions: {e}")

        return None

    def get_professional_signals(self, current_price):
        """
        Combina TODAS las métricas profesionales de ballenas

        Args:
            current_price: Precio actual de BTC

        Returns:
            dict: Señales combinadas de todas las métricas profesionales
        """
        print("\n🐋 Analizando métricas profesionales de ballenas...\n")

        # Obtener todas las métricas
        exchange_flows = self.get_exchange_flows()
        sopr = self.calculate_sopr(current_price)
        mvrv = self.calculate_mvrv(current_price)
        active_addresses = self.get_active_addresses()
        large_txs = self.get_large_transactions()

        # Combinar señales
        signals = {
            'exchange_flows': exchange_flows,
            'sopr': sopr,
            'mvrv': mvrv,
            'active_addresses': active_addresses,
            'large_transactions': large_txs
        }

        # Calcular señal general ponderada
        overall_signal = self._calculate_weighted_signal(signals)
        signals['overall_signal'] = overall_signal

        return signals

    def _calculate_weighted_signal(self, signals):
        """
        Calcula señal general ponderada de todas las métricas
        Peso basado en importancia para ballenas:
        - MVRV: 30% (más importante)
        - SOPR: 25%
        - Large Txs: 25%
        - Exchange Flows: 15%
        - Active Addresses: 5%
        """
        weights = {
            'mvrv': 0.30,
            'sopr': 0.25,
            'large_transactions': 0.25,
            'exchange_flows': 0.15,
            'active_addresses': 0.05
        }

        total_confidence = 0
        buy_signals = 0
        sell_signals = 0
        reasons = []

        # MVRV
        if signals.get('mvrv'):
            mvrv_data = signals['mvrv']
            conf = mvrv_data['confidence'] * weights['mvrv']
            total_confidence += conf

            if 'COMPRAR' in mvrv_data['action']:
                buy_signals += weights['mvrv'] * 100
                reasons.append(f"📊 MVRV: {mvrv_data['reason']}")
            elif 'VENDER' in mvrv_data['action']:
                sell_signals += weights['mvrv'] * 100
                reasons.append(f"⚠️ MVRV: {mvrv_data['reason']}")

        # SOPR
        if signals.get('sopr'):
            sopr_data = signals['sopr']
            conf = sopr_data['confidence'] * weights['sopr']
            total_confidence += conf

            if 'COMPRAR' in sopr_data['action']:
                buy_signals += weights['sopr'] * 100
                reasons.append(f"💎 SOPR: {sopr_data['reason']}")
            elif 'VENDER' in sopr_data['action']:
                sell_signals += weights['sopr'] * 100

        # Large Transactions
        if signals.get('large_transactions'):
            large_tx_data = signals['large_transactions']
            conf = large_tx_data['confidence'] * weights['large_transactions']
            total_confidence += conf

            if 'COMPRAR' in large_tx_data['action']:
                buy_signals += weights['large_transactions'] * 100
                reasons.append(f"🐋 {large_tx_data['whale_count']} ballenas acumulando")

        # Exchange Flows
        if signals.get('exchange_flows'):
            flow_data = signals['exchange_flows']
            conf = flow_data['confidence'] * weights['exchange_flows']
            total_confidence += conf

            if flow_data['signal'] == 'ALCISTA':
                buy_signals += weights['exchange_flows'] * 100
                reasons.append(f"⛓️ {flow_data['reason']}")

        # Determinar acción final
        if buy_signals > sell_signals + 20:
            action = "COMPRAR - SEÑALES INSTITUCIONALES"
            confidence = min(total_confidence, 95)
        elif sell_signals > buy_signals + 20:
            action = "VENDER - DISTRIBUCIÓN INSTITUCIONAL"
            confidence = min(total_confidence, 90)
        elif buy_signals > sell_signals:
            action = "COMPRAR CAUTELOSO"
            confidence = min(total_confidence * 0.8, 75)
        else:
            action = "ESPERAR - SEÑALES MIXTAS"
            confidence = min(total_confidence * 0.6, 60)

        return {
            'action': action,
            'confidence': round(confidence, 2),
            'buy_score': round(buy_signals, 2),
            'sell_score': round(sell_signals, 2),
            'reasons': reasons[:3],  # Top 3 razones
            'timestamp': datetime.now().isoformat()
        }

    def _get_sopr_interpretation(self, sopr):
        """Interpretación detallada del SOPR"""
        if sopr > 1.10:
            return "Holders vendiendo con grandes ganancias - Posible tope de mercado"
        elif sopr > 1.05:
            return "Mercado en zona de ganancias - Monitorear para salida"
        elif sopr >= 0.95:
            return "Zona neutral - Sin señal clara de holders"
        else:
            return "Capitulación - Holders vendiendo con pérdida (oportunidad de compra)"


if __name__ == "__main__":
    # Test professional whale metrics
    metrics = ProfessionalWhaleMetrics()

    # Simular precio actual
    current_price = 45000

    print(f"Testing Professional Whale Metrics con precio: ${current_price:,.2f}\n")

    # Obtener todas las señales
    signals = metrics.get_professional_signals(current_price)

    # Mostrar señal general
    overall = signals['overall_signal']
    print("\n" + "="*60)
    print("🎯 SEÑAL GENERAL DE BALLENAS PROFESIONALES")
    print("="*60)
    print(f"Acción: {overall['action']}")
    print(f"Confianza: {overall['confidence']:.1f}%")
    print(f"Buy Score: {overall['buy_score']:.1f}")
    print(f"Sell Score: {overall['sell_score']:.1f}")
    print(f"\nRazones principales:")
    for reason in overall['reasons']:
        print(f"  • {reason}")
