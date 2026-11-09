# MailOrchestr

### Agentic AI-Powered Email Orchestration System

MailOrchestr is an intelligent email automation system built with **LangGraph** that handles personal email composition and customer support response generation through multi-step AI workflows.

It combines LLM-powered email generation, intent classification, parallel task execution, contextual retrieval, and Human-in-the-Loop approval to deliver ready-to-send emails through the Brevo API.

## ✨ Features

- 🤖 **Agentic AI Workflows** – Multi-step, stateful email processing.
- ✍️ **Personal Email Composition** – Generate professional emails from natural-language instructions.
- 📩 **Customer Support Automation** – Classify incoming emails and generate contextual replies.
- ⚡ **Parallel Execution** – Run independent support tasks concurrently.
- 🔀 **Conditional Routing** – Route workflows based on intent and email type.
- 🔍 **Knowledge Retrieval** – Retrieve relevant information from a local support knowledge base.
- 👤 **Human-in-the-Loop** – Review, edit, approve, or reject every generated email.
- 📬 **Email Delivery** – Send approved emails using Brevo API.
- 💾 **State Persistence** – SQLite-backed workflow checkpointing.

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python | Core development |
| LangGraph | Agent orchestration and workflow management |
| LangChain | LLM integration and prompt management |
| Groq | LLM inference |
| GPT-OSS-120B | Email generation and classification |
| Pydantic | Structured data validation |
| SQLite | Workflow checkpoint persistence |
| Brevo API | Transactional email delivery |
| Requests | API communication |
| python-dotenv | Environment configuration |

## ⚙️ Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/Shruti627/MailOrchestr.git
cd MailOrchestr
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
copy .env.example .env
```

Add your Groq and Brevo API credentials to `.env`.

**5. Run the application**

```bash
python main.py
```

## 💻 How to Use

Choose one of the two workflows from the interactive terminal:

| Workflow | Steps |
|---|---|
| Personal Email | Enter instructions → Provide recipient email → Generate draft → Review → Approve and send |
| Customer Support | Paste customer email → Classify and process → Generate reply → Review → Approve and send |

**Human approval is mandatory for every outgoing email.**

## 📌 Current Scope

- Customer emails are manually provided through the terminal.
- Support ticket creation and customer history currently use demonstration implementations.
- Documentation retrieval uses a local JSON knowledge base.
- Email delivery is handled through Brevo.

## 👩‍💻 Author

**Shruti P. Sangvikar**

- GitHub: [Shruti627](https://github.com/Shruti627)
- LinkedIn: [Shruti Sangvikar](https://www.linkedin.com/in/shruti-sangvikar/)

---

<p align="center">
  <b>MailOrchestr</b><br>
  Intelligent Workflows. Human-Controlled Communication.
</p>