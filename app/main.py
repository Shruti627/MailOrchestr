
import os
import re
import uuid

from dotenv import load_dotenv

from langgraph.types import Command

from app.graph import build_graph
from app.database import get_checkpointer


load_dotenv()


# ------------------------------------------
# HELPERS
# ------------------------------------------

def print_banner():

    print("\n" + "=" * 65)
    print("             SMART AI EMAIL AGENT")
    print("=" * 65)


def validate_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(pattern, email.strip())
    )


def display_preview(email_data):

    sender_name = os.getenv(
        "BREVO_SENDER_NAME",
        "Smart AI Email Agent"
    )

    sender_email = os.getenv(
        "BREVO_SENDER_EMAIL",
        "Not configured"
    )

    print("\n" + "=" * 65)
    print("                  EMAIL PREVIEW")
    print("=" * 65)

    print(f"\nFrom: {sender_name} <{sender_email}>")

    print(
        f"To: {email_data['recipient']}"
    )

    print(
        f"Subject: {email_data['subject']}"
    )

    print("\n" + "-" * 65)

    print(email_data["draft_response"])

    print("\n" + "=" * 65)


# ------------------------------------------
# HUMAN REVIEW
# ------------------------------------------

def review_email(app, config, result):

    while True:

        interrupt_data = result["__interrupt__"][0].value

        display_preview(interrupt_data)

        print("\nChoose an action:")

        print("1. Approve and Send")
        print("2. Edit Email")
        print("3. Reject Email")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            decision = {
                "action": "approve"
            }

        elif choice == "2":

            print("\nEnter your edited email.")
            print("Type END on a new line when finished.\n")

            lines = []

            while True:

                line = input()

                if line.strip() == "END":
                    break

                lines.append(line)

            edited_response = "\n".join(lines).strip()

            if not edited_response:

                print("\nEmpty email. Returning to review.")

                continue

            print("\nEdited email preview:")
            print("-" * 65)
            print(edited_response)
            print("-" * 65)

            confirmation = input(
                "\nSend this edited email? (yes/no): "
            ).strip().lower()

            if confirmation != "yes":

                print("\nReturning to review menu.")

                continue

            decision = {
                "action": "approve",
                "edited_response": edited_response
            }

        elif choice == "3":

            decision = {
                "action": "reject"
            }

        else:

            print("\nInvalid choice. Try again.")

            continue

        # Resume interrupted LangGraph workflow
        result = app.invoke(
            Command(resume=decision),
            config=config
        )

        return result


# ------------------------------------------
# SHOW FINAL STATUS
# ------------------------------------------

def show_result(result):

    print("\n" + "=" * 65)
    print("                 WORKFLOW RESULT")
    print("=" * 65)

    print(
        "Review status:",
        result.get("review_status")
    )

    print(
        "Send status:",
        result.get("send_status")
    )

    if result.get("send_status") == "sent":

        print("\nEmail request accepted by Brevo.")

    elif result.get("send_status") == "failed":

        print("\nBrevo could not accept the email request.")

    elif result.get("send_status") == "not_sent":

        print("\nEmail was not sent.")

    print("=" * 65)


# ------------------------------------------
# COLLECT USER INPUT
# ------------------------------------------

def collect_input():

    print_banner()

    print("\nWhat would you like to do?")

    print("\n1. Write a new email")
    print("2. Process a customer support email")

    mode_choice = input(
        "\nChoose mode: "
    ).strip()

    if mode_choice == "1":

        mode = "personal"

        print("\n--- PERSONAL EMAIL MODE ---")

        email_content = input(
            "\nDescribe the email you want to write: "
        ).strip()

        recipient_email = input(
            "\nEnter recipient's actual email address: "
        ).strip()

        if not validate_email(recipient_email):

            raise ValueError(
                "Invalid recipient email address."
            )

        customer_email = ""

    elif mode_choice == "2":

        mode = "support"

        print("\n--- CUSTOMER SUPPORT MODE ---")

        email_content = input(
            "\nPaste the incoming customer email: "
        ).strip()

        customer_email = input(
            "\nEnter customer's email address: "
        ).strip()

        if not validate_email(customer_email):

            raise ValueError(
                "Invalid customer email address."
            )

        # A support reply goes back to the customer.
        recipient_email = customer_email

    else:

        raise ValueError(
            "Invalid mode. Choose 1 or 2."
        )

    if not email_content:

        raise ValueError(
            "Email content cannot be empty."
        )

    return {
        "mode": mode,
        "email_content": email_content,
        "recipient_email": recipient_email,
        "customer_email": customer_email,
        "email_id": str(uuid.uuid4()),
        "review_status": "pending",
        "send_status": "not_sent"
    }


# ------------------------------------------
# MAIN WORKFLOW
# ------------------------------------------

def main():

    try:

        initial_state = collect_input()

        print_banner()

        print("\nStarting LangGraph workflow...")

        thread_id = str(uuid.uuid4())

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        with get_checkpointer() as checkpointer:

            app = build_graph(checkpointer)

            result = app.invoke(
                initial_state,
                config=config
            )

            # Human approval interrupt
            if result.get("__interrupt__"):

                result = review_email(
                    app,
                    config,
                    result
                )

            show_result(result)

    except KeyboardInterrupt:

        print("\nOperation cancelled.")

    except Exception as error:

        print("\n[ERROR]", error)

        print(
            "\nPlease check your configuration "
            "and try again."
        )


if __name__ == "__main__":

    main()
