import requests
import time
from typing import List, Dict, Any, Optional
from config.env import Config
from models.user_activity import UserActivity, UserPosition
from storage.local_storage import LocalStorage

class DataFetcher:
    def __init__(self, storage: LocalStorage):
        self.storage = storage
        self.base_url = Config.POLYMARKET_API_URL
        
    def fetch_user_activities(self, wallet_address: str) -> List[UserActivity]:
        """Fetch recent trading activities for a user"""
        try:
            url = f"{self.base_url}/activity"
            params = {
                'user': wallet_address,
                'limit': 50,  # Get last 50 activities
                'offset': 0
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            activities = []
            for item in response.json():
                # Convert API response to our UserActivity model
                activity = UserActivity(
                    proxy_wallet=item.get('proxyWallet', wallet_address),
                    timestamp=int(item.get('timestamp', time.time())),
                    condition_id=item.get('conditionId', ''),
                    type=item.get('type', 'TRADE'),
                    size=float(item.get('size', 0)),
                    usdc_size=float(item.get('usdcSize', 0)),
                    transaction_hash=item.get('transactionHash', ''),
                    price=float(item.get('price', 0)),
                    asset=item.get('asset', ''),
                    side=item.get('side', 'BUY'),
                    outcome_index=int(item.get('outcomeIndex', 0)),
                    title=item.get('title', ''),
                    slug=item.get('slug', ''),
                    outcome=item.get('outcome', ''),
                    id=item.get('id', f"{wallet_address}_{item.get('timestamp', time.time())}")
                )
                activities.append(activity)
                
            return activities
            
        except Exception as e:
            print(f"❌ Error fetching user activities: {e}")
            return []
    
    def fetch_user_positions(self, wallet_address: str) -> List[UserPosition]:
        """Fetch current positions for a user"""
        try:
            url = f"{self.base_url}/positions"
            params = {'user': wallet_address}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            positions = []
            for item in response.json():
                position = UserPosition.from_api_data(item)
                positions.append(position)
                
            return positions
            
        except Exception as e:
            print(f"❌ Error fetching user positions: {e}")
            return []
    
    def get_balance(self, wallet_address: str) -> float:
        """Get USDC balance for a wallet"""
        try:
            from web3 import Web3
            
            w3 = Web3(Web3.HTTPProvider(Config.RPC_URL))
            
            # USDC contract ABI (just the balanceOf function)
            usdc_abi = [{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }]
            
            usdc_contract = w3.eth.contract(
                address=Config.USDC_CONTRACT_ADDRESS,
                abi=usdc_abi
            )
            
            balance_wei = usdc_contract.functions.balanceOf(wallet_address).call()
            balance_usdc = balance_wei / (10 ** 6)  # USDC has 6 decimals
            
            return balance_usdc
            
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return 0.0