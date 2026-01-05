"""
Alert System
Sistema de alertas en tiempo real para condiciones de mercado y trading
"""
from datetime import datetime
import json
import os


class AlertSystem:
    def __init__(self, alerts_file='data/alerts.json'):
        """
        Inicializa el sistema de alertas

        Args:
            alerts_file: Archivo para guardar alertas
        """
        self.alerts_file = alerts_file
        self.active_alerts = []
        self.alert_history = []
        self.load_alerts()

    def load_alerts(self):
        """Carga alertas guardadas"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    self.active_alerts = data.get('active', [])
                    self.alert_history = data.get('history', [])
            except:
                pass

    def save_alerts(self):
        """Guarda alertas en archivo"""
        os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
        with open(self.alerts_file, 'w') as f:
            json.dump({
                'active': self.active_alerts,
                'history': self.alert_history
            }, f, indent=2)

    def create_price_alert(self, target_price, direction='above', message=None):
        """
        Crea alerta de precio

        Args:
            target_price: Precio objetivo
            direction: 'above' o 'below'
            message: Mensaje personalizado

        Returns:
            dict: Alerta creada
        """
        alert = {
            'id': len(self.active_alerts) + len(self.alert_history) + 1,
            'type': 'price',
            'target_price': target_price,
            'direction': direction,
            'message': message or f"BTC {'por encima de' if direction == 'above' else 'por debajo de'} ${target_price:,.2f}",
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.active_alerts.append(alert)
        self.save_alerts()
        return alert

    def create_indicator_alert(self, indicator, condition, value, message=None):
        """
        Crea alerta de indicador técnico

        Args:
            indicator: Nombre del indicador (RSI, MACD, etc.)
            condition: 'above', 'below', 'crosses_above', 'crosses_below'
            value: Valor objetivo
            message: Mensaje personalizado

        Returns:
            dict: Alerta creada
        """
        alert = {
            'id': len(self.active_alerts) + len(self.alert_history) + 1,
            'type': 'indicator',
            'indicator': indicator,
            'condition': condition,
            'value': value,
            'message': message or f"{indicator} {condition} {value}",
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.active_alerts.append(alert)
        self.save_alerts()
        return alert

    def create_prediction_alert(self, confidence_threshold=75, trend=None, message=None):
        """
        Crea alerta basada en predicción

        Args:
            confidence_threshold: Umbral mínimo de confianza
            trend: Tendencia esperada ('alcista', 'bajista')
            message: Mensaje personalizado

        Returns:
            dict: Alerta creada
        """
        alert = {
            'id': len(self.active_alerts) + len(self.alert_history) + 1,
            'type': 'prediction',
            'confidence_threshold': confidence_threshold,
            'trend': trend,
            'message': message or f"Predicción con confianza >{confidence_threshold}%",
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        self.active_alerts.append(alert)
        self.save_alerts()
        return alert

    def check_price_alerts(self, current_price):
        """
        Verifica alertas de precio

        Args:
            current_price: Precio actual

        Returns:
            list: Alertas disparadas
        """
        triggered = []

        for alert in self.active_alerts[:]:
            if alert['type'] == 'price':
                should_trigger = False

                if alert['direction'] == 'above' and current_price >= alert['target_price']:
                    should_trigger = True
                elif alert['direction'] == 'below' and current_price <= alert['target_price']:
                    should_trigger = True

                if should_trigger:
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['triggered_price'] = current_price
                    alert['status'] = 'triggered'
                    triggered.append(alert)

                    # Mover a historial
                    self.alert_history.append(alert)
                    self.active_alerts.remove(alert)

        if triggered:
            self.save_alerts()

        return triggered

    def check_indicator_alerts(self, indicators):
        """
        Verifica alertas de indicadores

        Args:
            indicators: Dict con valores de indicadores

        Returns:
            list: Alertas disparadas
        """
        triggered = []

        for alert in self.active_alerts[:]:
            if alert['type'] == 'indicator':
                indicator_name = alert['indicator'].lower()

                if indicator_name in indicators:
                    current_value = indicators[indicator_name]
                    should_trigger = False

                    if alert['condition'] == 'above' and current_value >= alert['value']:
                        should_trigger = True
                    elif alert['condition'] == 'below' and current_value <= alert['value']:
                        should_trigger = True

                    if should_trigger:
                        alert['triggered_at'] = datetime.now().isoformat()
                        alert['triggered_value'] = current_value
                        alert['status'] = 'triggered'
                        triggered.append(alert)

                        # Mover a historial
                        self.alert_history.append(alert)
                        self.active_alerts.remove(alert)

        if triggered:
            self.save_alerts()

        return triggered

    def check_prediction_alerts(self, prediction_data):
        """
        Verifica alertas de predicción

        Args:
            prediction_data: Datos de predicción con confianza y tendencia

        Returns:
            list: Alertas disparadas
        """
        triggered = []

        for alert in self.active_alerts[:]:
            if alert['type'] == 'prediction':
                should_trigger = False
                confidence = prediction_data.get('confidence', 0)
                trend = prediction_data.get('trend', '').lower()

                if confidence >= alert['confidence_threshold']:
                    if alert['trend'] is None or alert['trend'].lower() in trend:
                        should_trigger = True

                if should_trigger:
                    alert['triggered_at'] = datetime.now().isoformat()
                    alert['triggered_confidence'] = confidence
                    alert['triggered_trend'] = trend
                    alert['status'] = 'triggered'
                    triggered.append(alert)

                    # Mover a historial
                    self.alert_history.append(alert)
                    self.active_alerts.remove(alert)

        if triggered:
            self.save_alerts()

        return triggered

    def get_active_alerts(self):
        """Obtiene alertas activas"""
        return self.active_alerts

    def get_alert_history(self, limit=50):
        """
        Obtiene historial de alertas

        Args:
            limit: Número máximo de alertas a retornar

        Returns:
            list: Historial de alertas
        """
        return self.alert_history[-limit:]

    def delete_alert(self, alert_id):
        """
        Elimina una alerta activa

        Args:
            alert_id: ID de la alerta

        Returns:
            bool: True si se eliminó
        """
        for i, alert in enumerate(self.active_alerts):
            if alert['id'] == alert_id:
                self.active_alerts.pop(i)
                self.save_alerts()
                return True
        return False

    def format_alert_message(self, alert):
        """
        Formatea mensaje de alerta para mostrar

        Args:
            alert: Alerta disparada

        Returns:
            str: Mensaje formateado
        """
        msg = f"🔔 ALERTA DISPARADA!\n\n"
        msg += f"Tipo: {alert['type'].upper()}\n"
        msg += f"Mensaje: {alert['message']}\n"

        if alert['type'] == 'price':
            msg += f"Precio objetivo: ${alert['target_price']:,.2f}\n"
            msg += f"Precio actual: ${alert.get('triggered_price', 0):,.2f}\n"

        elif alert['type'] == 'indicator':
            msg += f"Indicador: {alert['indicator']}\n"
            msg += f"Valor objetivo: {alert['value']}\n"
            msg += f"Valor actual: {alert.get('triggered_value', 0)}\n"

        elif alert['type'] == 'prediction':
            msg += f"Confianza: {alert.get('triggered_confidence', 0)}%\n"
            msg += f"Tendencia: {alert.get('triggered_trend', 'N/A')}\n"

        msg += f"\nCreada: {alert['created_at']}\n"
        msg += f"Disparada: {alert.get('triggered_at', 'N/A')}"

        return msg


if __name__ == "__main__":
    # Test alert system
    alerts = AlertSystem()

    # Crear algunas alertas de prueba
    alerts.create_price_alert(50000, 'above')
    alerts.create_price_alert(40000, 'below')
    alerts.create_indicator_alert('RSI', 'below', 30, "RSI en sobreventa")
    alerts.create_prediction_alert(80, 'alcista')

    print("Alertas activas:")
    for alert in alerts.get_active_alerts():
        print(f"  - {alert['message']}")

    # Simular verificación
    triggered = alerts.check_price_alerts(50100)
    if triggered:
        print(f"\nAlertas disparadas: {len(triggered)}")
        for alert in triggered:
            print(alerts.format_alert_message(alert))
