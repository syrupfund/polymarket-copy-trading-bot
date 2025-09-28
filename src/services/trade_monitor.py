import time
import threading
from typing import List
from config.env import Config
from services.data_fetcher import DataFetcher
from storage.local_storage import LocalStorage
from models.user_activity import UserActivity
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init()

class TradeMonitor:
    def __init__(self, storage: LocalStorage, data_fetcher: DataFetcher):
        self.storage = storage
        self.data_fetcher = data_fetcher
        self.target_wallet = Config.USER_ADDRESS
        self.running = False
        self.known_activities = set()
        
        # Load existing activities to avoid duplicates
        existing_activities = self.storage.load_activities(self.target_wallet)
        self.known_activities = {activity.id for activity in existing_activities}
    
    def start_monitoring(self):
        """Start monitoring in a separate thread"""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        print(f"{Fore.GREEN}✅ Trade monitoring started for {self.target_wallet}{Style.RESET_ALL}")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        print(f"{Fore.YELLOW}⏹ Trade monitoring stopped{Style.RESET_ALL}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_for_new_trades()
                time.sleep(Config.FETCH_INTERVAL)
            except Exception as e:
                print(f"{Fore.RED}❌ Error in monitoring loop: {e}{Style.RESET_ALL}")
                time.sleep(Config.FETCH_INTERVAL * 2)  # Wait longer on error
    
    def _check_for_new_trades(self):
        """Check for new trading activities"""
        try:
            # Fetch latest activities
            activities = self.data_fetcher.fetch_user_activities(self.target_wallet)
            
            # Filter for new trades only
            new_activities = [
                activity for activity in activities
                if (activity.id not in self.known_activities and
                    activity.type == 'TRADE' and
                    time.time() - activity.timestamp < Config.TOO_OLD_TIMESTAMP)
            ]
            
            if new_activities:
                print(f"{Fore.CYAN}🔍 Found {len(new_activities)} new trades to copy{Style.RESET_ALL}")
                
                # Load existing activities and add new ones
                all_activities = self.storage.load_activities(self.target_wallet)
                all_activities.extend(new_activities)
                
                # Save updated activities
                self.storage.save_activities(self.target_wallet, all_activities)
                
                # Update known activities
                for activity in new_activities:
                    self.known_activities.add(activity.id)
                    
                # Print trade details
                for activity in new_activities:
                    self._print_trade_info(activity)
                    
        except Exception as e:
            print(f"{Fore.RED}❌ Error checking for trades: {e}{Style.RESET_ALL}")
    
    def _print_trade_info(self, activity: UserActivity):
        """Print formatted trade information"""
        side_color = Fore.GREEN if activity.side == 'BUY' else Fore.RED
        print(f"""
{Fore.BLUE}📊 New Trade Detected:{Style.RESET_ALL}
  Market: {activity.title}
  {side_color}{activity.side}{Style.RESET_ALL} {activity.size:.2f} shares at ${activity.price:.3f}
  Total: ${activity.usdc_size:.2f}
  Outcome: {activity.outcome}
  Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(activity.timestamp))}
        """)