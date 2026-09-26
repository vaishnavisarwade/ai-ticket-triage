import pandas as pd
import json
from agent_graph import classify_node

# Load the dataset
df = pd.read_csv("../data/tickets.csv")

# Take a random sample (to keep it fast — classifying all 8,469 would take a while and cost API calls)
sample = df.sample(n=50, random_state=42)

correct = 0
total = 0
results = []

print(f"Evaluating classifier on {len(sample)} tickets...\n")

for _, row in sample.iterrows():
    ticket_text = row["Ticket Description"]
    true_category = row["Ticket Type"]

    # Run our classify_node — reuse the same function from the graph
    state = {"ticket_text": ticket_text, "classification": "", "similar_tickets": [], "draft_response": "", "escalation_status": ""}
    state = classify_node(state)

    try:
        predicted = json.loads(state["classification"])
        predicted_category = predicted.get("category", "")
    except:
        predicted_category = "PARSE_ERROR"

    is_correct = predicted_category.strip().lower() == true_category.strip().lower()
    if is_correct:
        correct += 1
    total += 1

    results.append({
        "true": true_category,
        "predicted": predicted_category,
        "correct": is_correct
    })

    print(f"[{total}/{len(sample)}] True: {true_category:25} | Predicted: {predicted_category:25} | {'✓' if is_correct else '✗'}")
    if not is_correct and total <= 5:
        print(f"    TICKET TEXT: {ticket_text[:300]}")
        print()

accuracy = (correct / total) * 100
print(f"\n{'='*50}")
print(f"ACCURACY: {correct}/{total} = {accuracy:.1f}%")
print(f"{'='*50}")