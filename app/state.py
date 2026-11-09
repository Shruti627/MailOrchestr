
from typing import TypedDict


class EmailAgentState(TypedDict, total=False):

    # Workflow mode
    mode: str

    # Incoming instruction or customer email
    email_content: str
    email_id: str

    # Separate recipient and customer identity
    recipient_email: str
    customer_email: str

    # AI classification
    classification: dict

    # Support workflow information
    ticket_id: str
    search_results: list[str]
    customer_history: dict

    # Generated email
    subject: str
    draft_response: str

    # Human approval
    review_status: str

    # Sending result
    send_status: str
