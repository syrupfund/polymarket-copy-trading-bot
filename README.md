# Polymarket Copy Trading Bot - Enhanced Python Version


Adaptation of the Typescript copy trading bot from Trust412 https://github.com/Trust412/polymarket-copy-trading-bot-v1

Sophisticated Python bot that automatically copies trades from any Polymarket trader in real-time. 

## 🚀 Features

### Core Copy Trading
- **Real-time monitoring** of target trader's activities
- **Intelligent position sizing** based on balance ratios
- **Multiple trading strategies**: Buy, Sell, Merge operations
- **Risk management** with configurable limits
- **Automatic retry logic** for failed trades

### Advanced Features
- **Portfolio analysis** and tracking
- **Market liquidity checks** before trading
- **Proportional copying** based on available balance
- **Local data persistence** (no database required)
- **Colored console output** for easy monitoring
- **Graceful error handling** and recovery

## 📦 Installation

1. **Clone and setup environment**:
```bash
git clone https://github.com/syrupfund/polymarket-copy-trading-bot.git
cd polymarket-copy-trading-bot
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your details
```

3. **Update your proxy wallet address**:
Edit `src/helpers/clob_client.py` and replace `YOUR_PROXY_ADDRESS_HERE` with your actual Polymarket proxy address.

## ⚙️ Configuration

### Required Environment Variables
```env
USER_ADDRESS=0x...     # Wallet address of trader to copy
PROXY_WALLET=0x...     # Your Polymarket proxy wallet
PK=0x...               # Your private key
```

### Optional Configuration
```env
FETCH_INTERVAL=5       # Check for new trades every 5 seconds
TOO_OLD_TIMESTAMP=3600 # Ignore trades older than 1 hour
RETRY_LIMIT=3          # Retry failed trades up to 3 times
```

## 🎯 Trading Strategies

### 1. **Proportional Buy Strategy**
- Calculates your balance vs target trader's balance
- Copies trades proportionally to your available funds
- Includes price deviation protection (max 10% difference)

### 2. **Smart Sell Strategy**
- Sells proportional to target trader's position reduction
- Handles complete position closure
- Maintains risk management

### 3. **Merge Strategy**
- Closes positions when target trader merges
- Finds best available market price
- Executes at optimal liquidity points

## 🔧 Usage

### Basic Usage
```bash
python src/main.py
```

### Monitor Specific Trader
```python
from copy_trading_bot import CopyTradingBot

# Initialize and start
bot = CopyTradingBot()
bot.start()
```

## 📊 Console Output

The bot provides rich, colored console output:
- 🔍 **Blue**: New trade detection
- ✅ **Green**: Successful operations
- ❌ **Red**: Errors and failures
- ⚠️ **Yellow**: Warnings and skipped trades
- 📊 **Cyan**: Status updates

## 🛡️ Risk Management

### Built-in Protections
- **Minimum balance checks** before trading
- **Position size limits** (configurable)
- **Daily loss limits** to prevent overexposure
- **Liquidity verification** before execution
- **Price deviation protection**

### Customizable Limits
```python
# In risk_manager.py
risk_manager = RiskManager(
    max_position_size=100.0,  # Max $100 per trade
    max_daily_loss=50.0       # Stop after $50 daily loss
)
```

## 🔍 Monitoring Features

### Real-time Trade Detection
```
🔍 Found 1 new trades to copy
📊 New Trade Detected:
  Market: Will the S&P 500 close higher on Friday?
  BUY 50.00 shares at $0.645
  Total: $32.25
  Outcome: Yes
  Time: 2024-01-15 14:30:22
```

### Portfolio Analysis
```
📊 Portfolio Summary for 0x1234...5678
  💰 Total Value: $1,234.56
  📈 Total P&L: +$123.45
  🎯 Positions: 5 total
  ✅ Profitable: 3 (60.0%)
  ❌ Losing: 2
```

## ⚠️ Important Notes

### Before Running
1. **Do at least one manual trade** on Polymarket to set allowances
2. **Test with small amounts** first ($1-5)
3. **Verify your proxy wallet address** is correct
4. **Ensure sufficient USDC balance** for copying trades

### Security
- **Keep your private key secure** - never share your `.env` file
- **The private key is only for signing** - funds stay in your Polymarket account
- **Bot respects your balance limits** - won't trade more than you have

## 🐛 Troubleshooting

### Common Issues

**"Error: TARGET_WALLET not configured"**
- Set `USER_ADDRESS` in your `.env` file

**"Insufficient balance to copy trade"**
- Add more USDC to your Polymarket account
- Lower the `max_position_size` in risk manager

**"No position to sell"**
- Normal behavior when you don't hold the position being sold

**"Price moved too much"**
- Market price changed significantly - trade skipped for safety

## 🚀 Advanced Usage

### Custom Risk Parameters
```python
# Modify risk_manager.py
risk_manager = RiskManager(
    max_position_size=50.0,   # Lower max trade size
    max_daily_loss=25.0       # More conservative daily limit
)
```

### Multiple Target Traders
```python
# Run multiple instances with different .env files
# Copy .env to .env.trader1, .env.trader2, etc.
```

## 📚 API Reference

The bot uses:
- **Polymarket CLOB API** for order execution
- **Polymarket Data API** for positions and activities
- **Web3** for balance checking
- **Local file storage** for persistence

## 💡 Tips for Success

1. **Start small** - Test with $5-10 trades first
2. **Monitor actively** - Watch the console output initially
3. **Choose good traders** - Look for consistent, profitable traders
4. **Diversify** - Don't put all funds into copy trading
5. **Understand markets** - Know what you're trading

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Happy Copy Trading! 🚀**
