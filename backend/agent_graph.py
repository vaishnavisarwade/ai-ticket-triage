import os
import json
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer
from typing import TypedDict
from langgraph.graph import StateGraph, END

load_dotenv(override=True)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="tickets")


class TicketState(TypedDict):
    ticket_text: str
    classification: str
    similar_tickets: list
    draft_response: str
    escalation_status: str


def classify_node(state: TicketState) -> TicketState:
    prompt = f"""You are a support ticket classifier. Read the ticket below and respond with ONLY a JSON object, nothing else.

Ticket: "{state['ticket_text']}"

Respond in this exact format:
{{"category": "one of: Technical issue, Billing inquiry, Cancellation request, Refund request, Product inquiry", "urgency": "one of: Low, Medium, High, Critical", "confidence": a number from 0 to 100 representing how confident you are in this classification}}
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    state["classification"] = response.choices[0].message.content
    return state


def retrieve_node(state: TicketState) -> TicketState:
    query_embedding = embed_model.encode([state["ticket_text"]]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=3)

    similar = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        similar.append({
            "description": doc,
            "category": meta["category"],
            "priority": meta["priority"],
            "resolution": meta["resolution"]
        })
    state["similar_tickets"] = similar
    return state


def draft_node(state: TicketState) -> TicketState:
    similar_context = "\n".join([
        f"- Similar past issue: {t['description'][:150]}"
        for t in state["similar_tickets"]
    ])

    prompt = f"""You are a helpful customer support agent. Write a short, professional draft response to this ticket.

Ticket: "{state['ticket_text']}"

Classification: {state['classification']}

Here are similar past tickets for context (may be low quality, use only if helpful):
{similar_context}

Write a brief, empathetic response (3-4 sentences max). Do not make promises about refunds/timelines you can't guarantee.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    state["draft_response"] = response.choices[0].message.content
    return state


def decide_escalation(state: TicketState) -> TicketState:
    try:
        parsed = json.loads(state["classification"])
        urgency = parsed.get("urgency", "Medium")
        confidence = parsed.get("confidence", 100)
    except:
        urgency = "Medium"
        confidence = 100

    reasons = []
    if urgency in ["Critical", "High"]:
        reasons.append(f"urgency is {urgency}")
    if confidence < 70:
        reasons.append(f"classification confidence is low ({confidence}%)")

    if reasons:
        state["escalation_status"] = f"ESCALATED - needs human review ({', '.join(reasons)})"
    else:
        state["escalation_status"] = "AUTO-APPROVED - safe to send"

    return state


graph = StateGraph(TicketState)

graph.add_node("classify", classify_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("draft", draft_node)
graph.add_node("decide", decide_escalation)

graph.set_entry_point("classify")
graph.add_edge("classify", "retrieve")
graph.add_edge("retrieve", "draft")
graph.add_edge("draft", "decide")
graph.add_edge("decide", END)

app = graph.compile()


if __name__ == "__main__":
    new_ticket = "Does your product support integration with Google Calendar?"

    result = app.invoke({
        "ticket_text": new_ticket,
        "classification": "",
        "similar_tickets": [],
        "draft_response": "",
        "escalation_status": ""
    })

    print("=" * 50)
    print("TICKET:", result["ticket_text"])
    print("\nCLASSIFICATION:", result["classification"])
    print("\nDRAFT RESPONSE:\n", result["draft_response"])
    print("\nESCALATION STATUS:", result["escalation_status"])
    print("=" * 50)