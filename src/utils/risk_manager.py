from typing import Dict, Any, Optional
from config.env import Config
from models.user_activity import UserActivity, UserPosition

class RiskManager:
    def __init__(self, max_position_size: float = 100.0, max_daily_loss: float = 50.0):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_loss = 0.0
        
    def check_trade_risk(self, trade: UserActivity, my_balance: float, 
                        my_position: Optional[UserPosition] = None) -> Dict[str, Any]:
        """Check if a trade meets risk management criteria"""
        
        risk_checks = {
            'approved': True,
            'reasons': [],
            'suggested_size': trade.usdc_size
        }
        
        # Check minimum balance
        if my_balance < 5.0:
            risk_checks['approved'] = False
            risk_checks['reasons'].append("Insufficient balance (< $5)")
        
        # Check maximum position size
        if trade.usdc_size > self.max_position_size:
            risk_checks['approved'] = False
            risk_checks['reasons'].append(f"Trade size too large (> ${self.max_position_size})")
            # Suggest smaller size
            risk_checks['suggested_size'] = min(self.max_position_size, my_balance * 0.1)
        
        # Check daily loss limit
        if self.daily_loss > self.max_daily_loss:
            risk_checks['approved'] = False
            risk_checks['reasons'].append(f"Daily loss limit exceeded (> ${self.max_daily_loss})")
        
        # Check position concentration (don't put more than 20% in one market)
        max_single_position = my_balance * 0.2
        if trade.usdc_size > max_single_position:
            risk_checks['suggested_size'] = max_single_position
        
        return risk_checks
    
    def update_daily_pnl(self, pnl_change: float):
        """Update daily P&L tracking"""
        if pnl_change < 0:
            self.daily_loss += abs(pnl_change)