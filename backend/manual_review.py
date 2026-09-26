import pandas as pd
from agent_graph import classify_node

df = pd.read_csv("../data/tickets.csv")
sample = df.sample(n=10, random_state=7)

print("Reading 10 tickets and their AI classification.\n")
print("For each one, judge for yourself: does the PREDICTED category make sense given the TICKET TEXT?\n")
print("=" * 70)

for i, (_, row) in enumerate(sample.iterrows(), 1):
    ticket_text = row["Ticket Description"]

    state = {"ticket_text": ticket_text, "classification": "", "similar_tickets": [], "draft_response": "", "escalation_status": ""}
    state = classify_node(state)

    print(f"\n[{i}] TICKET TEXT:\n{ticket_text}")
    print(f"\n    ORIGINAL DATASET LABEL: {row['Ticket Type']}")
    print(f"    AI PREDICTED:           {state['classification']}")
    print("-" * 70)