# 🎬 FlowSupport AI - Complete Demo Walkthrough

This document walks through the complete FlowSupport AI system, demonstrating how it handles three different support scenarios and how TAMs monitor everything through a unified dashboard.

---

## 🎯 What You're About to See

FlowSupport AI is an end-to-end customer success automation platform that demonstrates:

### **For Customers (localhost:8501)**
- Submit support requests through an intuitive form
- Get instant AI-powered responses from a knowledge base
- Provide feedback on whether solutions worked
- Receive automatic escalation to specialists when needed

### **For TAMs (localhost:8502)**
- Monitor all customer health metrics in real-time
- View complete ticket history with full AI context
- Receive Slack notifications for escalated issues
- Generate proactive outreach for at-risk customers
- Track AI performance through analytics

### **The Intelligence**
- **RAG Architecture**: Gemini 2.0 Flash + ChromaDB with 126 embedded document chunks
- **Confidence-Based Routing**: AI responds when confident, escalates when uncertain
- **Context Preservation**: Every ticket stores what AI attempted, confidence scores, and retrieved documents
- **Smart Escalation**: Policy-based (billing/privacy) + confidence-based (technical) + user feedback

---

## 📖 Demo Scenarios

We'll walk through three scenarios that showcase different system capabilities:

1. **Sarah Chen** - Technical issue that AI solves successfully
2. **Mike Rodriguez** - Billing dispute that requires immediate human escalation
3. **John Davis** - Technical issue where AI tries but user needs more help

---

## 🎬 Scenario 1: AI Successfully Resolves Issue

**Customer:** Sarah Chen from Design Co  
**Issue:** Mac transcription cutting off midway through dictation  
**Expected Outcome:** AI provides solution → User confirms it worked → Ticket closed

---

### **Step 1: Customer Submits Request**

![Sarah Chen submits form](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173138.png)

**What's happening:**
- Customer fills out the support form with their Mac transcription issue
- Form captures: name, email, device type, request type, detailed description
- One-click submission

---

### **Step 2: AI Generates Solution**

![Sarah receives AI solution](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173201.png)

**What's happening:**
- RAG agent searches knowledge base using semantic similarity
- Retrieves 3 relevant documents about Mac transcription issues
- Gemini 2.0 Flash generates tailored troubleshooting steps
- **AI Confidence: 42.7%** (above 45% threshold would auto-solve, but user feedback is shown)
- Response time: **5604ms** (under 3 seconds for AI generation)
- **Two feedback buttons appear:** "✅ Yes, solved!" and "❌ No, need help"

**Key Feature:** Notice the expandable "Knowledge Base Sources" section showing:
- Which documents were retrieved
- Page numbers for reference
- Relevance scores for transparency

---

### **Step 3: User Confirms Solution Worked**

![Success confirmation](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173222.png)

**What's happening:**
- Sarah clicks "✅ Yes, solved!" 
- System immediately:
  - Updates ticket **ZD-1001** status to "solved"
  - Sets escalated flag to `false`
  - Triggers confirmation email (simulated)
- **No human intervention needed** ✅

**Behind the scenes (tickets.json):**

![Ticket data](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173244.png)
```json
{
  "id": "ZD-1001",
  "status": "solved",
  "ai_analysis": {
    "confidence": 0.4274,
    "escalated": false,
    "team": "tech_mac",
    "response": "OK. Based on the provided documentation..."
  }
}
```

**Result:** Customer gets instant help, TAM workload reduced, full context preserved for analytics.

---

## 🎬 Scenario 2: Policy-Based Escalation

**Customer:** Mike Rodriguez from TechStart Inc  
**Issue:** Charged twice on credit card  
**Expected Outcome:** Immediate escalation to billing team (no AI response needed)

---

### **Step 1: Customer Submits Billing Issue**

![Mike submits billing form](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173307.png)

**What's happening:**
- Mike selects **"Billing"** as request type
- Describes being charged twice ($10 each on Dec 10th and 11th)
- System recognizes this as a billing dispute

---

### **Step 2: Immediate Escalation**

![Billing escalation](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173331.png)

**What's happening:**
- **No AI solution shown** (billing requires human verification)
- Ticket immediately escalated to billing team
- **Priority: HIGH** (billing disputes are high-priority)
- Email confirmation shows:
  - Ticket ID: **ZD-1002**
  - Team assigned: **Billing**
  - Expected response: **Within 4 hours**
  - AI attempted to provide context but escalated per policy

**Behind the scenes (slack_notifications.json):**

![Slack notification](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173352.png)
```json
{
  "id": "NOTIF-1",
  "channel": "#cs-billing",
  "priority": "high",
  "message": {
    "title": "🎫 New HIGH Priority Ticket",
    "customer": "Mike Rodriguez",
    "ticket_id": "ZD-1002",
    "issue_description": "I was charged twice..."
  }
}
```

**Behind the scenes (tickets.json):**

![Ticket data](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173421.png)

**Terminal output confirms:**
```
✅ Created ticket: ZD-1002
✅ Sent notification to #cs-billing
📧 Slack notification sent: NOTIF-1
```

**Result:** Billing team immediately notified via Slack, customer expectations set, no AI speculation on sensitive financial matters.

---

## 🎬 Scenario 3: AI Attempts → User Feedback → Escalation

**Customer:** John Davis from Acme Corp  
**Issue:** Windows installer failing with error code 0x80070005  
**Expected Outcome:** AI tries → User says "not helpful" → Escalates with full context

---

### **Step 1: Customer Submits Technical Issue**

![John submits form](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173446.png)

**What's happening:**
- Windows installation error with specific error code
- Request Type: **Issue** (technical)
- System will attempt AI resolution first

---

### **Step 2: AI Provides Troubleshooting Steps**

![AI solution provided](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173502.png)

**What's happening:**
- AI retrieves Windows installation troubleshooting docs
- Generates comprehensive step-by-step solution:
  1. Verify system requirements
  2. Address error code 0x80070005 (Access Denied)
  3. Complete uninstall & clean-up steps
  4. Re-download installer
  5. Run as administrator
  6. Temporarily disable antivirus
  7. Check VPN/proxy interference
- **AI Confidence: 49.1%** (borderline - showing feedback buttons)
- **Feedback buttons visible:** User decides if this worked

**This is the critical moment:** AI did its best, now user validates if solution worked.

---

### **Step 3: User Indicates Solution Didn't Work**

![Escalation after feedback](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173522.png)

**What's happening:**
- John clicks "❌ No, need help"
- System **immediately**:
  - Updates **ZD-1003** from solved → **open**
  - Sets escalated flag to `true`
  - Sends Slack notification to **#cs-tech-windows**
  - Shows escalation email with **full context for TAM**

**Email provides TAM with:**
- What AI attempted (troubleshooting steps)
- AI confidence score (49.1%)
- Documents retrieved (3 sources)
- Device info (Windows)
- Original error code (0x80070005)

**This is context preservation in action:** TAM doesn't start from scratch, they see exactly what AI tried and can build on it or try different approach.

**Behind the scenes (tickets.json):**

![Updated ticket](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173536.png)
```json
{
  "id": "ZD-1003",
  "status": "open",  // Changed from "solved" after feedback
  "ai_analysis": {
    "confidence": 0.491,
    "escalated": true,  // Updated after user clicked "No"
    "team": "tech_windows",
    "response": "Okay, here's a troubleshooting plan..."
  }
}
```

**Behind the scenes (slack_notifications.json):**

![Slack notification](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173642.png)
```json
{
  "id": "NOTIF-2",
  "channel": "#cs-tech-windows",
  "priority": "low",
  "message": {
    "customer": "John Davis",
    "ai_confidence": 0.491,
    "ai_response": "Okay, here's a troubleshooting plan...",
    "issue_description": "I downloaded Flow but the installer keeps failing..."
  }
}
```

**Terminal confirms the workflow:**


```
✅ Created ticket: ZD-1003
✅ Updated ticket ZD-1003: status=open, escalated=True
✅ Sent notification to #cs-tech-windows
📧 Slack notification sent after feedback: NOTIF-2
```

**Result:** Windows specialist gets notified with full context, knows what AI already tried, can provide more advanced troubleshooting.

---

## 📊 TAM Dashboard - Complete Operations View

Now let's see how TAMs monitor all of this activity through the unified dashboard (localhost:8502).

---

### **Page 1: Support Tickets Overview**

![Support tickets page](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173704.png)

**What TAMs see:**
- **Summary metrics:**
  - Total: 3 tickets
  - Open: 2 (Mike, John)
  - Solved: 1 (Sarah)
  - Escalated: 2 (Mike, John)
  
- **All tickets in one view:**
  - 🔴 ZD-1003 - John Davis - Flow won't install (OPEN)
  - 🔴 ZD-1002 - Mike Rodriguez - Charged twice (OPEN)
  - 🟢 ZD-1001 - Sarah Chen - Transcription issue (SOLVED)

- **Filterable by:**
  - Status (All, open, solved)
  - Priority (All, urgent, high, medium, low)
  - Device (All, Mac, Windows, iOS)

---

### **Expanded Ticket View**

![Expanded ticket details](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173730.png)

**What TAMs see for each ticket:**
- **Customer info:** Name, email
- **Issue details:** Full description
- **AI response:** What AI attempted (first 300 chars)
- **Status:** open/solved
- **Priority:** With color coding (🟠 high, 🟡 medium, 🟢 low)
- **Device type:** Mac/Windows/iOS
- **AI Confidence:** Percentage score
- **Created date:** Timestamp
- **Team assigned:** billing/tech_mac/tech_windows/etc.

**This is the "single source of truth" for all support activity.**

---

### **Page 2: Slack Notifications**

![Slack notifications](https://github.com/devaki264/flowsupportai_2.0/blob/main/screenshots/Screenshot%202025-12-12%20173754.png)

**What TAMs see:**
- **Summary:** Total: 2, Unread: 2
- **"Mark All as Read" button** for bulk operations
- **All notifications listed:**
  - 🔴 UNREAD | 🟢 #cs-tech-windows - New LOW Priority Ticket (John)
  - 🔴 UNREAD | 🟠 #cs-billing - New HIGH Priority Ticket (Mike)

**Expandable cards show:**
- Customer name & email
- Issue subject & description
- AI attempted response
- Ticket ID & link
- Channel routed to
- Device type
- Priority level
- AI confidence score
- Timestamp
- "Mark as Read" button

**This simulates real Slack webhooks** - in production, these would appear in actual Slack channels like #cs-billing, #cs-tech-windows, etc.

---

### **Page 3: Analytics & Performance**

![Analytics overview](docs/screenshots/Screenshot__2969_.png)

**Key Metrics (Top Row):**
- **Total Tickets:** 3
- **AI Resolution Rate:** 33.3% (1 out of 3 solved without human)
- **Escalated:** 2
- **Avg AI Confidence:** 42.7%

**Charts:**

1. **📈 AI Resolution Rate Over Time**
   - Line chart showing trend of AI vs human resolution
   - Helps identify if AI is improving or degrading

2. **🎯 Tickets by Priority**
   - High: 1 ticket (Mike - billing)
   - Low: 2 tickets (Sarah, John)
   - Helps resource allocation

3. **💻 Tickets by Device Type**
   - Mac: 1 ticket (Sarah)
   - Windows: 2 tickets (Mike, John)
   - Helps identify platform-specific issues

4. **⚡ Response Times by Date**
   - Shows average response time trends
   - Identifies performance bottlenecks

![Analytics charts](docs/screenshots/Screenshot__2970_.png)

5. **📢 Slack Notifications by Channel**
   - Shows distribution of escalations across teams
   - Helps identify overloaded teams

**Detailed Statistics:**
- Total tickets: 3
- Open: 2, Solved: 1
- AI Resolved: 1
- Escalated: 2
- Escalation Rate: 66.7%
- Avg AI Confidence: 42.7%
- Total Notifications: 2
- Unread Notifications: 2
- Unique Channels Used: 2

**This provides leadership with data-driven insights into AI performance and team workload.**

---

## 🎯 Summary: What We Just Demonstrated

### **Three Complete Workflows:**

| Scenario | Customer | Issue Type | AI Confidence | Outcome | Slack | Time |
|----------|----------|------------|---------------|---------|-------|------|
| 1 | Sarah Chen | Technical (Mac) | 42.7% | User confirmed → Solved | ❌ None | 5.6s |
| 2 | Mike Rodriguez | Billing | 36.3% | Policy escalation → Open | ✅ #cs-billing | 65ms |
| 3 | John Davis | Technical (Windows) | 49.1% | User rejected → Escalated | ✅ #cs-tech-windows | 8.2s |

---

### **System Capabilities Shown:**

✅ **RAG-Powered AI Agent**
- Semantic search over 126 document chunks
- Confidence scoring for quality control
- Sub-3s response generation

✅ **Intelligent Decision Engine**
- Policy-based routing (billing → immediate escalation)
- Confidence-based routing (low confidence → escalate)
- User feedback loop (user validation)

✅ **Context Preservation**
- Full AI analysis stored with every ticket
- Retrieved documents tracked
- Confidence scores logged
- Team assignments preserved

✅ **Real-Time Operations**
- Ticket persistence across sessions
- Slack notifications with rich context
- Channel-based routing (#cs-billing, #cs-tech-windows)

✅ **TAM Empowerment**
- Unified customer view (tickets + health + notifications)
- Proactive outreach recommendations
- Performance analytics
- Complete ticket filtering

✅ **Production-Ready Patterns**
- Simulates Zendesk ticket system
- Simulates Slack webhook integration
- Demonstrates CRM data model
- Shows workflow automation logic

---

## 💡 What Makes This Different

**Most CS chatbots:**
- Answer questions
- That's it

**FlowSupport AI:**
- Answers questions (RAG agent)
- Decides when to escalate (confidence + policy)
- Routes to correct team (device-specific channels)
- Preserves context (TAM sees AI's attempt)
- Monitors customer health (proactive CS)
- Tracks performance (analytics)
- Enables TAM workflows (unified dashboard)

**This is an operations platform, not just a chatbot.**

---

## 🚀 Technical Implementation

**Want to dive deeper into how this works?**

- [Architecture Documentation](ARCHITECTURE.md) - RAG design, decision engine logic, data models
- [Setup Guide](SETUP.md) - Run this locally in 5 minutes
- [README](README.md) - Project overview & tech stack

---

**Built by Devakinandan Palla** 

Demonstrating the exact capabilities from the Wispr Flow Customer Success AI Agent Engineer role.






