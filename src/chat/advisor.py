"""
BTC Trading Advisor
Sistema de asesoramiento inteligente basado en predicciones del modelo
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.risk_manager import RiskManager
from utils.alert_system import AlertSystem
from data.onchain_data import OnChainDataCollector, WhaleDetector
from data.professional_whale_metrics import ProfessionalWhaleMetrics


class TradingAdvisor:
    def __init__(self, predictor, data_collector, feature_engineer, initial_capital=10000):
        """
        Inicializa el asesor de trading

        Args:
            predictor: Instancia del BTCPredictor
            data_collector: Instancia del BTCDataCollector
            feature_engineer: Instancia del FeatureEngineer
            initial_capital: Capital inicial en USDT
        """
        self.predictor = predictor
        self.data_collector = data_collector
        self.feature_engineer = feature_engineer
        self.current_data = None
        self.predictions = None
        self.current_price = None

        # Risk management y alertas
        self.risk_manager = RiskManager(initial_capital=initial_capital)
        self.alert_system = AlertSystem()

        # On-chain data y detección de ballenas
        self.onchain_collector = OnChainDataCollector()
        self.whale_detector = WhaleDetector(whale_threshold=100)
        self.onchain_signals = None

        # Métricas profesionales de ballenas (SOPR, MVRV, Exchange Flows, etc.)
        self.professional_metrics = ProfessionalWhaleMetrics()

    def update_data(self):
        """Actualiza datos del mercado"""
        try:
            # Obtener datos recientes
            df = self.data_collector.fetch_ohlcv(
                timeframe='1h',
                limit=self.predictor.sequence_length + 50
            )

            if df is None:
                return False

            # Agregar características
            self.current_data = self.feature_engineer.create_all_features(df)

            # Obtener precio actual
            self.current_price = self.data_collector.get_current_price()

            return True
        except Exception as e:
            print(f"Error updating data: {e}")
            return False

    def make_prediction(self):
        """Hace predicción con el modelo"""
        if self.current_data is None:
            if not self.update_data():
                return None

        try:
            self.predictions = self.predictor.predict(self.current_data)
            return self.predictions
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None

    def get_onchain_signals(self):
        """
        Obtiene señales on-chain (ballenas, métricas de blockchain)

        Returns:
            dict: Señales on-chain
        """
        try:
            self.onchain_signals = self.onchain_collector.get_onchain_signals()
            return self.onchain_signals
        except Exception as e:
            print(f"Error obteniendo señales on-chain: {e}")
            return None

    def detect_whales(self):
        """
        Detecta movimientos de ballenas

        Returns:
            dict: Análisis de ballenas
        """
        try:
            return self.whale_detector.detect_whale_movements()
        except Exception as e:
            print(f"Error detectando ballenas: {e}")
            return None

    def analyze_trend(self):
        """
        Analiza la tendencia predicha

        Returns:
            dict: Análisis de tendencia
        """
        if self.predictions is None:
            self.make_prediction()

        if self.predictions is None:
            return None

        current = self.current_price
        predictions = self.predictions

        # Calcular cambios
        changes = [(pred - current) / current * 100 for pred in predictions]
        avg_change = np.mean(changes)
        max_change = max(changes)
        min_change = min(changes)

        # Determinar tendencia
        if avg_change > 2:
            trend = "ALCISTA FUERTE"
            confidence = min(abs(avg_change) / 5 * 100, 100)
        elif avg_change > 0.5:
            trend = "ALCISTA"
            confidence = min(abs(avg_change) / 3 * 100, 100)
        elif avg_change < -2:
            trend = "BAJISTA FUERTE"
            confidence = min(abs(avg_change) / 5 * 100, 100)
        elif avg_change < -0.5:
            trend = "BAJISTA"
            confidence = min(abs(avg_change) / 3 * 100, 100)
        else:
            trend = "LATERAL"
            confidence = 50

        return {
            'trend': trend,
            'confidence': round(confidence, 2),
            'avg_change': round(avg_change, 2),
            'max_change': round(max_change, 2),
            'min_change': round(min_change, 2),
            'predictions': predictions.tolist()
        }

    def get_recommendation(self):
        """
        Genera recomendación de trading basada en IA y señales on-chain

        Returns:
            dict: Recomendación detallada con señales on-chain
        """
        analysis = self.analyze_trend()

        if analysis is None:
            return {
                'action': 'ESPERAR',
                'reason': 'No se pudo obtener datos o hacer predicción',
                'confidence': 0
            }

        trend = analysis['trend']
        avg_change = analysis['avg_change']
        confidence = analysis['confidence']

        # Obtener MÉTRICAS PROFESIONALES DE BALLENAS (SOPR, MVRV, Exchange Flows, etc.)
        print("  🐋 Analizando métricas profesionales de ballenas...")
        professional_signals = self.professional_metrics.get_professional_signals(self.current_price)

        # Ajustar confianza basado en métricas profesionales
        onchain_boost = 0
        onchain_reasons = []

        if professional_signals:
            overall_whale = professional_signals.get('overall_signal', {})
            buy_score = overall_whale.get('buy_score', 0)
            sell_score = overall_whale.get('sell_score', 0)

            # Boost basado en señales profesionales
            if 'COMPRAR' in overall_whale.get('action', ''):
                if buy_score > 50:
                    onchain_boost += 20  # Señal institucional fuerte
                    onchain_reasons.append("🏦 Señales institucionales alcistas fuertes")
                elif buy_score > 30:
                    onchain_boost += 15
                    onchain_reasons.append("🏦 Señales institucionales alcistas")
                else:
                    onchain_boost += 10
                    onchain_reasons.append("🏦 Señales institucionales moderadas")

            elif 'VENDER' in overall_whale.get('action', ''):
                if sell_score > 50:
                    onchain_boost -= 20  # Señal bajista fuerte
                    onchain_reasons.append("⚠️ Instituciones distribuyendo")
                else:
                    onchain_boost -= 10
                    onchain_reasons.append("⚠️ Señales de distribución institucional")

            # Agregar razones específicas de métricas
            for reason in overall_whale.get('reasons', []):
                onchain_reasons.append(reason)

        # Ajustar confianza final
        final_confidence = min(confidence + onchain_boost, 95)

        # Lógica de recomendación mejorada con on-chain
        if trend == "ALCISTA FUERTE" and final_confidence > 70:
            action = "COMPRAR FUERTE" if onchain_boost > 15 else "COMPRAR"
            reason = f"Tendencia alcista fuerte detectada. Incremento esperado: {avg_change:.2f}%"
            if onchain_reasons:
                reason += f" | {' | '.join(onchain_reasons)}"
            risk_level = "BAJO"

        elif trend == "ALCISTA" and final_confidence > 60:
            action = "COMPRAR" if onchain_boost > 10 else "COMPRAR (CAUTELOSO)"
            reason = f"Tendencia alcista moderada. Incremento esperado: {avg_change:.2f}%"
            if onchain_reasons:
                reason += f" | {' | '.join(onchain_reasons)}"
            risk_level = "MEDIO" if onchain_boost < 10 else "BAJO"

        elif trend == "BAJISTA FUERTE" and final_confidence > 70:
            # Si hay acumulación de ballenas, reducir señal bajista
            if onchain_boost > 15:
                action = "ESPERAR - Señales Mixtas"
                reason = f"Tendencia bajista pero ballenas acumulando. Esperar confirmación."
                risk_level = "MEDIO"
            else:
                action = "VENDER"
                reason = f"Tendencia bajista fuerte. Caída esperada: {abs(avg_change):.2f}%"
                risk_level = "BAJO"

        elif trend == "BAJISTA" and final_confidence > 60:
            if onchain_boost > 10:
                action = "ESPERAR - Señales Contradictorias"
                reason = "Tendencia bajista pero actividad de ballenas sugiere acumulación"
                risk_level = "MEDIO"
            else:
                action = "VENDER (CAUTELOSO)"
                reason = f"Tendencia bajista moderada. Caída esperada: {abs(avg_change):.2f}%"
                risk_level = "MEDIO"

        else:
            # Mercado lateral - dejarse guiar más por on-chain
            if onchain_boost > 15:
                action = "COMPRAR (SEÑAL ON-CHAIN)"
                reason = f"Mercado lateral pero fuerte actividad de ballenas | {' | '.join(onchain_reasons)}"
                risk_level = "MEDIO"
            elif onchain_boost > 10:
                action = "MONITOREAR - Actividad de Ballenas"
                reason = f"Mercado lateral con actividad de ballenas | {' | '.join(onchain_reasons)}"
                risk_level = "MEDIO"
            else:
                action = "MANTENER/ESPERAR"
                reason = "Mercado lateral sin señales claras. Esperar mejor oportunidad."
                risk_level = "ALTO"

        # Calcular niveles de precio objetivo
        target_price = self.predictions[-1]  # Última predicción
        stop_loss = self.current_price * (0.97 if avg_change > 0 else 1.03)

        return {
            'action': action,
            'reason': reason,
            'confidence': round(final_confidence, 2),
            'ai_confidence': round(confidence, 2),
            'onchain_boost': round(onchain_boost, 2),
            'risk_level': risk_level,
            'current_price': round(self.current_price, 2),
            'target_price': round(target_price, 2),
            'stop_loss': round(stop_loss, 2),
            'expected_change': f"{avg_change:+.2f}%",
            'analysis': analysis,
            'whale_activity': whale_analysis,
            'onchain_signals': onchain
        }

    def get_market_analysis(self):
        """
        Obtiene análisis completo del mercado

        Returns:
            dict: Análisis completo
        """
        if self.current_data is None:
            self.update_data()

        last_row = self.current_data.iloc[-1]

        # Indicadores técnicos
        rsi = last_row.get('rsi_14', None)
        macd = last_row.get('macd', None)
        macd_signal = last_row.get('macd_signal', None)

        # Análisis de RSI
        if rsi:
            if rsi > 70:
                rsi_signal = "SOBRECOMPRADO"
                rsi_meaning = "El mercado puede estar sobrecomprado, posible corrección."
            elif rsi < 30:
                rsi_signal = "SOBREVENDIDO"
                rsi_meaning = "El mercado puede estar sobrevendido, posible rebote."
            else:
                rsi_signal = "NEUTRAL"
                rsi_meaning = "RSI en zona neutral."
        else:
            rsi_signal = "N/A"
            rsi_meaning = "No disponible"

        # Análisis de MACD
        if macd and macd_signal:
            if macd > macd_signal:
                macd_trend = "ALCISTA"
                macd_meaning = "MACD por encima de la señal, momentum alcista."
            else:
                macd_trend = "BAJISTA"
                macd_meaning = "MACD por debajo de la señal, momentum bajista."
        else:
            macd_trend = "N/A"
            macd_meaning = "No disponible"

        return {
            'timestamp': datetime.now().isoformat(),
            'current_price': round(self.current_price, 2),
            'technical_indicators': {
                'rsi': {
                    'value': round(rsi, 2) if rsi else None,
                    'signal': rsi_signal,
                    'meaning': rsi_meaning
                },
                'macd': {
                    'value': round(macd, 4) if macd else None,
                    'signal_value': round(macd_signal, 4) if macd_signal else None,
                    'trend': macd_trend,
                    'meaning': macd_meaning
                }
            }
        }

    def answer_question(self, question):
        """
        Responde preguntas del usuario

        Args:
            question: Pregunta del usuario

        Returns:
            str: Respuesta
        """
        question = question.lower()

        # Actualizar datos si es necesario
        if self.current_data is None:
            self.update_data()
            self.make_prediction()

        if "precio" in question or "cuanto" in question or "valor" in question:
            return f"El precio actual de BTC/USDT es ${self.current_price:,.2f}"

        elif "comprar" in question or "vender" in question or "recomienda" in question:
            rec = self.get_recommendation()
            response = f"🎯 RECOMENDACIÓN: {rec['action']}\n\n"
            response += f"📊 Confianza: {rec['confidence']:.1f}%\n"
            response += f"⚠️ Nivel de Riesgo: {rec['risk_level']}\n\n"
            response += f"💰 Precio Actual: ${rec['current_price']:,.2f}\n"
            response += f"🎯 Precio Objetivo: ${rec['target_price']:,.2f}\n"
            response += f"🛡️ Stop Loss: ${rec['stop_loss']:,.2f}\n\n"
            response += f"📈 Cambio Esperado: {rec['expected_change']}\n\n"
            response += f"💡 Razón: {rec['reason']}"
            return response

        elif "tendencia" in question or "prediccion" in question or "subir" in question or "bajar" in question:
            analysis = self.analyze_trend()
            response = f"📊 ANÁLISIS DE TENDENCIA\n\n"
            response += f"Tendencia: {analysis['trend']}\n"
            response += f"Confianza: {analysis['confidence']:.1f}%\n"
            response += f"Cambio promedio esperado: {analysis['avg_change']:+.2f}%\n"
            response += f"Rango: {analysis['min_change']:.2f}% a {analysis['max_change']:.2f}%\n\n"
            response += f"Predicciones para las próximas {len(self.predictions)} horas:\n"
            for i, pred in enumerate(analysis['predictions'], 1):
                change = (pred - self.current_price) / self.current_price * 100
                response += f"  {i}h: ${pred:,.2f} ({change:+.2f}%)\n"
            return response

        elif "indicador" in question or "rsi" in question or "macd" in question:
            market = self.get_market_analysis()
            response = f"📈 INDICADORES TÉCNICOS\n\n"
            response += f"Precio: ${market['current_price']:,.2f}\n\n"

            rsi_data = market['technical_indicators']['rsi']
            if rsi_data['value']:
                response += f"RSI(14): {rsi_data['value']:.2f}\n"
                response += f"Señal: {rsi_data['signal']}\n"
                response += f"{rsi_data['meaning']}\n\n"

            macd_data = market['technical_indicators']['macd']
            if macd_data['value']:
                response += f"MACD: {macd_data['value']:.4f}\n"
                response += f"Señal: {macd_data['signal_value']:.4f}\n"
                response += f"Tendencia: {macd_data['trend']}\n"
                response += f"{macd_data['meaning']}"

            return response

        elif "ballena" in question or "whale" in question or "onchain" in question or "on-chain" in question or "on chain" in question or "metricas" in question or "profesional" in question:
            # Obtener MÉTRICAS PROFESIONALES DE BALLENAS
            prof_signals = self.professional_metrics.get_professional_signals(self.current_price)

            response = "🏦 MÉTRICAS PROFESIONALES DE BALLENAS\n"
            response += "=" * 50 + "\n\n"

            # Señal general
            if prof_signals:
                overall = prof_signals.get('overall_signal', {})
                response += f"🎯 SEÑAL INSTITUCIONAL: {overall.get('action', 'N/A')}\n"
                response += f"📊 Confianza: {overall.get('confidence', 0):.1f}%\n"
                response += f"📈 Buy Score: {overall.get('buy_score', 0):.1f}\n"
                response += f"📉 Sell Score: {overall.get('sell_score', 0):.1f}\n\n"

                response += "💡 RAZONES PRINCIPALES:\n"
                for reason in overall.get('reasons', []):
                    response += f"  • {reason}\n"

                # MVRV
                if prof_signals.get('mvrv'):
                    mvrv = prof_signals['mvrv']
                    response += f"\n📊 MVRV (Market Value / Realized Value)\n"
                    response += f"  Valor: {mvrv['value']:.2f}\n"
                    response += f"  Señal: {mvrv['signal']}\n"
                    response += f"  Acción: {mvrv['action']}\n"
                    response += f"  {mvrv['reason']}\n"

                # SOPR
                if prof_signals.get('sopr'):
                    sopr = prof_signals['sopr']
                    response += f"\n💎 SOPR (Spent Output Profit Ratio)\n"
                    response += f"  Valor: {sopr['value']:.3f}\n"
                    response += f"  Señal: {sopr['signal']}\n"
                    response += f"  Acción: {sopr['action']}\n"
                    response += f"  {sopr['interpretation']}\n"

                # Large Transactions
                if prof_signals.get('large_transactions'):
                    large_tx = prof_signals['large_transactions']
                    response += f"\n🐋 TRANSACCIONES GRANDES (>100 BTC)\n"
                    response += f"  Ballenas detectadas: {large_tx['whale_count']}\n"
                    response += f"  Volumen total: {large_tx['total_volume_btc']:,.2f} BTC\n"
                    response += f"  Señal: {large_tx['signal']}\n"
                    response += f"  {large_tx['reason']}\n"

                # Exchange Flows
                if prof_signals.get('exchange_flows'):
                    flows = prof_signals['exchange_flows']
                    response += f"\n⛓️ EXCHANGE FLOWS\n"
                    response += f"  Volumen 24h: {flows['trade_volume_btc']:,.0f} BTC\n"
                    response += f"  Flujo: {flows['flow_signal']}\n"
                    response += f"  Señal: {flows['signal']}\n"
                    response += f"  {flows['reason']}\n"

                # Active Addresses
                if prof_signals.get('active_addresses'):
                    active = prof_signals['active_addresses']
                    response += f"\n📍 ACTIVE ADDRESSES\n"
                    response += f"  Estimadas: {active['estimated_active']:,.0f}\n"
                    response += f"  Señal: {active['signal']}\n"
                    response += f"  {active['reason']}\n"

            return response

        elif "capital" in question or "balance" in question or "portafolio" in question:
            stats = self.risk_manager.get_performance_stats()
            response = f"💰 ESTADO DEL PORTAFOLIO\n\n"
            response += f"Capital Inicial: ${stats['initial_capital']:,.2f}\n"
            response += f"Capital Actual: ${stats['current_capital']:,.2f}\n"
            response += f"P&L Total: ${stats['total_pnl']:,.2f} ({stats['total_pnl_pct']:+.2f}%)\n\n"

            if stats['total_trades'] > 0:
                response += f"📊 ESTADÍSTICAS\n"
                response += f"Total Trades: {stats['total_trades']}\n"
                response += f"Win Rate: {stats['win_rate']:.2f}%\n"
                response += f"Ganancia Promedio: ${stats['avg_win']:,.2f}\n"
                response += f"Pérdida Promedio: ${stats['avg_loss']:,.2f}\n"
                response += f"Profit Factor: {stats['profit_factor']:.2f}\n"
                response += f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}"

            return response

        elif "riesgo" in question or "position size" in question or "cuanto comprar" in question:
            rec = self.get_recommendation()
            entry_price = self.current_price
            stop_loss = rec['stop_loss']

            position_size = self.risk_manager.calculate_position_size(
                entry_price,
                stop_loss,
                confidence=rec['confidence']/100
            )

            response = f"📊 CÁLCULO DE POSICIÓN\n\n"
            response += f"💰 Precio de Entrada: ${entry_price:,.2f}\n"
            response += f"🛡️ Stop Loss: ${stop_loss:,.2f}\n\n"
            response += f"Tamaño de Posición:\n"
            response += f"  BTC: {position_size['position_size_btc']:.8f}\n"
            response += f"  USDT: ${position_size['position_size_usdt']:,.2f}\n\n"
            response += f"Capital en Riesgo: ${position_size['capital_at_risk']:,.2f} ({position_size['risk_percentage']:.2f}%)\n"
            response += f"Riesgo por Unidad: {position_size['risk_per_unit']:.2f}%"

            return response

        elif "alerta" in question and "crear" in question:
            return """🔔 CREAR ALERTAS

Para crear una alerta, usa:
- "Crear alerta de precio X" - Alerta cuando BTC llegue a precio X
- "Crear alerta RSI bajo 30" - Alerta cuando RSI esté bajo 30
- "Crear alerta confianza alta" - Alerta cuando predicción tenga confianza >75%

Ejemplos:
- "Crear alerta de precio 50000"
- "Crear alerta RSI bajo 30"
- "Crear alerta confianza 80"
"""

        elif "alerta" in question and "ver" in question:
            active = self.alert_system.get_active_alerts()
            if not active:
                return "No tienes alertas activas."

            response = "🔔 ALERTAS ACTIVAS\n\n"
            for i, alert in enumerate(active, 1):
                response += f"{i}. {alert['message']}\n"
            return response

        elif "performance" in question or "rendimiento" in question or "estadisticas" in question:
            stats = self.risk_manager.get_performance_stats()
            risk_status = self.risk_manager.check_risk_limits()

            response = f"📊 RENDIMIENTO Y ESTADÍSTICAS\n\n"
            response += f"💰 Capital: ${stats['current_capital']:,.2f} ({stats['capital_pct']:.1f}%)\n"
            response += f"📈 P&L: ${stats['total_pnl']:,.2f} ({stats['total_pnl_pct']:+.2f}%)\n\n"

            if stats['total_trades'] > 0:
                response += f"TRADES\n"
                response += f"  Total: {stats['total_trades']}\n"
                response += f"  Ganadores: {stats['winning_trades']} ✅\n"
                response += f"  Perdedores: {stats['losing_trades']} ❌\n"
                response += f"  Win Rate: {stats['win_rate']:.2f}%\n\n"

                response += f"MÉTRICAS\n"
                response += f"  Ganancia Promedio: ${stats['avg_win']:,.2f}\n"
                response += f"  Pérdida Promedio: ${stats['avg_loss']:,.2f}\n"
                response += f"  Profit Factor: {stats['profit_factor']:.2f}\n"
                response += f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}\n\n"

            response += f"⚠️ RIESGO\n"
            response += f"  Drawdown: {risk_status['drawdown']:.2f}%\n"
            response += f"  Pérdida Diaria: {risk_status['daily_loss_pct']:.2f}%\n"
            response += f"  Puede Operar: {'✅ Sí' if risk_status['can_trade'] else '❌ No'}"

            if risk_status['warnings']:
                response += "\n\n⚠️ ADVERTENCIAS:\n"
                for warning in risk_status['warnings']:
                    response += f"  - {warning}\n"

            return response

        elif "ayuda" in question or "que puedes" in question or "comandos" in question:
            return """🤖 COMANDOS DISPONIBLES:

ANÁLISIS Y PREDICCIONES:
1. "¿Cuál es el precio actual?" - Precio actual de BTC/USDT
2. "¿Debería comprar/vender?" - Recomendación de trading (incluye señales on-chain)
3. "¿Cuál es la tendencia?" - Análisis de tendencia y predicciones
4. "¿Cómo están los indicadores?" - Indicadores técnicos (RSI, MACD)
5. "Análisis completo" - Reporte detallado del mercado

MÉTRICAS PROFESIONALES DE BALLENAS:
6. "Ballenas" / "Métricas profesionales" - Análisis institucional completo
   ├─ SOPR (Spent Output Profit Ratio)
   ├─ MVRV (Market Value / Realized Value)
   ├─ Exchange Flows (flujos de exchanges)
   ├─ Large Transactions (>100 BTC)
   └─ Active Addresses (actividad de red)

GESTIÓN DE RIESGO:
7. "¿Cuánto comprar?" / "Position size" - Cálculo de tamaño de posición
8. "Balance" / "Capital" - Estado del portafolio
9. "Performance" / "Estadísticas" - Métricas de rendimiento

ALERTAS:
10. "Crear alerta" - Información sobre alertas
11. "Ver alertas" - Alertas activas

12. "Actualizar" - Actualiza datos del mercado
13. "Ayuda" - Muestra este mensaje

💡 Puedes hacer preguntas en lenguaje natural!
🏦 Usa métricas profesionales de instituciones (SOPR, MVRV, etc.)
🐋 Las recomendaciones incluyen análisis institucional automáticamente!"""

        elif "analisis completo" in question or "reporte" in question:
            rec = self.get_recommendation()
            market = self.get_market_analysis()

            response = "📊 ANÁLISIS COMPLETO DE BTC/USDT\n"
            response += "=" * 50 + "\n\n"

            response += f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            response += f"💰 Precio Actual: ${market['current_price']:,.2f}\n\n"

            response += "🎯 RECOMENDACIÓN\n"
            response += f"Acción: {rec['action']}\n"
            response += f"Confianza: {rec['confidence']:.1f}%\n"
            response += f"Riesgo: {rec['risk_level']}\n"
            response += f"Cambio Esperado: {rec['expected_change']}\n"
            response += f"Razón: {rec['reason']}\n\n"

            response += "📈 OBJETIVOS\n"
            response += f"Precio Objetivo: ${rec['target_price']:,.2f}\n"
            response += f"Stop Loss: ${rec['stop_loss']:,.2f}\n\n"

            response += "📊 INDICADORES TÉCNICOS\n"
            rsi_data = market['technical_indicators']['rsi']
            if rsi_data['value']:
                response += f"RSI(14): {rsi_data['value']:.2f} - {rsi_data['signal']}\n"

            macd_data = market['technical_indicators']['macd']
            if macd_data['value']:
                response += f"MACD: {macd_data['trend']}\n"

            return response

        else:
            return "No entendí tu pregunta. Escribe 'ayuda' para ver los comandos disponibles."


if __name__ == "__main__":
    print("Testing TradingAdvisor...")
    print("This requires a trained model. Run btc_predictor.py first.")
