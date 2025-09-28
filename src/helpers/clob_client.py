import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

def create_clob_client() -> ClobClient:
    load_dotenv()
    
    host = "https://clob.polymarket.com"
    key = os.getenv('PK')  # Your exported private key from Polymarket
    
    # REPLACE THIS: Your Polymarket proxy address (shown below profile picture)
    polymarket_proxy_address = "0x1234567890abcdef1234567890abcdef12345678"
    
    client = ClobClient(
        host=host, 
        key=key, 
        chain_id=POLYGON, 
        signature_type=1, 
        funder=polymarket_proxy_address
    )
    
    # Create or derive API credentials automatically
    client.set_api_creds(client.derive_api_key())
    
    return client