# dashboard_tam.py

import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.synthetic_customers import CUSTOMERS
from src.integrations.local_ticketing import LocalTicketSystem
from src.integrations.local_slack import LocalSlackSimulator

st.set_page_config(page_title="TAM Dashboard", page_icon="🎯", layout="wide")

# Initialize systems
@st.cache_resource
def init_systems():
    return LocalTicketSystem(), LocalSlackSimulator()

ticket_system, slack_sim = init_systems()

# Sidebar navigation
st.sidebar.title("🎯 TAM Dashboard")
page = st.sidebar.radio(
    "Navigation",
    ["Customer Health", "Support Tickets", "Slack Notifications", "Proactive Outreach", "Analytics"],
    label_visibility="collapsed"
)

# ============================================================================
# PAGE 1: CUSTOMER HEALTH
# ============================================================================
if page == "Customer Health":
    st.title("👥 Customer Health Dashboard")
    
    # Customer selector
    customer_names = [c["name"] for c in CUSTOMERS]
    selected = st.selectbox("Select Customer", customer_names, label_visibility="collapsed")
    
    customer = next(c for c in CUSTOMERS if c["name"] == selected)
    
    # Health score banner
    if customer["churn_risk"] == "CRITICAL":
        st.error(f"🔴 CRITICAL RISK: {customer['name']} - Health Score: {customer['health_score']}/100")
    elif customer["churn_risk"] == "HIGH":
        st.warning(f"🟠 HIGH RISK: {customer['name']} - Health Score: {customer['health_score']}/100")
    elif customer["churn_risk"] == "MEDIUM":
        st.info(f"🟡 MEDIUM RISK: {customer['name']} - Health Score: {customer['health_score']}/100")
    else:
        st.success(f"🟢 HEALTHY: {customer['name']} - Health Score: {customer['health_score']}/100")
    
    # Key metrics (4 columns)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Contract Value", f"${customer['contract_value']:,}")
        days_to_renewal = (datetime.strptime(customer['renewal_date'], '%Y-%m-%d') - datetime.now()).days
        st.metric("Days to Renewal", days_to_renewal)
    
    with col2:
        usage_change = customer['usage']['last_7_days'] - customer['usage']['avg_weekly']
        st.metric("Usage (7 days)", f"{customer['usage']['last_7_days']}h", 
                 delta=f"{usage_change:+.0f}h")
        st.metric("Last Active", customer["usage"]["last_active"])
    
    with col3:
        total_features = len(customer['features']['adopted']) + len(customer['features']['not_adopted'])
        st.metric("Features Adopted", f"{len(customer['features']['adopted'])}/{total_features}")
        st.metric("Open Tickets", customer["support"]["open_tickets"])
    
    with col4:
        if customer["support"]["resolved_this_month"] > 0:
            ai_rate = (customer["support"]["ai_resolved"] / customer["support"]["resolved_this_month"]) * 100
        else:
            ai_rate = 0
        st.metric("AI Resolution Rate", f"{ai_rate:.0f}%")
        if customer["support"]["avg_response_time_ms"] > 0:
            st.metric("Avg Response Time", f"{customer['support']['avg_response_time_ms']}ms")
        else:
            st.metric("Avg Response Time", "N/A")
    
    # Alerts section
    st.markdown("---")
    st.markdown("## 🚨 Alerts")
    
    alerts_shown = False
    
    if customer["usage"]["trend"] == "DOWN":
        alerts_shown = True
        drop_pct = ((customer['usage']['avg_weekly'] - customer['usage']['last_7_days']) / customer['usage']['avg_weekly']) * 100
        st.error(f"""
        **⚠️ Usage Drop Detected**
        - Usage dropped {drop_pct:.0f}% this week
        - From {customer['usage']['avg_weekly']}h → {customer['usage']['last_7_days']}h
        - **Recommended Action:** Proactive check-in call
        """)
    
    if days_to_renewal < 45 and customer["churn_risk"] in ["HIGH", "CRITICAL"]:
        alerts_shown = True
        st.warning(f"""
        **⚠️ Renewal Risk**
        - Renewal in {days_to_renewal} days
        - Health score: {customer['health_score']}/100
        - **Recommended Action:** Schedule renewal conversation
        """)
    
    if len(customer['features']['not_adopted']) > 0:
        alerts_shown = True
        st.info(f"""
        **💡 Feature Adoption Opportunity**
        - Not using: {', '.join(customer['features']['not_adopted'])}
        - **Recommended Action:** Schedule feature demo
        """)
    
    if not alerts_shown:
        st.success("✅ No alerts - customer is healthy!")
    
    # Support history
    st.markdown("---")
    st.markdown("## 💬 Support History")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        **This Month:**
        - AI Resolved: {customer['support']['ai_resolved']} tickets
        - Escalated: {customer['support']['escalated']} tickets
        - Open: {customer['support']['open_tickets']} tickets
        """)
    with col2:
        st.markdown(f"""
        **Performance:**
        - Avg Response: {customer['support']['avg_response_time_ms']}ms
        - AI Resolution Rate: {ai_rate:.0f}%
        """)

# ============================================================================
# PAGE 2: SUPPORT TICKETS
# ============================================================================
elif page == "Support Tickets":
    st.title("🎫 Support Tickets")
    
    tickets = ticket_system.get_all_tickets()
    
    if not tickets:
        st.info("📭 No tickets yet. Submit a support request to see tickets here.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", len(tickets))
        with col2:
            open_tickets = [t for t in tickets if t["status"] == "open"]
            st.metric("Open", len(open_tickets))
        with col3:
            solved_tickets = [t for t in tickets if t["status"] == "solved"]
            st.metric("Solved", len(solved_tickets))
        with col4:
            escalated = [t for t in tickets if t["ai_analysis"]["escalated"]]
            st.metric("Escalated", len(escalated))
        
        st.markdown("---")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "open", "solved"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "urgent", "high", "medium", "low"])
        with col3:
            device_filter = st.selectbox("Device", ["All", "Mac", "Windows", "iOS"])
        
        # Apply filters
        filtered = tickets
        if status_filter != "All":
            filtered = [t for t in filtered if t["status"] == status_filter]
        if priority_filter != "All":
            filtered = [t for t in filtered if t["priority"] == priority_filter]
        if device_filter != "All":
            filtered = [t for t in filtered if t["device_type"] == device_filter]
        
        st.markdown(f"**Showing {len(filtered)} tickets**")
        
        # Display tickets
        for ticket in reversed(filtered):  # Most recent first
            status_color = "🟢" if ticket["status"] == "solved" else "🔴"
            priority_icon = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(ticket["priority"], "⚪")
            
            with st.expander(f"{status_color} {ticket['id']} - {ticket['subject']} ({ticket['status'].upper()})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Customer:** {ticket['requester']['name']} ({ticket['requester']['email']})")
                    st.markdown(f"**Issue:** {ticket['description']}")
                    st.markdown(f"**AI Response:** {ticket['ai_analysis']['response'][:300]}...")
                
                with col2:
                    st.markdown(f"**Status:** {ticket['status']}")
                    st.markdown(f"**Priority:** {priority_icon} {ticket['priority']}")
                    st.markdown(f"**Device:** {ticket['device_type']}")
                    st.markdown(f"**AI Confidence:** {ticket['ai_analysis'].get('confidence', 0):.1%}")
                    st.markdown(f"**Created:** {ticket['created_at'][:10]}")
                    st.markdown(f"**Team:** {ticket['ai_analysis'].get('team', 'N/A')}")

# ============================================================================
# PAGE 3: SLACK NOTIFICATIONS
# ============================================================================
elif page == "Slack Notifications":
    st.title("🔔 Slack Notifications")
    
    notifications = slack_sim.get_all_notifications()
    
    if not notifications:
        st.success("📭 No notifications yet. Escalate tickets to see notifications here.")
    else:
        unread = slack_sim.get_unread_notifications()
        
        # Summary
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Notifications", len(notifications))
        with col2:
            st.metric("Unread", len(unread))
        
        if len(unread) > 0:
            if st.button("Mark All as Read"):
                slack_sim.mark_all_as_read()
                st.rerun()
        
        st.markdown("---")
        
        # Display notifications
        for notif in reversed(notifications):
            channel_icon = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(notif["priority"], "⚪")
            read_status = "✅ READ" if notif.get("read") else "🔴 UNREAD"
            
            with st.expander(f"{read_status} | {channel_icon} {notif['channel']} - {notif['message']['title']}"):
                msg = notif['message']
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Customer:** {msg['customer']} ({msg['customer_email']})")
                    st.markdown(f"**Issue:** {msg['issue_subject']}")
                    st.markdown(f"**Description:** {msg['issue_description']}")
                    st.markdown(f"**AI Attempted:** {msg['ai_response']}")
                
                with col2:
                    st.markdown(f"**Ticket:** {msg['ticket_id']}")
                    st.markdown(f"**Channel:** {notif['channel']}")
                    st.markdown(f"**Device:** {msg['device']}")
                    st.markdown(f"**Priority:** {notif['priority']}")
                    st.markdown(f"**AI Confidence:** {msg['ai_confidence']:.1%}")
                    st.markdown(f"**Time:** {notif['timestamp'][:19]}")
                
                if not notif.get("read"):
                    if st.button("Mark as Read", key=notif['id']):
                        slack_sim.mark_as_read(notif['id'])
                        st.rerun()

# ============================================================================
# PAGE 4: PROACTIVE OUTREACH
# ============================================================================
elif page == "Proactive Outreach":
    st.title("🤖 Proactive Outreach Queue")
    
    # Find customers needing outreach
    needs_outreach = [c for c in CUSTOMERS if c["churn_risk"] in ["HIGH", "CRITICAL"]]
    
    if not needs_outreach:
        st.success("✅ All customers healthy - no proactive outreach needed!")
    else:
        st.warning(f"⚠️ {len(needs_outreach)} customers need proactive outreach")
        
        for customer in needs_outreach:
            risk_color = "🔴" if customer["churn_risk"] == "CRITICAL" else "🟠"
            
            with st.expander(f"{risk_color} {customer['name']} - {customer['churn_risk']} RISK (Health: {customer['health_score']}/100)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("### 📧 AI-Generated Draft Email")
                    
                    # Generate personalized outreach based on issue
                    if customer["usage"]["trend"] == "DOWN":
                        drop_pct = ((customer['usage']['avg_weekly'] - customer['usage']['last_7_days']) / customer['usage']['avg_weekly']) * 100
                        
                        draft = f"""**To:** {customer['contact_email']}  
**Subject:** Quick check-in on {customer['name']}'s Flow usage

Hi {customer['contact_name'].split()[0]},

I noticed your team's Flow usage dropped {drop_pct:.0f}% this week (from {customer['usage']['avg_weekly']}h to {customer['usage']['last_7_days']}h).

Is everything okay? Common reasons for drops:
- Team members out on holiday
- Technical issues we should address  
- Workflow changes we could help optimize

Happy to hop on a quick 15-min call to make sure you're getting the most value from Flow.

Best,
[Your TAM Name]"""
                        
                        st.text_area("Draft Email", draft, height=300, key=f"draft_{customer['id']}")
                    
                    # Action buttons
                    cols = st.columns(3)
                    with cols[0]:
                        st.button("✅ Send Now", key=f"send_{customer['id']}")
                    with cols[1]:
                        st.button("📅 Schedule", key=f"schedule_{customer['id']}")
                    with cols[2]:
                        st.button("✏️ Edit", key=f"edit_{customer['id']}")
                
                with col2:
                    st.markdown("### 📊 Context")
                    st.markdown(f"**Health Score:** {customer['health_score']}/100")
                    st.markdown(f"**Churn Risk:** {customer['churn_risk']}")
                    st.markdown(f"**Contract Value:** ${customer['contract_value']:,}")
                    days_to_renewal = (datetime.strptime(customer['renewal_date'], '%Y-%m-%d') - datetime.now()).days
                    st.markdown(f"**Renewal:** {days_to_renewal} days")
                    st.markdown(f"**Open Tickets:** {customer['support']['open_tickets']}")
                    st.markdown(f"**Last Active:** {customer['usage']['last_active']}")
                    st.markdown(f"**Usage Trend:** {customer['usage']['trend']}")

# ============================================================================
# PAGE 5: ANALYTICS
# ============================================================================
elif page == "Analytics":
    st.title("📊 Analytics & Performance")
    
    tickets = ticket_system.get_all_tickets()
    notifications = slack_sim.get_all_notifications()
    
    if len(tickets) == 0:
        st.info("📭 No data yet. Submit support requests to see analytics!")
    else:
        # Summary metrics at top
        st.markdown("### 🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tickets = len(tickets)
            st.metric("Total Tickets", total_tickets)
        
        with col2:
            ai_resolved = len([t for t in tickets if t["status"] == "solved" and not t["ai_analysis"]["escalated"]])
            ai_resolution_rate = (ai_resolved / total_tickets * 100) if total_tickets > 0 else 0
            st.metric("AI Resolution Rate", f"{ai_resolution_rate:.1f}%")
        
        with col3:
            escalated = len([t for t in tickets if t["ai_analysis"]["escalated"]])
            st.metric("Escalated", escalated)
        
        with col4:
            if tickets:
                avg_response = sum(t.get("ai_analysis", {}).get("confidence", 0) for t in tickets) / len(tickets)
                st.metric("Avg AI Confidence", f"{avg_response:.1%}")
        
        st.markdown("---")
        
        # Row 1: AI Resolution Rate Over Time & Tickets by Priority
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 AI Resolution Rate Over Time")
            
            # Group tickets by date
            from collections import defaultdict
            tickets_by_date = defaultdict(lambda: {"total": 0, "ai_solved": 0})
            
            for ticket in tickets:
                date = ticket["created_at"][:10]  # Get just the date
                tickets_by_date[date]["total"] += 1
                if ticket["status"] == "solved" and not ticket["ai_analysis"]["escalated"]:
                    tickets_by_date[date]["ai_solved"] += 1
            
            # Calculate rates
            dates = sorted(tickets_by_date.keys())
            rates = []
            for date in dates:
                total = tickets_by_date[date]["total"]
                ai_solved = tickets_by_date[date]["ai_solved"]
                rate = (ai_solved / total * 100) if total > 0 else 0
                rates.append(rate)
            
            if len(dates) > 0:
                import pandas as pd
                chart_data = pd.DataFrame({
                    "Date": dates,
                    "AI Resolution Rate (%)": rates
                })
                st.line_chart(chart_data.set_index("Date"))
            else:
                st.info("Not enough data for trend")
        
        with col2:
            st.markdown("### 🎯 Tickets by Priority")
            
            # Count by priority
            priority_counts = {"urgent": 0, "high": 0, "medium": 0, "low": 0}
            for ticket in tickets:
                priority = ticket.get("priority", "medium")
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Filter out zeros
            priority_data = {k: v for k, v in priority_counts.items() if v > 0}
            
            if priority_data:
                import pandas as pd
                chart_data = pd.DataFrame({
                    "Priority": list(priority_data.keys()),
                    "Count": list(priority_data.values())
                })
                st.bar_chart(chart_data.set_index("Priority"))
            else:
                st.info("No priority data")
        
        st.markdown("---")
        
        # Row 2: Tickets by Device & Response Time Trend
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💻 Tickets by Device Type")
            
            # Count by device
            device_counts = {}
            for ticket in tickets:
                device = ticket.get("device_type", "Unknown")
                device_counts[device] = device_counts.get(device, 0) + 1
            
            if device_counts:
                import pandas as pd
                chart_data = pd.DataFrame({
                    "Device": list(device_counts.keys()),
                    "Count": list(device_counts.values())
                })
                st.bar_chart(chart_data.set_index("Device"))
            else:
                st.info("No device data")
        
        with col2:
            st.markdown("### ⚡ Response Times by Date")
            
            # Group by date
            from collections import defaultdict
            response_by_date = defaultdict(list)
            for ticket in tickets:
                date = ticket["created_at"][:10]
                # In real system, we'd have actual response times
                # For demo, use a simulated value based on whether escalated
                if ticket["ai_analysis"]["escalated"]:
                    response_time = 15000  # Escalated = slower (human needed)
                else:
                    response_time = 3000  # AI solved = fast
                response_by_date[date].append(response_time)
            
            # Calculate averages
            dates = sorted(response_by_date.keys())
            avg_times = []
            for date in dates:
                avg = sum(response_by_date[date]) / len(response_by_date[date])
                avg_times.append(avg)
            
            if len(dates) > 0:
                import pandas as pd
                chart_data = pd.DataFrame({
                    "Date": dates,
                    "Avg Response Time (ms)": avg_times
                })
                st.line_chart(chart_data.set_index("Date"))
            else:
                st.info("Not enough data for trend")
        
        st.markdown("---")
        
        # Row 3: Slack Notifications by Channel
        st.markdown("### 📢 Slack Notifications by Channel")
        
        if len(notifications) > 0:
            # Count by channel
            channel_counts = {}
            for notif in notifications:
                channel = notif.get("channel", "Unknown")
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
            
            import pandas as pd
            chart_data = pd.DataFrame({
                "Channel": list(channel_counts.keys()),
                "Notifications": list(channel_counts.values())
            })
            st.bar_chart(chart_data.set_index("Channel"))
        else:
            st.info("No notification data yet. Escalate tickets to see channel distribution!")
        
        st.markdown("---")
        
        # Detailed Stats Table
        st.markdown("### 📋 Detailed Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Ticket Breakdown:**")
            st.markdown(f"""
            - Total Tickets: {len(tickets)}
            - Open: {len([t for t in tickets if t['status'] == 'open'])}
            - Solved: {len([t for t in tickets if t['status'] == 'solved'])}
            - AI Resolved: {ai_resolved}
            - Escalated: {escalated}
            - Escalation Rate: {(escalated/len(tickets)*100):.1f}%
            """)
        
        with col2:
            st.markdown("**Performance Metrics:**")
            
            # Calculate avg confidence
            confidences = [t["ai_analysis"].get("confidence", 0) for t in tickets if t["ai_analysis"].get("confidence")]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            
            st.markdown(f"""
            - Avg AI Confidence: {avg_conf:.1%}
            - Total Notifications: {len(notifications)}
            - Unread Notifications: {len(slack_sim.get_unread_notifications())}
            - Unique Channels Used: {len(set(n['channel'] for n in notifications)) if notifications else 0}
            """)

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 System Status")
    st.markdown(f"""
    - **Customers:** {len(CUSTOMERS)}
    - **Tickets:** {len(ticket_system.get_all_tickets())}
    - **Notifications:** {len(slack_sim.get_all_notifications())}
    - **At Risk:** {len([c for c in CUSTOMERS if c["churn_risk"] in ["HIGH", "CRITICAL"]])}
    """)