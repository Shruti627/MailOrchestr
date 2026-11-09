
import os
import json
import re

from dotenv import load_dotenv
from typing import Literal

from pydantic import BaseModel, Field

from langchain_groq import ChatGroq

from langgraph.types import Command, interrupt
from langgraph.graph import END

from app.state import EmailAgentState

from app.prompts import (
    CLASSIFICATION_PROMPT,
    PERSONAL_EMAIL_PROMPT,
    SUPPORT_RESPONSE_PROMPT
)

from app.tools import (
    search_documentation,
    create_support_ticket,
    get_customer_history,
    send_email
)


# ------------------------------------------
# ENVIRONMENT
# ------------------------------------------

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY missing in .env")


# ------------------------------------------
# CLASSIFICATION SCHEMA
# ------------------------------------------

class EmailClassification(BaseModel):

    intent: Literal[
        "question",
        "bug",
        "billing",
        "feature",
        "complex"
    ]

    urgency: Literal[
        "low",
        "medium",
        "high",
        "critical"
    ]

    topic: str

    summary: str

    subject: str


# ------------------------------------------
# MODEL
# ------------------------------------------

model = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    ),
    temperature=0,
    max_retries=2
)


# ------------------------------------------
# HELPER: EXTRACT RESPONSE TEXT
# ------------------------------------------

def extract_response_text(content):

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):

                if block.get("type") == "text":
                    parts.append(
                        block.get("text", "")
                    )

        return "\n".join(parts).strip()

    return str(content).strip()


# ------------------------------------------
# HELPER: PARSE CLASSIFICATION
# ------------------------------------------

def parse_classification(response_text, state):

    data = {}

    # Try extracting JSON first
    try:

        start = response_text.find("{")
        end = response_text.rfind("}") + 1

        if start != -1 and end > start:

            data = json.loads(
                response_text[start:end]
            )

    except (json.JSONDecodeError, TypeError):
        data = {}

    # Fallback for models returning labelled text
    if not data:

        for field in [
            "intent",
            "urgency",
            "topic",
            "summary",
            "subject"
        ]:

            match = re.search(
                rf"(?im)^\s*{field}\s*:\s*(.+?)\s*$",
                response_text
            )

            if match:
                data[field] = match.group(1).strip()

    # Safe defaults
    allowed_intents = {
        "question",
        "bug",
        "billing",
        "feature",
        "complex"
    }

    allowed_urgencies = {
        "low",
        "medium",
        "high",
        "critical"
    }

    intent = str(
        data.get("intent", "question")
    ).lower()

    urgency = str(
        data.get("urgency", "medium")
    ).lower()

    if intent not in allowed_intents:
        intent = "question"

    if urgency not in allowed_urgencies:
        urgency = "medium"

    topic = str(
        data.get("topic")
        or "Email request"
    )

    summary = str(
        data.get("summary")
        or state["email_content"]
    )

    subject = str(
        data.get("subject")
        or topic
    )

    return EmailClassification(
        intent=intent,
        urgency=urgency,
        topic=topic,
        summary=summary,
        subject=subject
    )


# ------------------------------------------
# NODE 1: READ EMAIL / INSTRUCTION
# ------------------------------------------

def read_email(state: EmailAgentState):

    print("\n[NODE] Reading email instruction...")

    return {
        "email_content": state["email_content"].strip()
    }


# ------------------------------------------
# NODE 2: CLASSIFY
# ------------------------------------------

def classify_intent(state: EmailAgentState):

    print("\n[NODE] Understanding email request...")

    prompt = f"""
    {CLASSIFICATION_PROMPT}

    MODE:
    {state['mode']}

    EMAIL OR INSTRUCTION:
    {state['email_content']}
    """

    # Normal model invocation, NOT structured tool calling
    response = model.invoke(prompt)

    response_text = extract_response_text(
        response.content
    )

    classification = parse_classification(
        response_text,
        state
    )

    print("Intent:", classification.intent)
    print("Urgency:", classification.urgency)
    print("Topic:", classification.topic)
    print("Subject:", classification.subject)

    return {
        "classification": classification.model_dump(),
        "subject": classification.subject
    }


# ------------------------------------------
# NODE 3: PERSONAL EMAIL CONTEXT
# ------------------------------------------

def personal_context(state: EmailAgentState):

    print("\n[NODE] Preparing personal email...")

    return {
        "search_results": [],
        "customer_history": {},
        "ticket_id": ""
    }


# ------------------------------------------
# NODE 4: SUPPORT START
# ------------------------------------------

def support_start(state: EmailAgentState):

    print("\n[NODE] Starting customer support workflow...")

    return {}


# ------------------------------------------
# NODE 5: SEARCH DOCUMENTATION
# ------------------------------------------

def search_documentation_node(state: EmailAgentState):

    print("\n[NODE] Searching support documentation...")

    classification = state["classification"]

    query = (
        f"{classification['intent']} "
        f"{classification['topic']} "
        f"{classification['summary']}"
    )

    results = search_documentation(query)

    print(f"Retrieved {len(results)} documents.")

    return {
        "search_results": results
    }


# ------------------------------------------
# NODE 6: BUG TRACKING
# ------------------------------------------

def bug_tracking(state: EmailAgentState):

    print("\n[NODE] Processing support ticket...")

    classification = state["classification"]

    ticket_id = None

    if classification["intent"] in [
        "bug",
        "billing",
        "complex"
    ]:

        ticket_id = create_support_ticket(
            email_id=state["email_id"],
            topic=classification["topic"]
        )

    return {
        "ticket_id": ticket_id or ""
    }


# ------------------------------------------
# NODE 7: CUSTOMER HISTORY
# ------------------------------------------

def fetch_customer_history(state: EmailAgentState):

    print("\n[NODE] Fetching customer history...")

    history = get_customer_history(
        state["customer_email"]
    )

    return {
        "customer_history": history
    }


# ------------------------------------------
# NODE 8: GENERATE EMAIL
# ------------------------------------------

def write_response(
    state: EmailAgentState
) -> Command[Literal["human_review"]]:

    print("\n[NODE] Generating complete email...")

    classification = state["classification"]

    mode = state["mode"]

    sender_name = os.getenv(
        "EMAIL_SIGNATURE_NAME",
        "Shruti"
    )

    if mode == "personal":

        prompt = PERSONAL_EMAIL_PROMPT.format(

            email_content=state["email_content"],

            recipient_email=state["recipient_email"],

            sender_name=sender_name,

            subject=state["subject"]
        )

    else:

        documentation = "\n".join(
            state.get("search_results") or []
        )

        customer_history = str(
            state.get("customer_history") or {}
        )

        prompt = SUPPORT_RESPONSE_PROMPT.format(

            email_content=state["email_content"],

            customer_email=state["customer_email"],

            classification=classification,

            documentation=documentation,

            customer_history=customer_history,

            ticket_id=state.get("ticket_id") or "Not applicable"
        )

    response = model.invoke(prompt)

    draft = extract_response_text(
        response.content
    )

    if not draft:
        raise ValueError(
            "AI generated an empty email draft."
        )

    print("\nDraft generated successfully.")

    # No automatic sending in either mode.
    print("\n[ROUTER] Human approval required.")

    return Command(

        update={
            "draft_response": draft,
            "review_status": "pending"
        },

        goto="human_review"
    )


# ------------------------------------------
# NODE 9: HUMAN REVIEW
# ------------------------------------------

def human_review(
    state: EmailAgentState
) -> Command[Literal["send_reply", "__end__"]] :

    print("\n[NODE] Waiting for human approval...")

    decision = interrupt({

        "mode": state["mode"],

        "recipient": state["recipient_email"],

        "subject": state["subject"],

        "draft_response": state["draft_response"],

        "action": "Approve, edit or reject"
    })

    action = decision.get("action")

    if action == "approve":

        print("\n[HUMAN] Email approved.")

        edited_response = decision.get(
            "edited_response"
        )

        final_draft = (
            edited_response
            if edited_response
            else state["draft_response"]
        )

        return Command(

            update={
                "draft_response": final_draft,
                "review_status": "approved"
            },

            goto="send_reply"
        )

    elif action == "reject":

        print("\n[HUMAN] Email rejected.")

        return Command(

            update={
                "review_status": "rejected",
                "send_status": "not_sent"
            },

            goto=END
        )

    else:

        print("\n[HUMAN] Invalid decision.")

        return Command(

            update={
                "review_status": "invalid_decision",
                "send_status": "not_sent"
            },

            goto=END
        )


# ------------------------------------------
# NODE 10: SEND EMAIL
# ------------------------------------------

def send_reply(state: EmailAgentState):

    print("\n[NODE] Sending email through Brevo...")

    # Final safety check
    if state.get("review_status") != "approved":

        print("\n[SAFETY] Email not approved.")

        return {
            "send_status": "not_sent"
        }

    success = send_email(

        recipient=state["recipient_email"],

        subject=state["subject"],

        body=state["draft_response"],

        approved=True
    )

    return {
        "send_status": (
            "sent" if success else "failed"
        )
    }
