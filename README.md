# 🐋 CodeForge

> **Your AI co‑founder, senior architect, and code generator – design, plan, and build production‑ready software, all offline.**

CodeForge is a **conversational AI developer studio** that helps you design, architect, and generate code for your software projects. It runs entirely on your laptop, respects your privacy, and gives you **copy‑ready code** – you manage the files and run the project yourself.

---

## 🎯 What CodeForge Does

- **Plans** the architecture – tech stack, data models, relationships, API structure.
- **Writes** production‑ready code for any file (models, views, controllers, tests, etc.).
- **Explains** design decisions and concepts clearly.
- **Adds** new features to your project context.
- **Generates** unit tests, OpenAPI documentation, refactoring suggestions, security audits, and deployment strategies.
- **Remembers** the entire conversation – no need to repeat yourself.
- **Continues** long responses gracefully with the `@continue` command.

**You** copy the code, paste it into your own project, and run it. CodeForge is the architect – you are the builder.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 4.2 + Python 3.11 |
| **Frontend** | Alpine.js (local), Tailwind CSS (custom dark theme) |
| **LLM** | Qwen‑Coder 1.5B / 7B (GGUF, via `llama-cpp-python`) |
| **RAG** | TF‑IDF + Scikit‑learn (lightweight, no PyTorch) |
| **File Monitoring** | Watchdog (for `knowledge/` folder) |
| **Storage** | SQLite (Django ORM – for chat history) |
| **Frontend Libraries** | `marked.js`, `highlight.js` (local, no CDN) |

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/codeforge.git
cd codeforge

2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows

3. Install Dependencies
bash
pip install -r requirements.txt
4. Download the Model(s)
Place your .gguf model file in the models/ folder:

qwen2.5-coder-1.5b-instruct-q4_k_m.gguf (≈1.0 GB)

qwen2.5-coder-7b-instruct-q4_k_m.gguf (≈4.7 GB) – optional

5. Run Migrations
bash
python manage.py migrate
6. Start the Server
bash
python manage.py runserver

7. Open the App
Visit http://localhost:8000/ in your browser.

🧭 How to Use
The Dashboard
A single, clean chat interface.

Use natural language to describe your idea or use @commands.

@commands – Your Toolbox
Command	What It Does
@plan <idea>	Generates a high‑level architecture plan (tech stack, models, APIs, etc.).
@code <request>	Writes production‑ready code for a specific file or component.
@explain <topic>	Explains a design decision, pattern, or concept.
@add <feature>	Adds a new feature to your project context.
@test <request>	Generates unit tests (pytest, PHPUnit, JUnit).
@docs <request>	Generates OpenAPI/Swagger documentation.
@refactor <request>	Suggests refactoring and provides the refactored code.
@audit <request>	Performs a security audit and provides fixes.
@infra <request>	Recommends a deployment strategy (Docker, CI/CD, hosting).
@continue	Continues a cut‑off response (token limit).
@help	Shows all available commands.
Copy Code
Every code block has a "📋 Copy Code" button – one click copies all code from the response.

Chat Export
Click "📥 Export Chat" to download the entire conversation as a Markdown file.

Knowledge Base (RAG)
Drop .txt, .md, .pdf, .docx files into the knowledge/ folder.

The system automatically indexes them (via Watchdog).

The assistant will reference these documents when answering.


🧪 Example Workflow

You: @plan a task management system using Django

CodeForge: [Streams a detailed architecture plan with models, relationships, API structure, and folder layout.]

You: @code the Task model

CodeForge: [Streams the full code for the Task model in Django.]

You: [Click "Copy Code" → paste into your project's models.py]

You: @add user authentication to this project

CodeForge: [Streams code for login, logout, registration, and URL patterns.]

You: @test the Task model

CodeForge: [Streams unit tests for the Task model.]

You: @docs the API

CodeForge: [Streams OpenAPI YAML documentation.]

🗂️ Project Structure (Simplified)

codeforge/
├── apps/
│   ├── chat/          # LLM wrapper, router, commands, streaming
│   ├── core/          # Startup, resource monitor
│   └── knowledge/     # RAG ingestion and query (TF‑IDF)
├── config/            # Django settings and URL routing
├── templates/         # Base templates and includes
├── static/            # CSS, JS, and local libraries
├── knowledge/         # 📂 Upload specs here – auto‑indexed
├── models/            # GGUF model files (1.5B / 7B)
├── requirements.txt
├── manage.py
└── README.md

🔧 Troubleshooting
Issue                   Solution
Model fails to load ->	Check settings.py – ensure the .gguf path is correct and the file exists.
PyTorch/ONNX errors ->	CodeForge uses TF‑IDF, not PyTorch. If you see these, make sure you haven't installed sentence-transformers or torch accidentally.
Chat history disappears ->	Migrations must be run. Run python manage.py migrate.
@continue doesn't continue -> 	Ensure the previous response was stored. Send a long @plan first to test.
Copy button not showing  ->	Check that the message contains a code block (...).

📜 License
MIT – use it freely, modify, and share.

🙏 Acknowledgments
Qwen for the Qwen‑Coder models.

llama-cpp-python for CPU inference.

Alpine.js for lightweight reactivity.

Highlight.js and marked.js for offline syntax highlighting and Markdown rendering.

