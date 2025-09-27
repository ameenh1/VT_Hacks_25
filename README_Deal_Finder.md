# Deal Finder Agent - Real Estate Investment Opportunity Hunter

## 🏠 What is Deal Finder?

Deal Finder is **Agent 3** in your multi-agent real estate investment platform. It's an intelligent background service that continuously monitors real estate markets to identify undervalued investment opportunities automatically.

Think of it as having a 24/7 real estate analyst that never sleeps, constantly scanning properties and alerting you when it finds deals with significant profit potential.

## 🎯 How It Works

### The Magic Behind Deal Finding

```
1. 🔍 PROPERTY DISCOVERY
   ↓
2. 💰 VALUE ANALYSIS (ATTOM Data)
   ↓
3. 🏷️ CURRENT PRICING (Zillow API)
   ↓
4. 📊 PROFIT CALCULATION
   ↓
5. 🚨 SMART ALERTS
```

**Example Deal Detection:**
- ATTOM estimated value: **$400,000**
- Current Zillow listing: **$320,000**
- **= 25% profit potential!** 🎉

### Dual Analysis System

**🚀 Enhanced Mode (Recommended):**
- Uses ATTOM property data + current Zillow listings
- Calculates real profit potential
- Analyzes seller motivation (days on market)
- Provides rental income estimates

**⚠️ Fallback Mode:**
- Uses only ATTOM data when listing API unavailable
- Less accurate but still functional

## 🛠️ Quick Setup

### Prerequisites
```bash
# Required API Keys
ATTOM_API_KEY=your_attom_key_here        # Property data
RAPIDAPI_KEY=your_rapidapi_key_here      # Current listings (optional but recommended)
```

### Installation
```python
from agents.deal_finder import DealFinder, SearchCriteria
from integrations.attom_api import ATTOMDataBridge

# Initialize with API keys
attom_bridge = ATTOMDataBridge(api_key="your_attom_key")
deal_finder = DealFinder(
    attom_bridge=attom_bridge,
    rapidapi_key="your_rapidapi_key"  # Optional but recommended
)
```

## 🚀 Usage Examples

### 1. Find Deals Immediately
```python
import asyncio

# Define your investment criteria
criteria = SearchCriteria(
    max_price=500000,                    # Maximum property price
    target_locations=["24060", "24073"], # ZIP codes to search
    property_types=["SFR"],              # Single Family Residences
    min_deal_score=60.0                  # Minimum deal quality score
)

# Find deals now
deals = await deal_finder.find_deals_now(criteria, max_results=10)

for deal in deals:
    print(f"🎯 {deal.title}")
    print(f"   Address: {deal.property_address}")
    print(f"   Profit: {deal.key_metrics['profit_percentage']:.1f}%")
    print(f"   Confidence: {deal.confidence_score:.0%}")
```

### 2. Start Background Monitoring
```python
# Add user criteria for continuous monitoring
deal_finder.add_user_criteria("user_123", criteria)

# Start background monitoring (scans every 15 minutes)
await deal_finder.start_monitoring()

# Your deals will be automatically discovered and saved
# Check for new alerts later
user_alerts = await deal_finder.get_alerts_for_user("user_123")
```

### 3. Monitor Specific Properties
```python
# Watch specific addresses
await deal_finder.monitor_specific_property("123 Main St, Blacksburg, VA 24060")

# Check monitoring status
status = deal_finder.get_monitoring_status()
print(f"Monitoring {status['monitored_properties']} properties")
```

## 📊 Understanding Deal Alerts

### Alert Types
- **UNDERVALUED_PROPERTY**: Significantly below market value (>25% profit)
- **HIGH_CASH_FLOW**: Good rental income potential (>15% profit)
- **PRICE_DROP**: Recently reduced price
- **NEW_LISTING**: Just came on market
- **DISTRESSED_SALE**: Motivated seller situation

### Priority Levels
- **🔥 URGENT**: >20% profit + motivated seller
- **🟡 HIGH**: >15% profit potential
- **🔵 MEDIUM**: >10% profit potential
- **⚪ LOW**: <10% profit potential

### Sample Alert
```python
PropertyAlert(
    property_address="456 Investment Ave, Blacksburg, VA 24060",
    alert_type=AlertType.UNDERVALUED_PROPERTY,
    priority=AlertPriority.HIGH,
    title="🎯 REAL DEAL: 22.5% Profit Potential",
    key_metrics={
        "attom_estimated_value": 380000,
        "current_listing_price": 310000,
        "profit_percentage": 22.5,
        "days_on_market": 45,
        "seller_motivation": "motivated",
        "rental_estimate": 2400
    },
    confidence_score=0.85
)
```

## 🔧 Configuration Options

### Search Criteria
```python
criteria = SearchCriteria(
    max_price=600000,                    # Maximum property price
    min_deal_score=70.0,                 # Minimum profit threshold
    target_locations=["24060", "24073"], # ZIP codes or cities
    property_types=["SFR", "CON"],       # Property types
    min_cash_flow=200,                   # Minimum monthly cash flow
    preferred_strategies=[InvestmentStrategy.BUY_AND_HOLD]
)
```

### Deal Finder Settings
```python
deal_finder.scan_interval_minutes = 30    # How often to scan (default: 15)
deal_finder.alert_retention_days = 14     # How long to keep alerts (default: 7)
deal_finder.max_alerts_per_user = 100     # Max alerts per user (default: 50)
```

## 📈 Monitoring and Health Checks

### Check System Status
```python
# Get comprehensive status
status = deal_finder.get_monitoring_status()
print(f"Running: {status['is_running']}")
print(f"Active alerts: {status['active_alerts']}")
print(f"API requests made: {status['listing_api_usage']['requests_made']}")

# Health check
health = await deal_finder.health_check()
print(f"System status: {health['status']}")
```

### View Logs
The system provides detailed logging:
```
INFO:agents.deal_finder:Starting immediate deal search
INFO:integrations.attom_api:Found 50 properties matching search criteria
INFO:agents.deal_finder:🎯 FOUND REAL DEAL: 123 Main St - 18.5% profit
```

## 🎭 Testing and Development

### Run Tests
```bash
# Basic functionality test
python test_deal_finder_comparison.py

# Comprehensive feature test
python test_deal_finder_comprehensive.py
```

### Mock Data Mode
```python
# For testing without API keys
mock_deal_finder = DealFinder()  # No API bridges
mock_deals = await mock_deal_finder.find_deals_now(criteria)
# Returns realistic sample deals for development
```

## 🔑 API Keys Setup

### ATTOM Data API (Required)
1. Visit [ATTOM Data](https://developer.attomdata.com/)
2. Sign up and get API key
3. Add to `.env`: `ATTOM_API_KEY=your_key_here`

### RapidAPI Zillow (Optional but Recommended)
1. Visit [RapidAPI Zillow](https://rapidapi.com/apimaker/api/zillow-com1/)
2. Subscribe to free tier (100 requests/month)
3. Add to `.env`: `RAPIDAPI_KEY=your_key_here`

## 🚨 Common Issues and Solutions

### No Deals Found
```python
# Possible causes:
# 1. Criteria too strict - try lowering min_deal_score
criteria.min_deal_score = 50.0

# 2. Price limits too low - increase max_price
criteria.max_price = 800000

# 3. Limited area - expand target_locations
criteria.target_locations = ["24060", "24073", "24141"]
```

### API Rate Limits
```python
# Check API usage
status = deal_finder.get_monitoring_status()
usage = status['listing_api_usage']
print(f"Requests remaining: {usage['requests_remaining']}")

# Reduce scan frequency if hitting limits
deal_finder.scan_interval_minutes = 60  # Scan every hour
```

### Background Tasks Not Running
```python
# Check if monitoring is active
if not deal_finder.is_running:
    await deal_finder.start_monitoring()

# Verify health
health = await deal_finder.health_check()
print(health['background_tasks'])
```

## 🎯 Integration with Other Agents

### Customer Agent Integration
```python
# Deal Finder → Customer Agent flow
deals = await deal_finder.find_deals_now(user_criteria)
for deal in deals:
    # Send to Customer Agent for user presentation
    await customer_agent.present_deal_to_user(user_id, deal)
```

### Analysis Engine Integration
```python
# Deal Finder → Analysis Engine flow
if deal_finder.analysis_engine:
    detailed_analysis = await deal_finder.analysis_engine.deep_analyze(property_data)
    # Enhanced deal scoring with AI analysis
```

## 🏆 Best Practices

### 1. Start Conservative
```python
# Begin with higher profit thresholds
criteria.min_deal_score = 80.0
# Gradually lower as you understand the market
```

### 2. Monitor Multiple Areas
```python
# Diversify your search locations
criteria.target_locations = ["24060", "24073", "24141", "24112"]
```

### 3. Set Realistic Expectations
- 10-15% deals: Common in good markets
- 20%+ deals: Rare but possible
- 30%+ deals: Very rare, investigate thoroughly

### 4. Regular Health Checks
```python
# Monitor system daily
health = await deal_finder.health_check()
if health['status'] != 'healthy':
    print("⚠️  System needs attention")
```

## 📚 Advanced Features

### Custom Alert Filtering
```python
def custom_deal_filter(alert: PropertyAlert) -> bool:
    metrics = alert.key_metrics
    
    # Only deals with rental estimates
    if not metrics.get('rental_estimate'):
        return False
    
    # Must be 3+ bedrooms
    if metrics.get('bedrooms', 0) < 3:
        return False
    
    return True

# Apply custom filtering
filtered_deals = [deal for deal in deals if custom_deal_filter(deal)]
```

### Deal Scoring Customization
```python
def calculate_custom_score(property_data, listing_data):
    score = 0
    
    # Base profit score
    if listing_data.profit_percentage > 20:
        score += 40
    elif listing_data.profit_percentage > 10:
        score += 20
    
    # Location bonus
    if "downtown" in property_data.address.lower():
        score += 15
    
    # Days on market penalty
    if listing_data.days_on_market > 90:
        score += 10  # Motivated seller bonus
    
    return min(100, score)
```

## 🤝 Contributing

### Adding New Features
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-alert-type`
3. Add tests for your feature
4. Submit pull request

### Reporting Issues
Include:
- Error messages
- API response samples
- Configuration used
- Expected vs actual behavior

---

## 🎉 You're Ready to Find Deals!

Your Deal Finder is now configured and ready to hunt for investment opportunities. Start with the basic examples above and gradually explore the advanced features as you become more comfortable with the system.

**Happy Deal Hunting! 🏡💰**