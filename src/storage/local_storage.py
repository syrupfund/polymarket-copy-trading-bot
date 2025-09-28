import json
import os
from typing import List, Dict, Any, Optional
from models.user_activity import UserActivity, UserPosition

class LocalStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def _get_activities_file(self, wallet_address: str) -> str:
        return os.path.join(self.data_dir, f"activities_{wallet_address}.json")
    
    def _get_positions_file(self, wallet_address: str) -> str:
        return os.path.join(self.data_dir, f"positions_{wallet_address}.json")
    
    def save_activities(self, wallet_address: str, activities: List[UserActivity]):
        file_path = self._get_activities_file(wallet_address)
        data = [activity.to_dict() for activity in activities]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_activities(self, wallet_address: str) -> List[UserActivity]:
        file_path = self._get_activities_file(wallet_address)
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return [UserActivity.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def save_positions(self, wallet_address: str, positions: List[UserPosition]):
        file_path = self._get_positions_file(wallet_address)
        data = [pos.__dict__ for pos in positions]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_positions(self, wallet_address: str) -> List[UserPosition]:
        file_path = self._get_positions_file(wallet_address)
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return [UserPosition(**item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def get_pending_trades(self, wallet_address: str) -> List[UserActivity]:
        activities = self.load_activities(wallet_address)
        return [
            activity for activity in activities
            if (activity.type == 'TRADE' and 
                not activity.bot_executed and 
                activity.bot_executed_time < 3)  # Max 3 retries
        ]
    
    def mark_trade_executed(self, wallet_address: str, activity_id: str, success: bool = True):
        activities = self.load_activities(wallet_address)
        for activity in activities:
            if activity.id == activity_id:
                activity.bot_executed = success
                if not success:
                    activity.bot_executed_time += 1
                break
        self.save_activities(wallet_address, activities)