# Frontend Integration Testing Guide

## How to Test the Frontend Integration

### Prerequisites
1. Make sure the customer agent server is running:
   ```bash
   python customer_agent_server.py
   ```
   The server should be running on `http://localhost:8001`

2. Open the Try EquityNest page:
   ```
   frontend/pages/try-equitynest.html
   ```

### Test Steps

1. **Fill out the form**:
   - **Location**: Enter a location like "Austin, TX" or "New York" 
   - **Property Types**: Check one or more boxes:
     - 🏠 Primary Residence
     - 🔨 Fix & Flip  
     - 🏘️ Rental Property
     - 🏢 Multi-Family
     - ⚡ Quick Deals
   - **Budget**: Set a budget range using the dropdowns or custom inputs

2. **Click "Search Properties with AI"**

3. **Check Browser Console** (F12 → Console):
   You should see debugging output like:
   ```
   🎯 Detected Try EquityNest page, initializing demo functionality...
   🔍 Handling property search...
   📋 Collecting form data...
   📍 Location: Austin, TX
   🏠 Property types: ['fix-flip', 'rental-property']
   💵 Budget: { min: 200000, max: 500000 }
   ✅ Validation passed, starting chatbot with form data
   🤖 Starting chatbot with form data: {...}
   📤 Sending to chatbot API: {...}
   📥 API Response status: 200
   ✅ Chatbot session started: {...}
   ```

4. **Expected Result**:
   - Form disappears
   - Chatbot interface appears
   - Bot greets you with a personalized message acknowledging your form input:
     > "Hi there! I see you're interested in properties in Austin, TX, looking for fix and flip opportunities and rental properties, with a budget of $200,000 - $500,000. That's exciting! What's driving your interest in real estate investing right now?"

### Common Issues and Solutions

#### Issue 1: "Search button not found" 
**Cause**: Demo page not properly initialized
**Solution**: Check console for the auto-detection message. The page should automatically detect it's on try-equitynest.html

#### Issue 2: "Please enter a location" alert
**Cause**: Location field is empty
**Solution**: Make sure you enter something in the location field

#### Issue 3: "Please select at least one property type" alert  
**Cause**: No checkboxes selected
**Solution**: Check at least one property type checkbox

#### Issue 4: "Failed to start chatbot" with network error
**Cause**: Customer agent server not running
**Solution**: Start the server with `python customer_agent_server.py`

#### Issue 5: CORS errors
**Cause**: Browser blocking cross-origin requests
**Solution**: The server has CORS enabled, but you may need to serve the HTML file from a local server instead of opening it directly

### Debug Information

The browser console will show detailed information about:
- Form data collection
- Validation results  
- API requests and responses
- Chatbot session creation
- Any errors that occur

### Manual Server Testing

You can also test the server directly:

```bash
curl -X POST http://localhost:8001/chat/start \
  -H "Content-Type: application/json" \
  -d '{
    "frontend_data": {
      "location": "Austin, TX",
      "property_types": ["fix-flip", "rental-property"], 
      "budget_min": 200000,
      "budget_max": 500000
    }
  }'
```

Expected response:
```json
{
  "session_id": "some-uuid",
  "message": "Hi there! I see you're interested in properties in Austin, TX...",
  "status": "active"
}
```