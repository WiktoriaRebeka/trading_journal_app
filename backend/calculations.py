from decimal import Decimal

def calculate_position_based_on_leverage(deposit, risk, leverage):
    if leverage == 0:
        raise ValueError("Leverage cannot be zero")
    position = (risk / 100) * deposit * leverage  # Zależnie od tego, jak definiujesz wielkość pozycji
    return position

def calculate_leverage_based_on_position(deposit, risk, position):
    if position == 0:
        raise ValueError("Position cannot be zero")
    leverage = (position / ((risk / 100) * deposit))  # Zależnie od tego, jak definiujesz lewar
    return leverage

def calculate_risk_reward_ratio(entry, stop_loss, target_price):
    if entry == stop_loss:
        raise ZeroDivisionError("Entry price and stop loss cannot be the same")
    risk_reward_ratio = (target_price - entry) / (entry - stop_loss)
    return risk_reward_ratio

def calculate_win(risk, risk_reward_ratio, win):
    if win == 'YES':
        return risk * risk_reward_ratio
    else:
        return -risk  # Strata równa ryzyku
