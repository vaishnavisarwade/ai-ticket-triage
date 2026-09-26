from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_graph import app as agent_app
from database import init_db, save_ticket, get_all_tickets, delete_ticket, get_ticket_by_id

api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class TicketRequest(BaseModel):
    ticket_text: str


@api.post("/process-ticket")
def process_ticket(request: TicketRequest):
    result = agent_app.invoke({
        "ticket_text": request.ticket_text,
        "classification": "",
        "similar_tickets": [],
        "draft_response": "",
        "escalation_status": ""
    })
    save_ticket(result)
    return result


@api.get("/tickets")
def list_tickets():
    return get_all_tickets()


@api.get("/tickets/{ticket_id}")
def get_one_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return {"error": f"No ticket found with ID {ticket_id}"}
    return ticket


@api.delete("/tickets/{ticket_id}")
def remove_ticket(ticket_id: int):
    delete_ticket(ticket_id)
    return {"deleted": ticket_id}