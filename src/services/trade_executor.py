import time
import threading
from typing import List, Optional, Tuple
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from config.env import Config
from services.data_fetcher import DataFetcher
from storage.local_storage import LocalStorage
from models.user_activity import UserActivity, UserPosition
from colorama import Fore, Style

class TradeExecutor:
    def __init__(self, clob_client: ClobClient, storage: LocalStorage, data_fetcher: DataFetcher):
        self.clob_client = clob_client
        self.storage = storage
        self.data_fetcher = data_fetcher
        self.target_wallet = Config.USER_ADDRESS
        self.my_wallet = Config.PROXY_WALLET
        self.running = False
        
    def start_executing(self):
        """Start trade execution in a separate thread"""
        self.running = True
        executor_thread = threading.Thread(target=self._execution_loop, daemon=True)
        executor_thread.start()
        print(f"{Fore.GREEN}✅ Trade executor started{Style.RESET_ALL}")
        
    def stop_executing(self):
        """Stop trade execution"""
        self.running = False
        print(f"{Fore.YELLOW}⏹ Trade executor stopped{Style.RESET_ALL}")
    
    def _execution_loop(self):
        """Main execution loop"""
        while self.running:
            try:
                pending_trades = self.storage.get_pending_trades(self.target_wallet)
                
                if pending_trades:
                    print(f"{Fore.CYAN}⚡ Processing {len(pending_trades)} pending trades{Style.RESET_ALL}")
                    
                    for trade in pending_trades:
                        try:
                            success = self._execute_trade(trade)
                            self.storage.mark_trade_executed(
                                self.target_wallet, 
                                trade.id, 
                                success
                            )
                        except Exception as e:
                            print(f"{Fore.RED}❌ Error executing trade {trade.id}: {e}{Style.RESET_ALL}")
                            self.storage.mark_trade_executed(
                                self.target_wallet, 
                                trade.id, 
                                False
                            )
                
                time.sleep(2)  # Check every 2 seconds for pending trades
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error in execution loop: {e}{Style.RESET_ALL}")
                time.sleep(5)
    
    def _execute_trade(self, trade: UserActivity) -> bool:
        """Execute a single trade with sophisticated copy logic"""
        try:
            print(f"{Fore.BLUE}🔄 Executing copy trade for {trade.title}...{Style.RESET_ALL}")
            
            # Get current positions
            my_positions = self.data_fetcher.fetch_user_positions(self.my_wallet)
            target_positions = self.data_fetcher.fetch_user_positions(self.target_wallet)
            
            # Get current balances
            my_balance = self.data_fetcher.get_balance(self.my_wallet)
            target_balance = self.data_fetcher.get_balance(self.target_wallet)
            
            print(f"💰 My balance: ${my_balance:.2f} | Target balance: ${target_balance:.2f}")
            
            # Find relevant positions
            my_position = next(
                (pos for pos in my_positions if pos.condition_id == trade.condition_id), 
                None
            )
            target_position = next(
                (pos for pos in target_positions if pos.condition_id == trade.condition_id), 
                None
            )
            
            # Determine trading strategy
            strategy = self._determine_strategy(trade, my_position, target_position)
            
            # Execute based on strategy
            if strategy == 'buy':
                return self._execute_buy_strategy(trade, my_balance, target_balance)
            elif strategy == 'sell':
                return self._execute_sell_strategy(trade, my_position, target_position)
            elif strategy == 'merge':
                return self._execute_merge_strategy(trade, my_position)
            else:
                print(f"{Fore.YELLOW}⚠️ No strategy determined for trade{Style.RESET_ALL}")
                return True  # Mark as handled
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error in _execute_trade: {e}{Style.RESET_ALL}")
            return False
    
    def _determine_strategy(self, trade: UserActivity, my_position: Optional[UserPosition], 
                          target_position: Optional[UserPosition]) -> str:
        """Determine the appropriate trading strategy"""
        
        if trade.type == 'MERGE':
            return 'merge'
        
        if trade.side == 'BUY':
            return 'buy'
        elif trade.side == 'SELL':
            return 'sell'
        
        return 'skip'
    
    def _execute_buy_strategy(self, trade: UserActivity, my_balance: float, 
                            target_balance: float) -> bool:
        """Execute buy strategy with proportional sizing"""
        try:
            if my_balance < 1.0:  # Minimum balance check
                print(f"{Fore.YELLOW}⚠️ Insufficient balance to copy buy trade{Style.RESET_ALL}")
                return True
            
            # Calculate proportional size based on balance ratio
            balance_ratio = min(my_balance / (target_balance + trade.usdc_size), 1.0)
            copy_amount = trade.usdc_size * balance_ratio
            
            # Minimum copy amount
            if copy_amount < 0.1:
                print(f"{Fore.YELLOW}⚠️ Copy amount too small: ${copy_amount:.2f}{Style.RESET_ALL}")
                return True
            
            print(f"📈 Buying ${copy_amount:.2f} worth of {trade.outcome}")
            
            # Get current market price
            try:
                current_price_data = self.clob_client.get_last_trade_price(trade.asset)
                current_price = float(current_price_data.get('price', trade.price))
            except:
                current_price = trade.price
            
            # Check if price is reasonable (within 10% of original trade)
            if abs(current_price - trade.price) / trade.price > 0.1:
                print(f"{Fore.YELLOW}⚠️ Price moved too much. Original: ${trade.price:.3f}, Current: ${current_price:.3f}{Style.RESET_ALL}")
                return True
            
            # Create market buy order
            market_order_args = MarketOrderArgs(
                token_id=trade.asset,
                amount=copy_amount,
            )
            
            signed_order = self.clob_client.create_market_order(market_order_args)
            response = self.clob_client.post_order(signed_order, OrderType.FOK)
            
            if response.get('success', False):
                print(f"{Fore.GREEN}✅ Successfully bought ${copy_amount:.2f} worth{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Buy order failed: {response}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error in buy strategy: {e}{Style.RESET_ALL}")
            return False
    
    def _execute_sell_strategy(self, trade: UserActivity, my_position: Optional[UserPosition], 
                             target_position: Optional[UserPosition]) -> bool:
        """Execute sell strategy with proportional sizing"""
        try:
            if not my_position or my_position.size <= 0:
                print(f"{Fore.YELLOW}⚠️ No position to sell{Style.RESET_ALL}")
                return True
            
            # Calculate how much to sell
            if not target_position:
                # Target closed entire position, sell everything
                sell_amount = my_position.size
            else:
                # Calculate proportional sell
                sell_ratio = trade.size / (target_position.size + trade.size)
                sell_amount = my_position.size * sell_ratio
            
            # Minimum sell amount
            if sell_amount < 0.01:
                print(f"{Fore.YELLOW}⚠️ Sell amount too small: {sell_amount:.3f}{Style.RESET_ALL}")
                return True
            
            print(f"📉 Selling {sell_amount:.2f} shares of {trade.outcome}")
            
            # Get current market price
            try:
                current_price_data = self.clob_client.get_last_trade_price(trade.asset)
                current_price = float(current_price_data.get('price', trade.price))
            except:
                current_price = trade.price
            
            # Create market sell order
            market_order_args = MarketOrderArgs(
                token_id=trade.asset,
                amount=sell_amount,          
            )
            
            signed_order = self.clob_client.create_market_order(market_order_args)
            response = self.clob_client.post_order(signed_order, OrderType.FOK)
            
            if response.get('success', False):
                print(f"{Fore.GREEN}✅ Successfully sold {sell_amount:.2f} shares{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Sell order failed: {response}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error in sell strategy: {e}{Style.RESET_ALL}")
            return False
    
    def _execute_merge_strategy(self, trade: UserActivity, my_position: Optional[UserPosition]) -> bool:
        """Execute merge strategy (close position at best available price)"""
        try:
            if not my_position or my_position.size <= 0:
                print(f"{Fore.YELLOW}⚠️ No position to merge{Style.RESET_ALL}")
                return True
            
            print(f"🔄 Merging position: {my_position.size:.2f} shares")
            
            # Get orderbook to find best price
            orderbook = self.clob_client.get_order_book(trade.asset)
            
            if not orderbook.bids or len(orderbook.bids) == 0:
                print(f"{Fore.RED}❌ No bids available for merge{Style.RESET_ALL}")
                return False
            
            # Find best bid price
            best_bid = max(orderbook.bids, key=lambda x: float(x.price))
            best_price = float(best_bid.price)
            
            print(f"💰 Best bid price: ${best_price:.3f}")
            
            # Create limit sell order at best bid price
            order_args = OrderArgs(
                token_id=trade.asset,
                price=best_price,
                size=my_position.size,
                side=SELL
            )
            
            signed_order = self.clob_client.create_order(order_args)
            response = self.clob_client.post_order(signed_order, OrderType.FOK)
            
            if response.get('success', False):
                print(f"{Fore.GREEN}✅ Successfully merged position{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Merge failed: {response}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error in merge strategy: {e}{Style.RESET_ALL}")
            return False
