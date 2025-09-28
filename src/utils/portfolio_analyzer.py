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
