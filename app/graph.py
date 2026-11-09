
from langgraph.graph import StateGraph, START, END

from app.state import EmailAgentState

from app.nodes import (
    read_email,
    classify_intent,
    personal_context,
    support_start,
    search_documentation_node,
    bug_tracking,
    fetch_customer_history,
    write_response,
    human_review,
    send_reply
)


# ------------------------------------------
# ROUTING FUNCTIONS
# ------------------------------------------

def route_after_classification(state):

    if state["mode"] == "personal":
        return "personal"

    return "support"


def fan_out_support(state):

    # Execute these three nodes in parallel.
    return [
        "search_documentation",
        "bug_tracking",
        "fetch_customer_history"
    ]


# ------------------------------------------
# BUILD GRAPH
# ------------------------------------------

def build_graph(checkpointer=None):

    builder = StateGraph(EmailAgentState)

    # Register nodes
    builder.add_node("read_email", read_email)

    builder.add_node(
        "classify_intent",
        classify_intent
    )

    builder.add_node(
        "personal_context",
        personal_context
    )

    builder.add_node(
        "support_start",
        support_start
    )

    builder.add_node(
        "search_documentation",
        search_documentation_node
    )

    builder.add_node(
        "bug_tracking",
        bug_tracking
    )

    builder.add_node(
        "fetch_customer_history",
        fetch_customer_history
    )

    builder.add_node(
        "write_response",
        write_response
    )

    builder.add_node(
        "human_review",
        human_review
    )

    builder.add_node(
        "send_reply",
        send_reply
    )

    # --------------------------------------
    # COMMON FLOW
    # --------------------------------------

    builder.add_edge(START, "read_email")

    builder.add_edge(
        "read_email",
        "classify_intent"
    )

    # --------------------------------------
    # PERSONAL OR SUPPORT ROUTING
    # --------------------------------------

    builder.add_conditional_edges(

        "classify_intent",

        route_after_classification,

        {
            "personal": "personal_context",
            "support": "support_start"
        }
    )

    # Personal path
    builder.add_edge(
        "personal_context",
        "write_response"
    )

    # --------------------------------------
    # SUPPORT PARALLEL EXECUTION
    # --------------------------------------

    builder.add_conditional_edges(

        "support_start",

        fan_out_support,

        [
            "search_documentation",
            "bug_tracking",
            "fetch_customer_history"
        ]
    )

    # Wait for all three support branches
    builder.add_edge(

        [
            "search_documentation",
            "bug_tracking",
            "fetch_customer_history"
        ],

        "write_response"
    )

    # --------------------------------------
    # HUMAN APPROVAL AND SENDING
    # --------------------------------------

    # write_response routes using Command
    # human_review routes using Command

    builder.add_edge(
        "send_reply",
        END
    )

    return builder.compile(
        checkpointer=checkpointer
    )
