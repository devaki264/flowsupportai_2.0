# test_customers.py

from src.data.synthetic_customers import CUSTOMERS

print("\n👥 CUSTOMER DATABASE:\n")

for customer in CUSTOMERS:
    risk_icon = {
        "CRITICAL": "🔴",
        "HIGH": "🟠", 
        "MEDIUM": "🟡",
        "LOW": "🟢"
    }[customer["churn_risk"]]
    
    print(f"{risk_icon} {customer['name']} - Health: {customer['health_score']}/100")
    print(f"   Contact: {customer['contact_name']} ({customer['contact_email']})")
    print(f"   Contract: ${customer['contract_value']:,}")
    print(f"   Usage Trend: {customer['usage']['trend']}")
    print(f"   Open Tickets: {customer['support']['open_tickets']}")
    print(f"   Renewal: {customer['renewal_date']}")
    print()