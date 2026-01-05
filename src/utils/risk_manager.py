"""
Risk Management System
Sistema avanzado de gestión de riesgo para trading
"""
import numpy as np
from datetime import datetime


class RiskManager:
    def __init__(self, initial_capital=10000, max_risk_per_trade=0.02, max_portfolio_risk=0.06):
        """
        Inicializa el gestor de riesgo

        Args:
            initial_capital: Capital inicial en USDT
            max_risk_per_trade: Riesgo máximo por trade (% del capital)
            max_portfolio_risk: Riesgo máximo total del portafolio
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.open_positions = []
        self.trade_history = []
        self.daily_pnl = []

    def calculate_position_size(self, entry_price, stop_loss_price, confidence=1.0):
        """
        Calcula el tamaño de posición óptimo basado en riesgo

        Args:
            entry_price: Precio de entrada
            stop_loss_price: Precio de stop loss
            confidence: Nivel de confianza (0-1)

        Returns:
            dict: Tamaño de posición y detalles
        """
        # Riesgo por trade ajustado por confianza
        risk_per_trade = self.max_risk_per_trade * confidence

        # Capital a arriesgar
        capital_at_risk = self.current_capital * risk_per_trade

        # Diferencia entre entry y stop loss (%)
        risk_per_unit = abs(entry_price - stop_loss_price) / entry_price

        # Cantidad de BTC a comprar
        position_size_usdt = capital_at_risk / risk_per_unit if risk_per_unit > 0 else 0
        position_size_btc = position_size_usdt / entry_price

        # Verificar que no exceda capital disponible
        max_position_size = self.current_capital * 0.95  # 95% del capital máximo
        if position_size_usdt > max_position_size:
            position_size_usdt = max_position_size
            position_size_btc = position_size_usdt / entry_price

        return {
            'position_size_btc': round(position_size_btc, 8),
            'position_size_usdt': round(position_size_usdt, 2),
            'capital_at_risk': round(capital_at_risk, 2),
            'risk_percentage': round(risk_per_trade * 100, 2),
            'risk_per_unit': round(risk_per_unit * 100, 2)
        }

    def calculate_stop_loss(self, entry_price, direction='long', atr=None, volatility=0.03):
        """
        Calcula stop loss basado en volatilidad y ATR

        Args:
            entry_price: Precio de entrada
            direction: 'long' o 'short'
            atr: Average True Range
            volatility: Volatilidad esperada

        Returns:
            float: Precio de stop loss
        """
        if atr:
            # Usar ATR si está disponible
            stop_distance = atr * 2
        else:
            # Usar volatilidad
            stop_distance = entry_price * volatility

        if direction == 'long':
            stop_loss = entry_price - stop_distance
        else:
            stop_loss = entry_price + stop_distance

        return round(stop_loss, 2)

    def calculate_take_profit(self, entry_price, stop_loss_price, direction='long', risk_reward_ratio=2.5):
        """
        Calcula take profit basado en ratio riesgo/recompensa

        Args:
            entry_price: Precio de entrada
            stop_loss_price: Precio de stop loss
            direction: 'long' o 'short'
            risk_reward_ratio: Ratio riesgo/recompensa

        Returns:
            dict: Múltiples niveles de take profit
        """
        risk = abs(entry_price - stop_loss_price)

        if direction == 'long':
            tp1 = entry_price + (risk * 1.5)
            tp2 = entry_price + (risk * risk_reward_ratio)
            tp3 = entry_price + (risk * (risk_reward_ratio * 1.5))
        else:
            tp1 = entry_price - (risk * 1.5)
            tp2 = entry_price - (risk * risk_reward_ratio)
            tp3 = entry_price - (risk * (risk_reward_ratio * 1.5))

        return {
            'tp1': round(tp1, 2),
            'tp2': round(tp2, 2),
            'tp3': round(tp3, 2)
        }

    def check_risk_limits(self):
        """
        Verifica si se han alcanzado límites de riesgo

        Returns:
            dict: Estado de límites de riesgo
        """
        # Calcular pérdida total del día
        daily_loss = sum([pnl for pnl in self.daily_pnl if pnl < 0])
        daily_loss_pct = abs(daily_loss) / self.initial_capital

        # Calcular drawdown
        peak_capital = max([self.initial_capital] + [t['capital_after'] for t in self.trade_history])
        drawdown = (peak_capital - self.current_capital) / peak_capital if peak_capital > 0 else 0

        # Límites
        max_daily_loss = 0.05  # 5% pérdida diaria máxima
        max_drawdown = 0.20  # 20% drawdown máximo

        warnings = []
        can_trade = True

        if daily_loss_pct >= max_daily_loss:
            warnings.append(f"ALERTA: Límite de pérdida diaria alcanzado ({daily_loss_pct*100:.2f}%)")
            can_trade = False

        if drawdown >= max_drawdown:
            warnings.append(f"ALERTA: Drawdown máximo alcanzado ({drawdown*100:.2f}%)")
            can_trade = False

        if self.current_capital < self.initial_capital * 0.5:
            warnings.append("ALERTA CRÍTICA: Capital reducido a menos del 50%")
            can_trade = False

        return {
            'can_trade': can_trade,
            'daily_loss_pct': round(daily_loss_pct * 100, 2),
            'drawdown': round(drawdown * 100, 2),
            'warnings': warnings,
            'current_capital': round(self.current_capital, 2),
            'capital_pct': round((self.current_capital / self.initial_capital) * 100, 2)
        }

    def open_position(self, entry_price, position_size_btc, stop_loss, take_profit, direction='long', confidence=1.0):
        """
        Registra apertura de posición

        Args:
            entry_price: Precio de entrada
            position_size_btc: Tamaño en BTC
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
            direction: 'long' o 'short'
            confidence: Confianza en el trade
        """
        position = {
            'entry_time': datetime.now(),
            'entry_price': entry_price,
            'position_size_btc': position_size_btc,
            'position_size_usdt': entry_price * position_size_btc,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'direction': direction,
            'confidence': confidence,
            'status': 'open'
        }

        self.open_positions.append(position)
        return position

    def close_position(self, position_index, exit_price, reason='manual'):
        """
        Cierra una posición

        Args:
            position_index: Índice de la posición
            exit_price: Precio de salida
            reason: Razón del cierre

        Returns:
            dict: Resultado del trade
        """
        if position_index >= len(self.open_positions):
            return None

        position = self.open_positions[position_index]

        # Calcular P&L
        if position['direction'] == 'long':
            pnl_btc = position['position_size_btc'] * (exit_price - position['entry_price'])
        else:
            pnl_btc = position['position_size_btc'] * (position['entry_price'] - exit_price)

        pnl_pct = (pnl_btc / position['position_size_usdt']) * 100

        # Actualizar capital
        self.current_capital += pnl_btc

        # Registrar en historial
        trade_result = {
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size_btc': position['position_size_btc'],
            'direction': position['direction'],
            'pnl_usdt': round(pnl_btc, 2),
            'pnl_pct': round(pnl_pct, 2),
            'reason': reason,
            'capital_after': round(self.current_capital, 2)
        }

        self.trade_history.append(trade_result)
        self.daily_pnl.append(pnl_btc)

        # Remover de posiciones abiertas
        self.open_positions.pop(position_index)

        return trade_result

    def get_performance_stats(self):
        """
        Obtiene estadísticas de rendimiento

        Returns:
            dict: Estadísticas completas
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_pnl_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0
            }

        total_trades = len(self.trade_history)
        winning_trades = [t for t in self.trade_history if t['pnl_usdt'] > 0]
        losing_trades = [t for t in self.trade_history if t['pnl_usdt'] <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0

        total_pnl = sum([t['pnl_usdt'] for t in self.trade_history])
        total_pnl_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100

        avg_win = np.mean([t['pnl_usdt'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t['pnl_usdt']) for t in losing_trades]) if losing_trades else 0

        total_wins = sum([t['pnl_usdt'] for t in winning_trades])
        total_losses = abs(sum([t['pnl_usdt'] for t in losing_trades]))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

        # Sharpe Ratio simplificado
        if len(self.daily_pnl) > 1:
            returns = np.array(self.daily_pnl) / self.initial_capital
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(365) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_pct': round(total_pnl_pct, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'current_capital': round(self.current_capital, 2),
            'initial_capital': round(self.initial_capital, 2)
        }


if __name__ == "__main__":
    # Test risk manager
    rm = RiskManager(initial_capital=10000)

    # Simular un trade
    entry_price = 45000
    stop_loss = rm.calculate_stop_loss(entry_price, 'long', volatility=0.03)
    take_profit = rm.calculate_take_profit(entry_price, stop_loss, 'long')

    print(f"Entry: ${entry_price}")
    print(f"Stop Loss: ${stop_loss}")
    print(f"Take Profit: {take_profit}")

    position_size = rm.calculate_position_size(entry_price, stop_loss, confidence=0.8)
    print(f"\nPosition Size: {position_size}")

    # Verificar límites
    risk_status = rm.check_risk_limits()
    print(f"\nRisk Status: {risk_status}")
