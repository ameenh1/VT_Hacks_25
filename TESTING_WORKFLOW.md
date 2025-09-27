# Deal Finder Testing Workflow

## Prerequisites

### 1. Environment Setup
First, make sure you have your environment configured:

```powershell
# 1. Copy the example env file
copy .env.example .env

# 2. Edit .env file and add your API keys:
# GEMINI_API_KEY=your_key_here
# ATTOM_API_KEY=your_key_here (optional for now)
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

## Testing Workflow

### Step 1: Basic Mock Data Test (No API Keys Needed)
```powershell
python test_deal_finder.py
```

This will test:
- ✅ Deal Finder initialization
- ✅ Mock data generation (works without ATTOM API)
- ✅ Basic deal finding logic
- ✅ User criteria management

**Expected Output**: Should find 2-3 mock deals in Virginia Tech area

### Step 2: ATTOM API Test (Requires ATTOM API Key)
If you have an ATTOM API key, the test will also:
- ✅ Connect to real ATTOM API
- ✅ Search for properties in specified locations  
- ✅ Process real property data

**Expected Output**: Real property listings from ATTOM database

### Step 3: Manual Deal Finder Test
Create a simple test script:

```python
import asyncio
from agents.deal_finder import DealFinder, SearchCriteria

async def quick_test():
    # Initialize Deal Finder
    deal_finder = DealFinder()
    
    # Set search criteria
    criteria = SearchCriteria(
        max_price=350000,
        target_locations=["Blacksburg", "VA"],
        property_types=["SFR"]
    )
    
    # Find deals
    deals = await deal_finder.find_deals_now(criteria)
    
    # Print results
    for deal in deals:
        print(f"Found: {deal.property_address}")
        print(f"Price: ${deal.listing_price:,}")
        print(f"Estimated Value: ${deal.estimated_value:,}")
        print(f"Profit Potential: {deal.key_metrics['profit_percentage']:.1f}%")
        print("-" * 50)

# Run it
asyncio.run(quick_test())
```

## What to Look For

### ✅ Success Indicators:
- Deal Finder initializes without errors
- Mock deals are generated (Virginia locations)
- Deals have reasonable profit percentages (>10%)
- Alert priorities are set correctly (HIGH, MEDIUM, etc.)
- Background monitoring can start/stop

### ❌ Failure Indicators:
- Import errors (missing dependencies)
- No deals found even with mock data  
- ATTOM API connection timeouts
- Background tasks not starting properly

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the project root directory
2. **No Mock Deals**: Check that mock data generation is working
3. **ATTOM API Fails**: This is expected without API key - should fallback to mock data
4. **Background Tasks**: May need to run longer to see background monitoring effects

## Next Steps After Testing

1. If mock data works → Deal Finder core logic is good ✅
2. If ATTOM API works → Integration is properly configured ✅  
3. If both work → Ready to connect with Analysis Engine and Customer Agent ✅

The key is that **Deal Finder should work with mock data even without any API keys**. This proves the core functionality is sound.