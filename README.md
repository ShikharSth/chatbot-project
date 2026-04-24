# Local AI Chatbot (Django REST + React + Ollama)

A beginner-friendly **Local AI Chatbot** using:

* **Backend:** Django + Django REST Framework (ModelViewSet)
* **Frontend:** React + Vite + Tailwind CSS
* **AI Engine:** Ollama (local LLM)
* **Knowledge Files:** JSON / TXT / PY support

This project runs **fully on your computer** using local AI models like:

* `llama3:8b`
* `qwen2.5:7b`
* `phi3:mini`

---

# Features

✅ ChatGPT-style chatbot UI
✅ Django REST API with ModelViewSet
✅ React + Tailwind frontend
✅ Uses local Ollama models
✅ Reads company/order data from files
✅ Order lookup from JSON
✅ Policy lookup from TXT
✅ Fast optimized responses
✅ No OpenAI API cost
✅ Runs offline after setup

---

# Project Structure

```txt
chatbot-project/
│── backend/
│   │── manage.py
│   │── requirements.txt
│   │── knowledge/
│   │   │── detail.json
│   │   │── detail.txt
│   │── chat/
│   │── backend/
│
│── frontend/
│   │── package.json
│   │── src/
│
│── README.md
```

---

# 1. Install Ollama

## Mac

1. Visit:
   https://ollama.com/download

2. Download macOS version

3. Open `.dmg`

4. Drag Ollama to Applications

5. Open Ollama app

---

## Windows

1. Visit:
   https://ollama.com/download

2. Download Windows installer

3. Install normally

4. Open Ollama

---

# 2. Install AI Model

Open Terminal / CMD:

```bash
ollama pull qwen2.5:7b
```

OR

```bash
ollama pull llama3:8b
```

OR fastest:

```bash
ollama pull phi3:mini
```

---

# 3. Start Ollama

```bash
ollama serve
```

Runs on:

```txt
http://localhost:11434
```

---

# 4. Clone GitHub Project

```bash
git clone YOUR_GITHUB_REPO_URL
cd chatbot-project
```

---

# 5. Backend Setup

Go backend folder:

```bash
cd backend
```

---

## Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

# Install Python Packages

```bash
pip install -r requirements.txt
```

---

# Run Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Run Backend

```bash
python manage.py runserver
```

Backend:

```txt
http://127.0.0.1:8000
```

---

# 6. Frontend Setup

Open new terminal:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Run frontend:

```bash
npm run dev
```

Frontend:

```txt
http://localhost:5173
```

---

# 7. Change AI Model

Open:

```txt
backend/backend/settings.py
```

Change:

```python
OLLAMA_MODEL = "qwen2.5:7b"
```

Other options:

```python
OLLAMA_MODEL = "llama3:8b"
OLLAMA_MODEL = "phi3:mini"
```

---

# 8. Knowledge Files

Put files inside:

```txt
backend/knowledge/
```

Example:

## detail.json

```json
[
  {
    "order_id": "1024",
    "name": "Shikhar",
    "status": "Shipped"
  }
]
```

## detail.txt

```txt
Return policy:
Products can be returned within 7 days.
```

Now chatbot can answer:

* Where is order 1024?
* What is return policy?

---

# 9. Common Commands

## Run Backend

```bash
python manage.py runserver
```

## Run Frontend

```bash
npm run dev
```

## Run Ollama

```bash
ollama serve
```

---

# 10. Troubleshooting

## Ollama not found

Install Ollama and restart terminal.

---

## Backend error

Check:

```bash
pip install -r requirements.txt
```

---

## Frontend not loading

Run:

```bash
npm install
npm run dev
```

---

## Slow response

Use faster model:

```python
OLLAMA_MODEL = "phi3:mini"
```

---

# 11. Recommended Models

## Best Quality

```txt
qwen2.5:7b
```

## Balanced

```txt
llama3:8b
```

## Fastest

```txt
phi3:mini
```

---

# 12. Future Upgrade Ideas

✅ Streaming response
✅ Chat history sidebar
✅ Login system
✅ PostgreSQL
✅ Docker deployment
✅ PDF knowledge upload
✅ Voice chatbot

---

# Author

Built with Django + React + Ollama

---
