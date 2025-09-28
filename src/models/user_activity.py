from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

@dataclass
class UserActivity:
    proxy_wallet: str
    timestamp: int
    condition_id: str
    type: str  # 'TRADE', 'MERGE', etc.
    size: float
    usdc_size: float
    transaction_hash: str
    price: float
    asset: str
    side: str  # 'BUY', 'SELL'
    outcome_index: int
    title: str
    slug: str
    outcome: str
    bot_executed: bool = False
    bot_executed_time: int = 0
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserActivity':
        return cls(**data)

@dataclass
class UserPosition:
    proxy_wallet: str
    asset: str
    condition_id: str
    size: float
    avg_price: float
    initial_value: float
    current_value: float
    cash_pnl: float
    percent_pnl: float
    total_bought: float
    realized_pnl: float
    cur_price: float
    redeemable: bool
    title: str
    outcome: str
    outcome_index: int
    end_date: str
    negative_risk: bool

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> 'UserPosition':
        return cls(
            proxy_wallet=data.get('proxyWallet', ''),
            asset=data.get('asset', ''),
            condition_id=data.get('conditionId', ''),
            size=float(data.get('size', 0)),
            avg_price=float(data.get('avgPrice', 0)),
            initial_value=float(data.get('initialValue', 0)),
            current_value=float(data.get('currentValue', 0)),
            cash_pnl=float(data.get('cashPnl', 0)),
            percent_pnl=float(data.get('percentPnl', 0)),
            total_bought=float(data.get('totalBought', 0)),
            realized_pnl=float(data.get('realizedPnl', 0)),
            cur_price=float(data.get('curPrice', 0)),
            redeemable=data.get('redeemable', False),
            title=data.get('title', ''),
            outcome=data.get('outcome', ''),
            outcome_index=int(data.get('outcomeIndex', 0)),
            end_date=data.get('endDate', ''),
            negative_risk=data.get('negativeRisk', False)
        )
