import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv(override=True)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load the embedding model and vector DB (same as Day 2)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="tickets")


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


def retrieve_similar_tickets(ticket_text, n=3):
    query_embedding = embed_model.encode([ticket_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n
    )
    similar = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        similar.append({
            "description": doc,
            "category": meta["category"],
            "priority": meta["priority"],
            "resolution": meta["resolution"]
        })
    return similar


def process_ticket(ticket_text):
    classification = classify_ticket(ticket_text)
    similar_tickets = retrieve_similar_tickets(ticket_text)

    print("=" * 50)
    print("NEW TICKET:", ticket_text)
    print("\nCLASSIFICATION:", classification)
    print(f"\nTOP {len(similar_tickets)} SIMILAR PAST TICKETS:")
    for i, t in enumerate(similar_tickets, 1):
        print(f"\n  [{i}] Category: {t['category']} | Priority: {t['priority']}")
        print(f"      Description: {t['description'][:120]}...")
        print(f"      Resolution: {t['resolution']}")
    print("=" * 50)


# Test it
new_ticket = "I can't log into my account, it keeps saying invalid password even though I'm sure it's correct"
process_ticket(new_ticket)