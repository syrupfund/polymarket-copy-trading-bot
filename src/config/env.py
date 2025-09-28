import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Target user to copy
    USER_ADDRESS = os.getenv('USER_ADDRESS')
    if not USER_ADDRESS:
        raise ValueError("USER_ADDRESS is required")
    
    # Your wallet details
    PROXY_WALLET = os.getenv('PROXY_WALLET')
    if not PROXY_WALLET:
        raise ValueError("PROXY_WALLET is required")
        
    PRIVATE_KEY = os.getenv('PK')
    if not PRIVATE_KEY:
        raise ValueError('PK is required')
    
    # API URLs
    HOST = os.getenv('HOST', 'https://clob.polymarket.com')
    POLYMARKET_API_URL = 'https://data-api.polymarket.com'
    
    # Trading parameters
    FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', '5'))  # seconds
    TOO_OLD_TIMESTAMP = int(os.getenv('TOO_OLD_TIMESTAMP', '3600'))  # 1 hour
    RETRY_LIMIT = int(os.getenv('RETRY_LIMIT', '3'))
    
    # MongoDB (optional - fallback to local file storage)
    MONGO_URI = os.getenv('MONGO_URI')
    
    # Web3 config
    RPC_URL = os.getenv('RPC_URL', 'https://polygon-rpc.com')
    USDC_CONTRACT_ADDRESS = os.getenv('USDC_CONTRACT_ADDRESS', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
