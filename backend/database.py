import sqlite3
import json
from datetime import datetime

DB_PATH = "tickets.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_text TEXT,
            classification TEXT,
            similar_tickets TEXT,
            draft_response TEXT,
            escalation_status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_ticket(result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO processed_tickets 
        (ticket_text, classification, similar_tickets, draft_response, escalation_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        result["ticket_text"],
        result["classification"],
        json.dumps(result["similar_tickets"]),
        result["draft_response"],
        result["escalation_status"],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM processed_tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()


def get_all_tickets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM processed_tickets ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    tickets = []
    for row in rows:
        tickets.append({
            "id": row["id"],
            "ticket_text": row["ticket_text"],
            "classification": row["classification"],
            "similar_tickets": json.loads(row["similar_tickets"]),
            "draft_response": row["draft_response"],
            "escalation_status": row["escalation_status"],
            "created_at": row["created_at"]
        })
    return tickets


def get_ticket_by_id(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM processed_tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "ticket_text": row["ticket_text"],
        "classification": row["classification"],
        "similar_tickets": json.loads(row["similar_tickets"]),
        "draft_response": row["draft_response"],
        "escalation_status": row["escalation_status"],
        "created_at": row["created_at"]
    }