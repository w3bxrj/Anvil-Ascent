# 🛡️ Sentinel: Autonomous Issue Resolver v4.0

> **A self-evolving, multi-agent software engineering pipeline that investigates, reasons, validates, and resolves GitHub issues with minimal human oversight.**

[![Omium Tracing](https://img.shields.io/badge/Observability-Omium-blueviolet)](https://omium.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0%2B-009688)](https://fastapi.tiangolo.com/)

---

## 🌌 The Vision

Most AI developer tools are **reactive**. They wait for a prompt, provide a snippet, and stop. **Sentinel** is **proactive**. It watches your repository, plans its own investigation, searches for context, generates competing hypotheses, and validates its own fixes before even suggesting them to a human.

It's not just a chatbot; it's a **digital teammate**.

---

## 🧠 Multi-Agent Intelligence Center

Sentinel operates using a hierarchical swarm of specialized agents, each fine-tuned for a specific stage of the software development lifecycle:

| Agent | Responsibility | Key Tech |
| :--- | :--- | :--- |
| **🧠 Planner** | The Strategist. Breaks down issues and selects tools. | CoT Reasoning |
| **🔍 Research** | The Investigator. Performs semantic code retrieval. | ChromaDB / RAG |
| **💡 Hypothesis** | The Thinker. Evaluates competing root-cause theories. | Evidence Matching |
| **🛠️ Solution** | The Implementer. Generates code patches and fixes. | LLM (Gemini/Groq) |
| **⚖️ Critic** | The Guardrail. Validates fixes and prevents hallucinations. | Calibration Logic |
| **💾 Memory** | The Learner. Stores patterns from past successes/failures. | Vector Memory |
| **📢 PR Gen** | The Communicator. Drafts PRs and GitHub responses. | GitHub API |

---

## ⚡ Autonomous Workflow

Sentinel doesn't follow a hardcoded script. Its workflow is **dynamic and event-driven**:

1.  **Trigger**: A GitHub Webhook notifies Sentinel of a new issue.
2.  **Triaging**: The **Classifier** determines severity and type.
3.  **Planning**: The **Planner** creates a custom execution graph.
4.  **Discovery**: **Research** & **Memory** agents retrieve relevant code and historical context.
5.  **Reasoning**: **Hypothesis** agent tests theories against the code.
6.  **Synthesis**: **Solution** agent generates a targeted fix.
7.  **Validation**: **Critic** agent evaluates the fix. If it fails, the loop restarts or escalates.
8.  **Execution**: High-confidence fixes are posted as **Draft PRs** or detailed comments.

---

## 🛠️ Tool Surface & Tech Stack

-   **Backend**: FastAPI (Async-first orchestration)
-   **Observability**: **Omium SDK** (Full causal threading and trace visibility)
-   **Vector Engine**: ChromaDB (Repository indexing and semantic search)
-   **Embeddings**: Sentence-Transformers (Local, fast embeddings)
-   **LLMs**: Gemini 1.5 Pro / Flash, Groq (Llama 3), OpenAI
-   **Integration**: GitHub Webhooks & REST API

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
git clone https://github.com/reak-projects/anvil-hackathon.git
cd anvil-hackathon
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Configure `.env`
```env
GITHUB_TOKEN=your_pat
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1 # Or OpenAI/Gemini
LLM_MODEL=gemini-2.0-flash
OMIUM_API_KEY=your_omium_key
```

### 3. Launch Sentinel
```bash
PYTHONPATH=src uvicorn src.main:app --reload
```

---

## 📊 Observability with Omium

Sentinel is fully instrumented with **Omium**, providing deep visibility into:
-   Agent decision-making paths
-   RAG retrieval accuracy
-   Token usage and latency
-   Causal links between "Issue Opened" and "Fix Suggested"

---

## 📜 Whitepaper

For a deep dive into the architecture and autonomous logic, see the [**SENTINEL WHITEPAPER**](SENTINEL_WHITEPAPER.md).

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ for the Anvil Hackathon.**
