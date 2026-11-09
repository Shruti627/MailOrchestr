# Smart AI Email Agent

An intelligent customer support email agent
built using LangGraph, LangChain and Groq.

## Features

- Email classification
- Urgency detection
- Structured LLM output
- Parallel execution
- Documentation retrieval
- Support ticket creation
- Customer history retrieval
- AI response generation
- Conditional routing
- Human-in-the-loop approval
- SQLite checkpoint persistence
- Thread-based execution
- Batch email processing

## Tech Stack

- Python
- LangGraph
- LangChain
- Groq
- Pydantic
- SQLite

## Setup

Create virtual environment:

python -m venv venv

Activate:

.\venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Configure .env with your Groq API key.

## Process an Email

python -m app.main run --email "I was charged twice!"

## Approve an Email

python -m app.main resume --thread-id YOUR_THREAD_ID --action approve

## Reject an Email

python -m app.main resume --thread-id YOUR_THREAD_ID --action reject

## Edit an Email

python -m app.main resume --thread-id YOUR_THREAD_ID --action edit --edited-response "Your revised response"

## Batch Processing

python -m app.main batch