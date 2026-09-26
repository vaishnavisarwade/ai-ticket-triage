import os
from dotenv import load_dotenv
from groq import Groq

# Load the API key from .env
load_dotenv(override=True)

# DEBUG LINE — temporary
print("KEY LOADED:", repr(os.environ.get("GROQ_API_KEY")))

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def classify_ticket(ticket_text):
    prompt = f"""You are a support ticket classifier. Read the ticket below and respond with ONLY a JSON object, nothing else.

Ticket: "{ticket_text}"

Respond in this exact format:
{{"category": "one of: Technical issue, Billing inquiry, Cancellation request, Refund request, Product inquiry", "urgency": "one of: Low, Medium, High, Critical"}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


# Test it
# Test with a few different tickets
test_tickets = [
    "My app keeps crashing every time I try to open it, this is really urgent, I use it for work!",
    "I was charged twice for my subscription this month, can you refund the extra charge?",
    "I'd like to cancel my subscription, I no longer need the service.",
    "Does your product support integration with Google Calendar?"
]

for t in test_tickets:
    result = classify_ticket(t)
    print("\nTicket:", t)
    print("Classification:", result)