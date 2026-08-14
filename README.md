# 🐋 CodeForge

> **A sovereign, offline-first AI developer studio that builds full-stack SaaS, web apps, and APIs from natural language – all on an 8GB laptop.**

CodeForge is your **personal senior software engineer, architect, and technical lead**. It runs 100% offline, respects your privacy, and transforms natural language prompts into production-ready codebases with proper structure, documentation, and security best practices.

---

## 🚀 Key Features

- **🧠 Sovereign Intelligence** – 100% offline, no cloud APIs, no subscriptions. Your data never leaves your machine.
- **💬 Smart Chat** – Streaming responses with Markdown and syntax highlighting. Smart router handles greetings, time, and date instantly.
- **📚 Global Knowledge Base (RAG)** – Drop `.txt`, `.pdf`, `.docx`, `.md` files into `knowledge/`. Auto-indexed with TF‑IDF. Your assistant always has context.
- **🏗️ Multi-Stack Project Builder** – Generate complete projects with a single prompt.
  - **Backends:** Django, Flask, Laravel, Spring Boot, Node.js (Express)
  - **Frontends:** React, Vue, Blade, Django Templates
- **🖥️ Studio IDE** – Browse file trees, preview code with syntax highlighting, and chat contextually with your project.
- **🔄 Model Swapper** – Switch between **Fast (1.5B)** and **Smart (7B)** models on the fly.
- **🧹 Resource Guardian** – Monitors RAM and pauses heavy operations to prevent crashes on 8GB laptops.
- **🔐 Privacy First** – No telemetry, no external calls. Your code stays local.

---

## 🧰 Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Django 4.2 + Python 3.11 |
| **Frontend** | Alpine.js (local), Tailwind CSS (custom dark theme) |
| **LLM** | Qwen-Coder-1.5B / 7B (GGUF) via `llama-cpp-python` |
| **Vector Search** | TF‑IDF + Scikit‑learn (no PyTorch, no DLL issues) |
| **File Monitoring** | Watchdog |
| **Database** | SQLite (Django ORM) |
| **Frontend Libraries** | `marked.js`, `highlight.js` (fully local) |

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/codeforge.git
cd codeforge


python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

pip install -r requirements.txt

Place your GGUF models in models/:

qwen2.5-coder-1.5b-instruct-q4_k_m.gguf (≈1.0 GB)

qwen2.5-coder-7b-instruct-q4_k_m.gguf (≈4.7 GB)

python manage.py makemigrations
python manage.py migrate

python manage.py runserver

🧭 How to Use
Dashboard (Chat + Scripts)
Ask coding questions, get snippets, and generate scripts in any language.

Quick replies for "hello", "time", and "date".

Conversation history is stored locally.

Studio (Project Workspace)
Click Studio in the navbar.

Create a new project – choose a name and your stack (backend + frontend).

Open the project – explore the file tree, preview code, and chat contextually.

Ask CodeForge to build logic – add models, views, controllers, or entire features.

Switch models – toggle between Fast (1.5B) and Smart (7B) for complex reasoning.

Knowledge Base
Drop .txt, .md, .pdf, .docx files into knowledge/.

The system auto-indexes them (via Watchdog).

Your chat and Studio queries will reference these documents.


🎯 Command Examples
You                                     Say	CodeForge Does
"Write a Python script for hello world"	Returns a code snippet.
"Build a Django blog with user auth"	Creates a full Django project in generated_projects/.
"Add a Post model with title and content"	(In Studio) Generates the model and updates the file.
"Show me my project files"	(In Studio) Opens the file tree.
"Switch to Smart (7B)"	(In Studio) Reloads the 7B model (if RAM allows).

📜 License
MIT – feel free to use, and distribute.

🙏 Acknowledgments
Qwen for the Qwen-Coder models

llama-cpp-python for CPU inference

Alpine.js for lightweight reactivity

Highlight.js and marked.js for offline syntax highlighting and Markdown rendering


---

## 📤 Push to GitHub – Checklist

Before pushing, make sure:

### ✅ Files to Commit
- `apps/`
- `config/`
- `static/`
- `templates/`
- `manage.py`
- `requirements.txt`
- `README.md`
- `.gitignore`

### ❌ Files to Exclude (in `.gitignore`)

venv/
pycache/
*.pyc
db.sqlite3
/knowledge/
/generated_projects/
/models/
/lancedb/
tfidf_index.json
.env


## 📁 Project Structure
codeforge/
├── apps/
│ ├── chat/ # LLM wrapper, router, streaming
│ ├── core/ # Startup, resource monitor, middleware
│ ├── knowledge/ # RAG ingestion and querying (TF‑IDF)
│ ├── projects/ # Project models, generator, builder, scaffolder
│ └── studio/ # Studio IDE (file tree, chat, preview)
├── config/ # Django settings and URL routing
├── templates/ # Base templates and includes
├── static/ # CSS, JS, and libraries (local)
├── knowledge/ # 📂 User uploads specs here – auto-indexed
├── generated_projects/ # 🏗️ All generated projects
├── models/ # GGUF model files (1.5B and 7B)
├── requirements.txt
├── manage.py
└── README.md
