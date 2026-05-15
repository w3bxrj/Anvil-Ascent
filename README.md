# 🤖 Autonomous Issue Resolver

> AI-powered GitHub issue investigation agent that automatically researches bugs, understands repositories using RAG, and posts intelligent fix suggestions back to GitHub issues.

---

# 🚀 Features

- ✅ GitHub Webhook Integration
- ✅ Automatic Issue Classification
- ✅ RAG-based Repository Understanding
- ✅ Semantic Code Search with ChromaDB
- ✅ AI-generated Fix Suggestions
- ✅ Automatic GitHub Comment Posting
- ✅ FastAPI Backend
- ✅ Groq / OpenAI Compatible

---

# 🎯 What It Does

Whenever someone opens a GitHub issue, the system automatically:

1. Receives the issue through a GitHub webhook
2. Classifies the issue type
3. Indexes and researches the repository using embeddings + vector search
4. Retrieves relevant code context using RAG
5. Generates an AI-powered solution
6. Posts the response directly back to the GitHub issue

All of this happens automatically in under 30 seconds.

---

# 🏗️ Architecture

```text
GitHub Issue Opened
        │
        ▼
┌────────────────────┐
│ Webhook Handler    │
│ + Issue Classifier │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Research Agent     │
│ (RAG + ChromaDB)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Solution Agent     │
│ (LLM Generation)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ GitHub Commenter   │
└────────────────────┘
```

---

# 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Uvicorn |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers |
| LLM | Groq / OpenAI |
| Git Integration | GitPython |
| HTTP Client | HTTPX |
| Validation | Pydantic |

---

# 📂 Project Structure

```text
autonomous-issue-resolver/
├── .env                          # API keys (secret)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
│
├── src/                          # MAIN CODE
│   ├── __init__.py               # Package marker
│   ├── main.py                   # 🚀 ENTRY POINT - FastAPI server
│   ├── models.py                 # 📦 Data structures (Pydantic)
│   ├── classifier.py             # 🏷️ Issue type detector
│   ├── config.py                 # ⚙️ Settings loader
│   │
│   └── agents/                   # 🤖 AI AGENTS
│       ├── __init__.py           # Package marker
│       ├── repo_indexer.py       # 📚 Codebase → Vector DB
│       ├── code_retriever.py     # 🔍 Semantic search (RAG)
│       ├── research_agent.py     # 🔬 Investigation orchestrator
│       ├── solution_agent.py     # 🧠 LLM fix generator
│       └── github_commenter.py   # 💬 GitHub API poster
│
├── tests/
│   ├── __init__.py               # Package marker
│   └── test_webhook.py           # 🧪 Fake GitHub payloads
│
└── data/
    └── chroma_db/                # 🗄️ Vector database storage
```

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/autonomous-issue-resolver.git

cd autonomous-issue-resolver
```

---

## 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
# GitHub
GITHUB_TOKEN=your_github_token

# Groq / OpenAI Compatible APIs
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# LLM
LLM_MODEL=llama3-8b-8192

# App
DEBUG=true
```

---

# 🔑 Getting API Keys

## Groq API Key

1. Visit:
   https://console.groq.com/keys

2. Generate a new API key

---

## GitHub Token

1. Open GitHub
2. Go to:

```text
Settings → Developer Settings → Personal Access Tokens
```

3. Create a token with:

```text
repo permissions
```

---

# ▶️ Run The Server

```bash
PYTHONPATH=src uvicorn src.main:app --reload --port 8000
```

Server starts at:

```text
http://127.0.0.1:8000
```

---

# 🧪 Run Tests

```bash
python3 tests/test_webhook.py
```

---

# 🔗 GitHub Webhook Setup

Go to your repository:

```text
Repository → Settings → Webhooks → Add Webhook
```

Configure:

| Setting | Value |
| --- | --- |
| Payload URL | `https://your-ngrok-url/webhook/github` |
| Content Type | `application/json` |
| Events | `Issues → Opened` |

Save webhook.

---

# 🌐 Expose Localhost Using ngrok

Install ngrok and run:

```bash
ngrok http 8000
```

Copy the generated HTTPS URL and use it in GitHub webhooks.

Example:

```text
https://abc123.ngrok-free.app/webhook/github
```

---

# 🧠 How The System Works

| Step | Description |
| --- | --- |
| Parse | Extract issue title, body, labels |
| Classify | Detect issue type |
| Index | Clone and embed repository |
| Search | Retrieve relevant code |
| Generate | Produce AI fix suggestion |
| Comment | Post response back to GitHub |

---

# 🧪 Example Workflow

## GitHub Issue

```text
"App crashes when clicking login button"
```

## AI Investigation

```text
Type: BUG
Priority: CRITICAL
Confidence: 95%
```

## Retrieved Files

```text
src/components/LoginButton.js
src/screens/AuthScreen.tsx
```

## Generated Response

```text
The issue is likely caused by a missing session null check
before navigation logic executes.
```

## Result

AI automatically comments on the GitHub issue.

---

# 📦 Example API Flow

```text
GitHub Issue
    ↓
Webhook Trigger
    ↓
Issue Classification
    ↓
Repository Indexing
    ↓
Semantic Search
    ↓
LLM Reasoning
    ↓
GitHub Comment Posted
```

---

# 🔮 Future Improvements

- [ ] Automatic PR generation
- [ ] AI-generated code patches
- [ ] Multi-repository support
- [ ] Similar issue detection
- [ ] Slack / Discord integration
- [ ] Confidence-based auto-merge
- [ ] Docker deployment
- [ ] CI/CD support

---

# 🧹 Recommended `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc
venv/

# Environment
.env

# VSCode
.vscode/

# macOS
.DS_Store

# ChromaDB
data/chroma_db/
```

---

# ⚠️ Important Security Note

Never commit:

- `.env`
- API keys
- GitHub tokens
- `.pyc` files

GitHub secret scanning will block pushes containing secrets.

---

# 👥 Team

Built for hackathons and autonomous developer tooling experiments.

---

# 📜 License

MIT License