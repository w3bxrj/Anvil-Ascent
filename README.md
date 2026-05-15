# 🤖 Autonomous Issue Resolver

&gt; **AI-powered GitHub issue investigation & autonomous resolution system**
&gt; 
&gt; *Built for Hackathons | Autonomous Agents | RAG + LLM Pipeline*

---

## 🎯 What It Does

When a new GitHub issue is opened, our autonomous agent:

1. **🔔 Receives** the issue via webhook
2. **🏷️ Classifies** it (Bug / Feature / Security / Performance / Docs)
3. **🔍 Researches** the codebase using RAG (Retrieval Augmented Generation)
4. **🧠 Generates** a solution using LLM (Groq/Gemini/OpenAI)
5. **💬 Posts** an AI-powered comment back to the issue

**Zero human intervention. Fully autonomous.**

---

## 🏗️ Architecture
GitHub Issue Opened
│
▼
┌─────────────────┐
│  Webhook Parser │  ← FastAPI + Pydantic
│  & Classifier   │
└────────┬────────┘
│
▼
┌─────────────────┐
│  Research Agent │  ← ChromaDB + Sentence Transformers
│  (RAG Pipeline) │
└────────┬────────┘
│
▼
┌─────────────────┐
│  Solution Agent │  ← LLM (Groq/Gemini/OpenAI)
│  (Code Drafting)│
└────────┬────────┘
│
▼
┌─────────────────┐
│  GitHub Comment │  ← GitHub REST API
│  Poster         │
└─────────────────┘

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- GitHub Personal Access Token
- LLM API Key (Groq / Gemini / OpenAI)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/autonomous-issue-resolver.git
cd autonomous-issue-resolver

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

2. Configure Environment

cp .env.example .env
# Edit .env with your keys

# GitHub
GITHUB_TOKEN=ghp_your_github_token_here

# LLM (Choose one)
# Groq (Fast, Free Tier)
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama3-8b-8192

# OR Gemini
# OPENAI_API_KEY=your_gemini_key
# OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
# LLM_MODEL=gemini-2.0-flash

# OR OpenAI
# OPENAI_API_KEY=sk-your-openai-key
# OPENAI_BASE_URL=https://api.openai.com/v1
# LLM_MODEL=gpt-4o-mini

DEBUG=true

3. Run Server

PYTHONPATH=src uvicorn src.main:app --reload --port 8000

