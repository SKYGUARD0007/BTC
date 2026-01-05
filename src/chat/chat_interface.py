"""
Chat Interface for BTC Trading Advisor
Interfaz de chat interactiva para asesoramiento de trading
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.btc_predictor import BTCPredictor
from data.data_collector import BTCDataCollector
from data.feature_engineering import FeatureEngineer
from chat.advisor import TradingAdvisor


class ChatInterface:
    def __init__(self):
        """Inicializa la interfaz de chat"""
        self.advisor = None
        self.setup_complete = False

    def setup(self):
        """Configura el sistema"""
        print("🚀 Iniciando sistema de predicción BTC/USDT...")
        print("=" * 60)

        try:
            # Cargar modelo
            print("\n1️⃣ Cargando modelo de predicción...")
            self.predictor = BTCPredictor()

            if os.path.exists('models/btc_predictor_model.h5'):
                self.predictor.load('models/btc_predictor')
                print("✅ Modelo cargado exitosamente")
            else:
                print("❌ No se encontró modelo entrenado.")
                print("Por favor, ejecuta primero:")
                print("  python src/data/data_collector.py")
                print("  python src/data/feature_engineering.py")
                print("  python src/models/btc_predictor.py")
                return False

            # Inicializar recopilador de datos
            print("\n2️⃣ Conectando con Binance...")
            self.data_collector = BTCDataCollector()
            print("✅ Conexión establecida")

            # Inicializar ingeniero de características
            print("\n3️⃣ Inicializando ingeniero de características...")
            self.feature_engineer = FeatureEngineer()
            print("✅ Listo")

            # Crear asesor
            print("\n4️⃣ Inicializando asesor de trading...")
            self.advisor = TradingAdvisor(
                self.predictor,
                self.data_collector,
                self.feature_engineer
            )
            print("✅ Asesor listo")

            # Actualizar datos iniciales
            print("\n5️⃣ Obteniendo datos del mercado...")
            if self.advisor.update_data():
                print("✅ Datos actualizados")
                self.advisor.make_prediction()
                print("✅ Predicción inicial completada")
            else:
                print("⚠️ No se pudieron obtener datos. Verifica tu conexión.")
                return False

            self.setup_complete = True
            return True

        except Exception as e:
            print(f"\n❌ Error durante la configuración: {e}")
            return False

    def print_header(self):
        """Imprime el encabezado del chat"""
        print("\n" + "=" * 60)
        print("🤖 ASISTENTE DE TRADING BTC/USDT")
        print("=" * 60)
        print("\nEscribe 'ayuda' para ver comandos disponibles")
        print("Escribe 'salir' para terminar la sesión")
        print("=" * 60 + "\n")

    def format_response(self, response):
        """
        Formatea la respuesta para mejor visualización

        Args:
            response: Respuesta del advisor

        Returns:
            str: Respuesta formateada
        """
        lines = response.split('\n')
        formatted_lines = []

        for line in lines:
            if line.strip():
                formatted_lines.append(f"  {line}")
            else:
                formatted_lines.append("")

        return '\n'.join(formatted_lines)

    def run(self):
        """Ejecuta el chat interactivo"""
        # Setup
        if not self.setup():
            return

        # Imprimir encabezado
        self.print_header()

        # Mostrar información inicial
        try:
            current_price = self.advisor.current_price
            print(f"💰 Precio actual de BTC/USDT: ${current_price:,.2f}\n")
        except:
            pass

        # Loop principal del chat
        while True:
            try:
                # Obtener input del usuario
                user_input = input("Tú: ").strip()

                if not user_input:
                    continue

                # Comandos especiales
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("\n👋 ¡Hasta luego! Buena suerte con tus trades.")
                    break

                if user_input.lower() in ['actualizar', 'refresh', 'update']:
                    print("\n🔄 Actualizando datos...")
                    if self.advisor.update_data():
                        self.advisor.make_prediction()
                        print("✅ Datos actualizados correctamente\n")
                        current_price = self.advisor.current_price
                        print(f"💰 Precio actual: ${current_price:,.2f}\n")
                    else:
                        print("❌ Error al actualizar datos\n")
                    continue

                # Procesar pregunta
                print()  # Línea en blanco
                response = self.advisor.answer_question(user_input)

                # Mostrar respuesta
                print("🤖 Asistente:")
                print(self.format_response(response))
                print()  # Línea en blanco

            except KeyboardInterrupt:
                print("\n\n👋 Sesión interrumpida. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                continue


def main():
    """Función principal"""
    chat = ChatInterface()
    chat.run()


if __name__ == "__main__":
    main()
