# 🧪 AI System Testing Guide

## ✅ Quick Test Checklist

### Test 1: Server Running
```
✅ Server started successfully
✅ Port 5000 accessible
✅ 7 AI endpoints registered:
   - /api/ai/alerts
   - /api/ai/chat
   - /api/ai/history
   - /api/ai/insight
   - /api/ai/predict
   - /api/ai/status
   - /api/ai/summary
```

### Test 2: AI Status Endpoint
Open in browser:
```
http://localhost:5000/api/ai/status
```

**Expected Response:**
```json
{
  "success": true,
  "status": "AI system operational",
  "version": "1.0.0",
  "capabilities": [
    "Daily insights generation",
    "Natural language chat",
    "Balance predictions",
    "Anomaly detection",
    "Priority alerts",
    "Conversation history"
  ],
  "endpoints": {
    "insight": "/api/ai/insight",
    "chat": "/api/ai/chat",
    "history": "/api/ai/history",
    "alerts": "/api/ai/alerts",
    "predict": "/api/ai/predict",
    "summary": "/api/ai/summary"
  }
}
```

### Test 3: Daily Insights
Open in browser:
```
http://localhost:5000/api/ai/insight
```

**Expected Response:**
```json
{
  "success": true,
  "insights": [
    {
      "type": "balance",
      "severity": "high",
      "title": "...",
      "message": "..."
    }
  ],
  "anomalies": [...],
  "predictions": [...],
  "timestamp": "2024-..."
}
```

### Test 4: Chat Endpoint (PowerShell)
```powershell
# Create a test session file
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Make chat request
$body = @{message = "Quanto tenho de saldo?"} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body `
  -WebSession $session
```

**Expected Response:**
```json
{
  "success": true,
  "ai_response": "💰 **Seu Saldo Atual**\n\nVocê tem R$ ...",
  "intent": "saldo",
  "context": {...}
}
```

### Test 5: UI Components

#### A. Dashboard with Floating Button
1. Open: http://localhost:5000/dashboard
2. Look for purple floating button (bottom-right corner)
3. Button should have message icon (💬)
4. Green pulse indicator should be visible

#### B. Click Floating Button
1. Click the button
2. Chat panel should slide up from bottom
3. Button icon changes to X
4. Button color changes to red
5. Welcome message should appear from AI

#### C. Test Chat Interface
1. Type: "Quanto tenho de saldo?"
2. Press Enter or click Send button
3. Loading indicator should appear
4. AI response should appear with:
   - Markdown formatting
   - Emojis (💰, 📊, etc.)
   - Proper styling (gray bubble, left-aligned)

#### D. Quick Questions
1. Click any of the quick question buttons
2. Question should auto-populate input
3. Response should be generated automatically

#### E. AI Panel
1. Open: http://localhost:5000/ai
2. Should see 4 tabs:
   - Insights do Dia
   - Previsões
   - Alertas
   - Chat com IA
3. Click each tab and verify content loads
4. Check for charts in Predictions tab

---

## 🔍 Detailed Test Scenarios

### Scenario 1: New User (No Data)
**Steps:**
1. Login with a new account
2. Open dashboard
3. Click AI floating button
4. Ask: "Quanto tenho de saldo?"

**Expected:**
- AI responds with "Saldo: R$ 0,00"
- Message mentions no transactions yet
- Suggests adding transactions

### Scenario 2: User with Transactions
**Steps:**
1. Login with account that has transactions
2. Ask: "Quanto gastei este mês?"

**Expected:**
- AI shows total expenses
- Breakdown by category (top 3)
- Comparison with previous month if available

### Scenario 3: Category Query
**Steps:**
1. Ask: "Quanto gastei com alimentação?"

**Expected:**
- AI extracts "alimentação" category
- Shows specific spending for that category
- Percentage of total expenses
- Comparison with other categories

### Scenario 4: Investment Query
**Steps:**
1. User with investments
2. Ask: "Como estão meus investimentos?"

**Expected:**
- Total portfolio value
- Individual assets
- Current profit/loss
- Average return rate

### Scenario 5: Prediction Query
**Steps:**
1. Ask: "Qual a previsão para 30 dias?"

**Expected:**
- Predicted balance for 30 days
- Confidence score
- Trend indicator (growing/declining)
- Disclaimer about prediction accuracy

### Scenario 6: Unknown Intent
**Steps:**
1. Ask: "Qual o sentido da vida?"

**Expected:**
- Friendly fallback message
- Suggestions of what AI can help with
- List of sample questions

---

## 📊 API Response Time Tests

Use PowerShell to measure response times:

```powershell
# Test insight endpoint
Measure-Command {
  Invoke-RestMethod -Uri "http://localhost:5000/api/ai/insight"
}

# Target: < 2 seconds

# Test chat endpoint
$body = @{message = "Quanto tenho?"} | ConvertTo-Json
Measure-Command {
  Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
    -Method POST -ContentType "application/json" -Body $body
}

# Target: < 500 milliseconds

# Test prediction endpoint
Measure-Command {
  Invoke-RestMethod -Uri "http://localhost:5000/api/ai/predict?days=30"
}

# Target: < 1 second
```

---

## 🐛 Error Testing

### Test 1: Unauthenticated Request
```powershell
# Should return 401 Unauthorized
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" `
  -Body '{"message": "test"}'
```

### Test 2: Invalid JSON
```powershell
# Should return 400 Bad Request
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" `
  -Body 'invalid json'
```

### Test 3: Empty Message
```powershell
# Should return error message
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" `
  -Body '{"message": ""}'
```

### Test 4: Very Long Message
```powershell
# Should handle gracefully (truncate or error)
$longMessage = "a" * 10000
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" `
  -Body (@{message = $longMessage} | ConvertTo-Json)
```

---

## 🎨 UI/UX Testing

### Visual Tests
- [ ] Floating button is visible and not covered by other elements
- [ ] Chat panel doesn't overflow screen
- [ ] Messages are readable (good font size, contrast)
- [ ] Markdown renders correctly (bold, lists, code blocks)
- [ ] Emojis display properly
- [ ] Loading indicators are visible
- [ ] Error messages are user-friendly

### Interaction Tests
- [ ] Button responds to hover (cursor: pointer)
- [ ] Chat panel opens/closes smoothly
- [ ] Input field accepts text
- [ ] Enter key sends message
- [ ] Send button is clickable
- [ ] Quick questions are clickable
- [ ] Auto-scroll works on new messages
- [ ] Chat history persists during session

### Responsive Tests
- [ ] Works on desktop (1920x1080)
- [ ] Works on laptop (1366x768)
- [ ] Works on tablet (768px width)
- [ ] Works on mobile (375px width)
- [ ] Chat panel doesn't exceed viewport

---

## 📱 Browser Compatibility

Test on:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)

Common issues:
- Flexbox support (should be fine, all modern browsers)
- CSS Grid support (all modern browsers)
- Fetch API (all modern browsers)
- Async/await (all modern browsers)

---

## 🔒 Security Tests

### Test 1: SQL Injection
```powershell
# Try SQL injection in message
$body = @{message = "'; DROP TABLE users; --"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" -Body $body
```
**Expected:** AI treats it as normal text, no SQL execution

### Test 2: XSS Attempt
```powershell
# Try XSS in message
$body = @{message = "<script>alert('xss')</script>"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -ContentType "application/json" -Body $body
```
**Expected:** Script tags escaped/sanitized in response

### Test 3: CSRF Protection
```powershell
# Try request from different origin (should be blocked by CORS)
Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
  -Method POST -Headers @{Origin = "http://evil.com"} `
  -ContentType "application/json" -Body '{"message": "test"}'
```
**Expected:** CORS error or 403 Forbidden

---

## 📈 Load Testing (Optional)

### Simple Load Test
```powershell
# Send 10 concurrent requests
1..10 | ForEach-Object -Parallel {
  $body = @{message = "test $_"} | ConvertTo-Json
  Invoke-RestMethod -Uri "http://localhost:5000/api/ai/chat" `
    -Method POST -ContentType "application/json" -Body $body
} -ThrottleLimit 10
```

**Expected:**
- All requests succeed
- No server crashes
- Response times remain reasonable

---

## ✅ Final Checklist

Before marking as "Production Ready":

**Backend:**
- [ ] All 7 endpoints respond correctly
- [ ] Database tables created (ai_history.db)
- [ ] Conversation history saves
- [ ] Insights generate without errors
- [ ] Predictions calculate correctly
- [ ] Anomalies detect properly
- [ ] Error handling works

**Frontend:**
- [ ] Floating button appears
- [ ] Chat panel opens/closes
- [ ] Messages send and receive
- [ ] Markdown renders
- [ ] Loading states show
- [ ] Error messages display
- [ ] AI Panel route works
- [ ] All tabs functional

**Integration:**
- [ ] Login required for API
- [ ] Tenant isolation working
- [ ] Session management correct
- [ ] CORS configured properly
- [ ] Frontend built successfully
- [ ] No console errors

**Documentation:**
- [ ] AI_SYSTEM_DOCUMENTATION.md complete
- [ ] AI_QUICKSTART.md clear
- [ ] AI_IMPLEMENTATION_SUMMARY.md accurate
- [ ] requirements_ai.txt up-to-date
- [ ] Code comments sufficient

**Performance:**
- [ ] Chat response < 500ms
- [ ] Insights generation < 2s
- [ ] Predictions < 1s
- [ ] Frontend bundle < 1MB

---

## 🎉 Success Criteria

System is ready when:
1. ✅ Server starts without errors
2. ✅ All AI endpoints accessible
3. ✅ Chat responds to questions
4. ✅ UI components render correctly
5. ✅ No JavaScript errors in console
6. ✅ Documentation is complete
7. ✅ Dependencies installed

---

## 📞 Troubleshooting

**Problem:** Floating button doesn't appear
**Check:**
- Frontend built? `npm run build`
- AIFloatingButton imported in DashboardFinanceira.jsx?
- Browser console errors?

**Problem:** Chat doesn't respond
**Check:**
- Server running? `python app.py`
- Logged in? AI requires authentication
- Network tab shows 200 response?

**Problem:** "Module not found" errors
**Check:**
- Python packages installed? `pip install -r requirements_ai.txt`
- Frontend packages installed? `cd frontend && npm install`

**Problem:** Markdown not rendering
**Check:**
- react-markdown installed? `npm list react-markdown`
- Import statement correct in AIChat.jsx?

---

**All tests passing = System ready for production! 🚀**
