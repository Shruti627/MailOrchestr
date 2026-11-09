
import json
import uuid
import re
import os
import requests

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_PATH = (
    BASE_DIR / "data" / "knowledge_base.json"
)


# ------------------------------------------
# TOOL 1: SEARCH DOCUMENTATION
# ------------------------------------------

def search_documentation(query: str) -> list[str]:

    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        documents = json.load(file)

    query_words = set(
        re.findall(r"\w+", query.lower())
    )

    scored_documents = []

    for document in documents:

        searchable_text = (
            document["topic"] + " " +
            document["content"]
        ).lower()

        document_words = set(
            re.findall(r"\w+", searchable_text)
        )

        score = len(
            query_words & document_words
        )

        if score > 0:

            scored_documents.append(
                (score, document["content"])
            )

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        content
        for score, content in scored_documents[:3]
    ]


# ------------------------------------------
# TOOL 2: CREATE SUPPORT TICKET
# ------------------------------------------

def create_support_ticket(
    email_id: str,
    topic: str
) -> str:

    ticket_id = (
        f"TICKET-{str(uuid.uuid4())[:8].upper()}"
    )

    print(
        f"\n[TOOL] Support ticket created: {ticket_id}"
    )

    return ticket_id


# ------------------------------------------
# TOOL 3: CUSTOMER HISTORY
# ------------------------------------------

def get_customer_history(
    customer_email: str
) -> dict:

    # Demo data. Replace with a real customer database
    # when you connect your CRM.

    return {
        "email": customer_email,
        "tier": "standard",
        "previous_tickets": 2,
        "customer_status": "active"
    }


# ------------------------------------------
# TOOL 4: SEND REAL EMAIL USING BREVO
# ------------------------------------------

def send_email(
    recipient: str,
    subject: str,
    body: str,
    approved: bool = False
) -> bool:

    """
    Send an actual transactional email through Brevo.

    Sending is blocked unless human approval is explicit.
    """

    # Additional safety layer
    if approved is not True:

        print(
            "\n[SAFETY] Email was not approved. "
            "Sending cancelled."
        )

        return False

    api_key = os.getenv("BREVO_API_KEY")

    sender_email = os.getenv("BREVO_SENDER_EMAIL")

    sender_name = os.getenv(
        "BREVO_SENDER_NAME",
        "Smart AI Email Agent"
    )

    if not api_key:
        raise ValueError(
            "BREVO_API_KEY is missing in .env"
        )

    if not sender_email:
        raise ValueError(
            "BREVO_SENDER_EMAIL is missing in .env"
        )

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": recipient
            }
        ],
        "subject": subject,
        "textContent": body
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        print("\n" + "=" * 60)
        print("EMAIL ACCEPTED BY BREVO")
        print("=" * 60)

        print("From:", sender_name, sender_email)
        print("To:", recipient)
        print("Subject:", subject)
        print("Message ID:", result.get("messageId"))

        print("=" * 60)

        return True

    except requests.RequestException as error:

        print("\n[BREVO] EMAIL REQUEST FAILED")
        print("Error:", error)

        if error.response is not None:
            print(
                "Brevo response:",
                error.response.text
            )

        return False
