# test_tickets.py

from src.integrations.local_ticketing import LocalTicketSystem

ticket_system = LocalTicketSystem()

print("\n📋 ALL TICKETS:\n")

tickets = ticket_system.get_all_tickets()

if not tickets:
    print("No tickets yet. Submit some support requests!")
else:
    for ticket in tickets:
        print(f"🎫 {ticket['id']} - {ticket['status'].upper()}")
        print(f"   Subject: {ticket['subject']}")
        print(f"   Customer: {ticket['requester']['name']}")
        print(f"   Device: {ticket['device_type']}")
        print(f"   AI Confidence: {ticket['ai_analysis'].get('confidence', 0):.1%}")
        print(f"   Escalated: {ticket['ai_analysis']['escalated']}")
        print(f"   Team: {ticket['ai_analysis'].get('team', 'N/A')}")
        print()

print(f"Total Tickets: {len(tickets)}")