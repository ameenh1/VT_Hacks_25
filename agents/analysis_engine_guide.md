# Analysis Engine User Guide

## Overview

The Professional Real Estate Analysis Engine is a sophisticated valuation system that implements industry-standard appraisal methodology using AI-enhanced analysis. It uses **Gemini 2.5 Pro** for intelligent property evaluation and generates structured, professional-grade reports.

## Quick Start

### Basic Initialization

```python
from agents.analysis_engine import AnalysisEngine, PropertyFeatures
import asyncio

# Initialize with your Gemini API key
api_key = "your_gemini_api_key_here"
engine = AnalysisEngine(api_key=api_key)
```

### Simple Property Analysis

```python
async def analyze_property():
    # Quick analysis method (legacy compatibility)
    result = await engine.quick_analysis(
        address="123 Main Street",
        listing_price=350000
    )
    
    if result["success"]:
        print(f"Deal Score: {result['deal_score']}%")
        print(f"ARV Estimate: ${result['arv_estimate']:,}")
        print(f"Investment Strategy: {result['recommended_strategy']}")
    
# Run the analysis
asyncio.run(analyze_property())
```

## Professional Valuation Analysis

### Input Data Structure

The engine uses the `PropertyFeatures` dataclass for comprehensive property information:

```python
from agents.analysis_engine import PropertyFeatures
from datetime import datetime

property_data = PropertyFeatures(
    address="123 Investment Avenue",
    gla=2200,                    # Gross Living Area (sq ft)
    bedrooms=4,
    bathrooms=2.5,
    garage_spaces=2,
    lot_size=8500,              # Lot size (sq ft)
    age=12,                     # Property age (years)
    condition='good',           # 'excellent', 'good', 'average', 'fair', 'poor'
    property_type='SFR',        # 'SFR' (Single Family), 'CON' (Condo), 'TWH' (Townhome)
    listing_price=425000,       # Current listing price (optional)
    monthly_rent=2800           # Monthly rental income (optional)
)
```

### Comprehensive Analysis

```python
async def full_analysis():
    # Comprehensive professional valuation
    analysis_result = await engine.comprehensive_valuation_analysis(
        property_data=property_data,
        user_criteria={
            "max_price": 450000,
            "min_cash_flow": 200,
            "target_roi": 0.15
        }
    )
    
    # Access detailed results
    print(f"ARV Estimate: ${analysis_result.valuation.arv_estimate:,.0f}")
    print(f"Deal Score: {analysis_result.deal_score:.0f}%")
    print(f"Investment Grade: {analysis_result.investment_grade}")
    print(f"Confidence: {analysis_result.confidence_score:.1%}")
    
    # Valuation breakdown by method
    for method, value in analysis_result.valuation.valuation_methods.items():
        weight = analysis_result.valuation.method_weights[method]
        print(f"{method.value}: ${value:,.0f} (Weight: {weight:.1%})")

asyncio.run(full_analysis())
```

## Data Input Requirements

### Required Fields
- `address`: Property address (string)
- `gla`: Gross living area in square feet (int)
- `bedrooms`: Number of bedrooms (int)
- `bathrooms`: Number of bathrooms (float, e.g., 2.5)
- `garage_spaces`: Number of garage spaces (int)
- `lot_size`: Lot size in square feet (float)
- `age`: Property age in years (int)
- `condition`: Property condition (string)
- `property_type`: Type of property (string)

### Optional Fields
- `listing_price`: Current listing price (float)
- `monthly_rent`: Monthly rental income (float)

### Property Condition Values
- `'excellent'`: Recently renovated, move-in ready
- `'good'`: Well-maintained, minor updates needed
- `'average'`: Normal wear, some updates recommended
- `'fair'`: Deferred maintenance, updates needed
- `'poor'`: Significant repairs required

### Property Type Values
- `'SFR'`: Single Family Residence
- `'CON'`: Condominium
- `'TWH'`: Townhome

## Analysis Output Structure

### Main Analysis Result (`PropertyAnalysisSchema`)

```python
# Key result properties
result.property_address          # Property address
result.valuation.arv_estimate   # After Repair Value estimate
result.deal_score               # Investment deal score (0-100)
result.investment_grade         # Letter grade (A+ to D)
result.confidence_score         # Analysis confidence (0.0-1.0)
result.executive_summary        # Executive summary text
result.recommendation           # Buy/Hold/Pass recommendation
```

### Valuation Details

```python
# Three-approach valuation breakdown
valuation = result.valuation
valuation.valuation_methods     # Dict of method values
valuation.method_weights        # Dict of method weights
valuation.comparable_properties # List of comparable sales
valuation.key_factors          # List of value drivers
valuation.value_range          # Conservative/optimistic range
```

### Investment Analysis

```python
# Investment metrics
result.investment_strategy.recommended_strategy    # Primary strategy
result.investment_strategy.financial_projections  # Cash flow projections
result.investment_strategy.investment_metrics     # ROI, cap rate, etc.
result.investment_strategy.execution_plan         # Step-by-step plan
```

### Risk Assessment

```python
# Risk analysis
risk = result.risk_assessment
risk.overall_risk_score        # Overall risk (1-10)
risk.risk_rating              # Risk level (LOW, MODERATE, HIGH)
risk.risk_factors             # List of specific risks
risk.key_concerns             # Primary concerns
```

### Market Analysis

```python
# Market conditions
market = result.market_analysis
market.market_condition        # Market type (BUYERS/SELLERS/BALANCED)
market.price_trends           # Price trend data
market.inventory_analysis     # Supply/demand metrics
market.investment_climate     # Investment environment
```

## Batch Processing

For analyzing multiple properties:

```python
async def analyze_multiple_properties():
    properties = [property1, property2, property3]  # List of PropertyFeatures
    
    # Batch analysis
    results = await engine.analyze_property_batch(
        properties=properties,
        user_criteria={"max_price": 500000}
    )
    
    # Process results
    for analysis in results:
        print(f"{analysis.property_address}: {analysis.deal_score:.0f}%")

asyncio.run(analyze_multiple_properties())
```

## User Criteria Options

Pass custom criteria to influence analysis:

```python
user_criteria = {
    # Financial constraints
    "max_price": 450000,
    "min_cash_flow": 200,
    "max_cash_investment": 100000,
    
    # Return expectations
    "target_roi": 0.15,        # 15% annual return
    "min_cap_rate": 0.06,      # 6% cap rate
    "target_appreciation": 0.05, # 5% annual appreciation
    
    # Investment preferences
    "preferred_strategy": "buy_and_hold",
    "risk_tolerance": "moderate",  # low, moderate, high
    "hold_period": 60,            # months
    
    # Property preferences
    "min_bedrooms": 3,
    "max_age": 30,
    "preferred_condition": ["good", "excellent"]
}
```

## Error Handling

```python
async def safe_analysis():
    try:
        result = await engine.comprehensive_valuation_analysis(property_data)
        return result
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        # Fallback analysis is automatically generated
        return None
```

## Integration with Deal Finder

The analysis engine can work with the Deal Finder agent:

```python
# Initialize with Deal Finder integration
from agents.deal_finder import DealFinder

deal_finder = DealFinder(api_key)
engine = AnalysisEngine(api_key=api_key, deal_finder=deal_finder)

# Analysis will use Deal Finder for comparable sales data
result = await engine.comprehensive_valuation_analysis(property_data)
```

## Performance Notes

### Processing Time
- **Quick Analysis**: ~2-5 seconds
- **Comprehensive Analysis**: ~10-15 seconds
- **Batch Processing**: ~5-10 seconds per property

### Rate Limits
- Gemini 2.5 Pro: Managed automatically
- Consider delays between batch requests for large datasets

### Memory Usage
- Single analysis: ~10-20MB
- Batch processing: Scale linearly with property count

## Environment Setup

### Required Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
# or
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `google-generativeai`: Gemini API integration
- `pydantic`: Data validation and schemas
- `python-dotenv`: Environment variable management
- `asyncio`: Asynchronous processing

## Advanced Usage

### Custom Adjustment Rates

```python
# Modify professional adjustment rates
engine.adjustment_rates.update({
    'gla_per_sqft': 60.0,        # Increase GLA adjustment
    'bathroom_value': 4000.0,    # Increase bathroom value
    'annual_appreciation': 0.06   # 6% annual appreciation
})
```

### Custom Analysis Prompts

```python
# Modify AI analysis prompts
engine.analysis_prompts['sales_comparison'] = """
Your custom sales comparison analysis prompt here...
"""
```

## API Reference

### Main Methods

| Method | Description | Input | Output |
|--------|-------------|-------|---------|
| `quick_analysis()` | Legacy quick analysis | address, listing_price | Dict with basic results |
| `comprehensive_valuation_analysis()` | Full professional analysis | PropertyFeatures, user_criteria | PropertyAnalysisSchema |
| `analyze_property_batch()` | Batch processing | List[PropertyFeatures], user_criteria | List[PropertyAnalysisSchema] |

### Data Classes

| Class | Purpose | Key Fields |
|-------|---------|------------|
| `PropertyFeatures` | Property input data | address, gla, bedrooms, bathrooms, etc. |
| `ComparableSale` | Comparable sale data | address, sale_price, adjustments, etc. |
| `PropertyAnalysisSchema` | Analysis output | valuation, deal_score, investment_grade, etc. |

## Examples

### Example 1: Fix & Flip Analysis

```python
property_data = PropertyFeatures(
    address="456 Fixer Upper Lane",
    gla=1800,
    bedrooms=3,
    bathrooms=2.0,
    garage_spaces=1,
    lot_size=6000,
    age=25,
    condition='fair',  # Needs work
    property_type='SFR',
    listing_price=280000
)

result = await engine.comprehensive_valuation_analysis(property_data)
print(f"Strategy: {result.investment_strategy.recommended_strategy.value}")
print(f"ARV: ${result.valuation.arv_estimate:,.0f}")
```

### Example 2: Rental Property Analysis

```python
property_data = PropertyFeatures(
    address="789 Rental Income Dr",
    gla=2400,
    bedrooms=4,
    bathrooms=3.0,
    garage_spaces=2,
    lot_size=9000,
    age=8,
    condition='good',
    property_type='SFR',
    listing_price=450000,
    monthly_rent=3200  # Include rental data
)

result = await engine.comprehensive_valuation_analysis(property_data)
cash_flow = result.investment_strategy.financial_projections["cash_flow"]
print(f"Net Cash Flow: ${cash_flow.net_cash_flow:,.0f}/month")
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file exists with `GEMINI_API_KEY` or `GOOGLE_API_KEY`
   - Check environment variable loading with `python-dotenv`

2. **JSON Parsing Errors**
   - The engine includes automatic fallback handling
   - Check network connectivity for Gemini API calls

3. **Import Errors**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path includes the project directory

4. **Performance Issues**
   - Use batch processing for multiple properties
   - Consider implementing request caching for repeated analyses

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
engine = AnalysisEngine(api_key=api_key)
```

## Support

For questions or issues:
1. Check the comprehensive test file: `test_professional_engine.py`
2. Review the analysis schemas: `agents/analysis_schemas.py`
3. Examine the main implementation: `agents/analysis_engine.py`