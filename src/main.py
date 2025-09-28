import os
import sys
from colorama import Fore, Style, init
from copy_trading_bot import CopyTradingBot
from config.env import Config

# Initialize colorama
init()

def main():
    """Main entry point for the copy trading bot"""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    POLYMARKET COPY TRADING BOT                    ║
║                          Enhanced Python Version                  ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Validate environment
    try:
        # Test configuration
        print(f"{Fore.BLUE}🔍 Validating configuration...{Style.RESET_ALL}")
        
        if not Config.USER_ADDRESS:
            raise ValueError("❌ USER_ADDRESS not configured")
        if not Config.PROXY_WALLET:
            raise ValueError("❌ PROXY_WALLET not configured")
        if not Config.PRIVATE_KEY:
            raise ValueError("❌ PRIVATE_KEY not configured")
            
        print(f"{Fore.GREEN}✅ Configuration validated{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Please check your .env file configuration{Style.RESET_ALL}")
        return
    
    # Start the bot
    try:
        bot = CopyTradingBot()
        bot.start()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start bot: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

# src/utils/portfolio_analyzer.py
from typing import List, Dict, Any
from models.user_activity import UserPosition
from colorama import Fore, Style

class PortfolioAnalyzer:
    @staticmethod
    def analyze_positions(positions: List[UserPosition]) -> Dict[str, Any]:
        """Analyze a portfolio of positions"""
        if not positions:
            return {
                'total_value': 0,
                'total_pnl': 0,
                'num_positions': 0,
                'profitable_positions': 0,
                'losing_positions': 0
            }
        
        total_value = sum(pos.current_value for pos in positions)
        total_pnl = sum(pos.cash_pnl for pos in positions)
        profitable = sum(1 for pos in positions if pos.cash_pnl > 0)
        losing = sum(1 for pos in positions if pos.cash_pnl < 0)
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'num_positions': len(positions),
            'profitable_positions': profitable,
            'losing_positions': losing,
            'win_rate': profitable / len(positions) if positions else 0
        }
    
    @staticmethod
    def print_portfolio_summary(wallet_address: str, positions: List[UserPosition]):
        """Print a formatted portfolio summary"""
        analysis = PortfolioAnalyzer.analyze_positions(positions)
        
        pnl_color = Fore.GREEN if analysis['total_pnl'] >= 0 else Fore.RED
        pnl_symbol = "+" if analysis['total_pnl'] >= 0 else ""
        
        print(f"""
{Fore.BLUE}📊 Portfolio Summary for {wallet_address[:8]}...{wallet_address[-8:]}{Style.RESET_ALL}
  💰 Total Value: ${analysis['total_value']:.2f}
  {pnl_color}📈 Total P&L: {pnl_symbol}${analysis['total_pnl']:.2f}{Style.RESET_ALL}
  🎯 Positions: {analysis['num_positions']} total
  ✅ Profitable: {analysis['profitable_positions']} ({analysis['win_rate']:.1%})
  ❌ Losing: {analysis['losing_positions']}
        """)

# src/utils/risk_manager.py
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