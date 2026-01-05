"""
On-Chain Data Collector
Recopila datos on-chain de Bitcoin: movimientos de ballenas, métricas de blockchain, etc.
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


class OnChainDataCollector:
    def __init__(self):
        """Inicializa el recopilador de datos on-chain"""
        self.whale_threshold = 100  # BTC - Define qué es una ballena
        self.base_urls = {
            'blockchain': 'https://blockchain.info',
            'mempool': 'https://mempool.space/api',
            'blockchair': 'https://api.blockchair.com/bitcoin'
        }

    def get_large_transactions(self, min_btc=100, hours=24):
        """
        Obtiene transacciones grandes (movimientos de ballenas)

        Args:
            min_btc: BTC mínimo para considerar transacción grande
            hours: Horas hacia atrás

        Returns:
            list: Transacciones grandes detectadas
        """
        try:
            # Usar API de Blockchain.info para transacciones recientes
            url = f"{self.base_urls['blockchain']}/unconfirmed-transactions?format=json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                large_txs = []

                for tx in data.get('txs', [])[:100]:  # Últimas 100 transacciones
                    # Calcular valor total en BTC
                    total_btc = sum([out['value'] for out in tx.get('out', [])]) / 1e8

                    if total_btc >= min_btc:
                        large_txs.append({
                            'hash': tx.get('hash'),
                            'time': datetime.fromtimestamp(tx.get('time', 0)),
                            'size_btc': round(total_btc, 2),
                            'inputs': len(tx.get('inputs', [])),
                            'outputs': len(tx.get('out', []))
                        })

                return large_txs

        except Exception as e:
            print(f"Error obteniendo transacciones grandes: {e}")

        return []

    def get_exchange_flows(self):
        """
        Detecta flujos hacia/desde exchanges (señal de venta/compra de ballenas)

        Returns:
            dict: Flujos de exchange
        """
        try:
            # Obtener datos de mempool
            url = f"{self.base_urls['mempool']}/v1/mining/pools/24h"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                pools_data = response.json()

                return {
                    'total_blocks_24h': pools_data.get('blockCount', 0),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error obteniendo flujos de exchange: {e}")

        return {}

    def get_network_metrics(self):
        """
        Obtiene métricas de la red Bitcoin

        Returns:
            dict: Métricas de red
        """
        try:
            # Hash rate y dificultad
            stats_url = f"{self.base_urls['blockchain']}/stats?format=json"
            response = requests.get(stats_url, timeout=10)

            if response.status_code == 200:
                stats = response.json()

                return {
                    'hash_rate': stats.get('hash_rate', 0),
                    'difficulty': stats.get('difficulty', 0),
                    'total_btc': stats.get('totalbc', 0) / 1e8,
                    'market_price_usd': stats.get('market_price_usd', 0),
                    'trade_volume_btc': stats.get('trade_volume_btc', 0),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error obteniendo métricas de red: {e}")

        return {}

    def get_mempool_size(self):
        """
        Obtiene tamaño del mempool (congestión de red)

        Returns:
            dict: Datos del mempool
        """
        try:
            url = f"{self.base_urls['mempool']}/mempool"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                mempool_data = response.json()

                return {
                    'size_bytes': mempool_data.get('size', 0),
                    'tx_count': mempool_data.get('count', 0),
                    'vsize': mempool_data.get('vsize', 0),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"Error obteniendo mempool: {e}")

        return {}

    def analyze_whale_activity(self, large_txs):
        """
        Analiza actividad de ballenas

        Args:
            large_txs: Lista de transacciones grandes

        Returns:
            dict: Análisis de actividad de ballenas
        """
        if not large_txs:
            return {
                'whale_count': 0,
                'total_volume_btc': 0,
                'avg_size_btc': 0,
                'signal': 'NEUTRAL',
                'confidence': 0
            }

        total_volume = sum([tx['size_btc'] for tx in large_txs])
        avg_size = total_volume / len(large_txs) if large_txs else 0

        # Determinar señal
        if len(large_txs) > 10:  # Muchas transacciones grandes
            if avg_size > 200:  # Transacciones muy grandes
                signal = 'ACUMULACIÓN FUERTE'
                confidence = 85
            else:
                signal = 'ACUMULACIÓN'
                confidence = 70
        elif len(large_txs) > 5:
            signal = 'ACUMULACIÓN MODERADA'
            confidence = 60
        else:
            signal = 'NEUTRAL'
            confidence = 50

        return {
            'whale_count': len(large_txs),
            'total_volume_btc': round(total_volume, 2),
            'avg_size_btc': round(avg_size, 2),
            'signal': signal,
            'confidence': confidence,
            'largest_tx': max([tx['size_btc'] for tx in large_txs]) if large_txs else 0
        }

    def get_onchain_signals(self):
        """
        Obtiene todas las señales on-chain combinadas

        Returns:
            dict: Señales on-chain completas
        """
        print("📊 Obteniendo señales on-chain...")

        # Obtener datos
        large_txs = self.get_large_transactions(min_btc=self.whale_threshold)
        network_metrics = self.get_network_metrics()
        mempool_data = self.get_mempool_size()
        exchange_flows = self.get_exchange_flows()

        # Analizar ballenas
        whale_analysis = self.analyze_whale_activity(large_txs)

        # Combinar todo
        signals = {
            'whale_activity': whale_analysis,
            'network_metrics': network_metrics,
            'mempool': mempool_data,
            'exchange_flows': exchange_flows,
            'timestamp': datetime.now().isoformat()
        }

        # Generar señal principal
        overall_signal = self._generate_overall_signal(signals)
        signals['overall_signal'] = overall_signal

        return signals

    def _generate_overall_signal(self, signals):
        """
        Genera señal general basada en todas las métricas on-chain

        Args:
            signals: Todas las señales on-chain

        Returns:
            dict: Señal general
        """
        whale_signal = signals['whale_activity']['signal']
        whale_confidence = signals['whale_activity']['confidence']

        # Análisis de mempool
        mempool_congestion = signals['mempool'].get('tx_count', 0)

        # Señal basada en congestión
        if mempool_congestion > 50000:
            mempool_signal = 'ALTA_DEMANDA'
            mempool_conf = 70
        elif mempool_congestion > 20000:
            mempool_signal = 'DEMANDA_MODERADA'
            mempool_conf = 60
        else:
            mempool_signal = 'BAJA_DEMANDA'
            mempool_conf = 50

        # Combinar señales
        if 'ACUMULACIÓN' in whale_signal and mempool_signal in ['ALTA_DEMANDA', 'DEMANDA_MODERADA']:
            action = 'COMPRAR - Ballenas Acumulando'
            confidence = min((whale_confidence + mempool_conf) / 2, 90)
        elif whale_signal == 'NEUTRAL':
            action = 'ESPERAR - Sin Actividad Clara de Ballenas'
            confidence = 50
        else:
            action = 'MONITOREAR - Señales Mixtas'
            confidence = 60

        return {
            'action': action,
            'confidence': round(confidence, 2),
            'whale_signal': whale_signal,
            'mempool_signal': mempool_signal,
            'reasoning': self._generate_reasoning(whale_signal, mempool_signal)
        }

    def _generate_reasoning(self, whale_signal, mempool_signal):
        """Genera explicación de la señal"""
        reasons = []

        if 'ACUMULACIÓN' in whale_signal:
            reasons.append("Ballenas están acumulando BTC (transacciones grandes detectadas)")

        if mempool_signal == 'ALTA_DEMANDA':
            reasons.append("Alta congestión en mempool indica fuerte demanda")
        elif mempool_signal == 'DEMANDA_MODERADA':
            reasons.append("Demanda moderada en la red")

        return ' | '.join(reasons) if reasons else "Sin señales claras"


class WhaleDetector:
    """Detector especializado de movimientos de ballenas"""

    def __init__(self, whale_threshold=100):
        """
        Inicializa detector de ballenas

        Args:
            whale_threshold: BTC mínimo para considerar ballena
        """
        self.whale_threshold = whale_threshold
        self.collector = OnChainDataCollector()

    def detect_whale_movements(self):
        """
        Detecta y analiza movimientos de ballenas

        Returns:
            dict: Análisis detallado de ballenas
        """
        large_txs = self.collector.get_large_transactions(self.whale_threshold)

        if not large_txs:
            return {
                'detected': False,
                'message': 'No se detectaron movimientos de ballenas en las últimas horas',
                'recommendation': 'NEUTRAL'
            }

        # Análisis
        analysis = self.collector.analyze_whale_activity(large_txs)

        # Generar recomendación
        if analysis['whale_count'] > 10:
            recommendation = 'COMPRAR - Fuerte Actividad de Ballenas'
            message = f"⚠️ ALERTA: {analysis['whale_count']} transacciones grandes detectadas!\n"
            message += f"Volumen total: {analysis['total_volume_btc']:,.2f} BTC\n"
            message += f"Transacción más grande: {analysis['largest_tx']:,.2f} BTC\n"
            message += f"Señal: {analysis['signal']}"
        elif analysis['whale_count'] > 5:
            recommendation = 'MONITOREAR - Actividad Moderada de Ballenas'
            message = f"📊 {analysis['whale_count']} movimientos grandes detectados\n"
            message += f"Volumen: {analysis['total_volume_btc']:,.2f} BTC"
        else:
            recommendation = 'NEUTRAL'
            message = f"Actividad normal: {analysis['whale_count']} transacciones grandes"

        return {
            'detected': True,
            'whale_count': analysis['whale_count'],
            'total_volume': analysis['total_volume_btc'],
            'signal': analysis['signal'],
            'confidence': analysis['confidence'],
            'recommendation': recommendation,
            'message': message,
            'transactions': large_txs[:5]  # Últimas 5 para detalle
        }


if __name__ == "__main__":
    # Test on-chain data collector
    print("Testing On-Chain Data Collector...\n")

    collector = OnChainDataCollector()

    # Test transacciones grandes
    print("1. Buscando transacciones grandes de ballenas...")
    large_txs = collector.get_large_transactions(min_btc=50)
    print(f"   Encontradas: {len(large_txs)} transacciones grandes\n")

    # Test métricas de red
    print("2. Obteniendo métricas de red...")
    network = collector.get_network_metrics()
    if network:
        print(f"   Hash Rate: {network.get('hash_rate', 0):,.0f}")
        print(f"   Market Price: ${network.get('market_price_usd', 0):,.2f}\n")

    # Test señales completas
    print("3. Generando señales on-chain completas...")
    signals = collector.get_onchain_signals()

    overall = signals.get('overall_signal', {})
    print(f"\n🎯 SEÑAL ON-CHAIN: {overall.get('action', 'N/A')}")
    print(f"   Confianza: {overall.get('confidence', 0)}%")
    print(f"   Razón: {overall.get('reasoning', 'N/A')}")

    # Test detector de ballenas
    print("\n4. Detector de Ballenas...")
    whale_detector = WhaleDetector(whale_threshold=100)
    whale_analysis = whale_detector.detect_whale_movements()
    print(f"\n{whale_analysis['message']}")
    print(f"Recomendación: {whale_analysis['recommendation']}")
