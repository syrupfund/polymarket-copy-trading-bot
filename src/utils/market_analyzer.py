import requests
from typing import Dict, Any, Optional
from config.env import Config

class MarketAnalyzer:
    @staticmethod
    def get_market_info(condition_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed market information"""
        try:
            url = f"{Config.POLYMARKET_API_URL}/markets/{condition_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching market info: {e}")
            return None
    
    @staticmethod
    def check_market_liquidity(token_id: str, clob_client) -> Dict[str, Any]:
        """Check market liquidity before trading"""
        try:
            orderbook = clob_client.get_order_book(token_id)
            
            # Calculate total liquidity
            bid_liquidity = sum(float(bid['size']) * float(bid['price']) 
                              for bid in orderbook.bids) if orderbook.bids else 0
            ask_liquidity = sum(float(ask['size']) * float(ask['price']) 
                              for ask in orderbook.asks) if orderbook.asks else 0
            
            # Get spread
            if orderbook.bids and orderbook.asks:
                best_bid = max(float(bid['price']) for bid in orderbook.bids)
                best_ask = min(float(ask['price']) for ask in orderbook.asks)
                spread = best_ask - best_bid
                spread_pct = spread / best_ask if best_ask > 0 else 1.0
            else:
                spread = 1.0
                spread_pct = 1.0
            
            return {
                'bid_liquidity': bid_liquidity,
                'ask_liquidity': ask_liquidity,
                'total_liquidity': bid_liquidity + ask_liquidity,
                'spread': spread,
                'spread_percentage': spread_pct,
                'liquid': bid_liquidity > 10 and ask_liquidity > 10 and spread_pct < 0.05
            }
            
        except Exception as e:
            print(f"❌ Error checking liquidity: {e}")
            return {
                'bid_liquidity': 0,
                'ask_liquidity': 0,
                'total_liquidity': 0,
                'spread': 1.0,
                'spread_percentage': 1.0,
                'liquid': False
            }