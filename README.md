# Local Chatbot with Django REST Framework + Ollama + React + Tailwind

A beginner-friendly guide to build a local chatbot using:

- Django + Django REST Framework
- ModelViewSet + Routers
- Ollama for local LLM inference
- React + Vite
- Tailwind CSS v4 with `@tailwindcss/vite`

This project runs locally on your machine and can answer both general questions and knowledge-based questions from your own files.

---

## 1) What this project does

You will have:

- a Django backend with chat conversations and messages
- an API endpoint like `POST /api/conversations/<id>/chat/`
- a React frontend that looks like a chatbot
- local AI responses using Ollama
- optional company knowledge from `.json`, `.txt`, or `.py` files

---

## 2) Requirements

### Install these first

- Python 3.11+
- Node.js 20.19+ (Vite 8+ recommends this range)
- Ollama
- Git (optional but useful)

### On macOS

For Ollama, download the macOS app, open the `.dmg`, and drag **Ollama** into **Applications**.

After installation, Ollama runs locally and exposes its API at:

```bash
http://localhost:11434
```

---

## 3) Install Ollama

### Download and install
1. Go to the Ollama download page in your browser.
2. Download the macOS installer.
3. Open the `.dmg`.
4. Drag Ollama into the Applications folder.

### Start Ollama
Open the Ollama app, or run:

```bash
ollama serve
```

### Check it is working

```bash
ollama
```

or:

```bash
curl http://localhost:11434/api/tags
```

---

## 4) Pull the models you already have

You already have:

- `llama3:8b`
- `qwen2.5:7b`

For this chatbot, I recommend:

- Best balance: `qwen2.5:7b`
- Fastest: `phi3:mini` if you later want to pull it

You can confirm available models with:

```bash
ollama list
```

---

## 5) Project structure

Create this structure:

```txt
chatbot-project/
  backend/
    manage.py
    backend/
      settings.py
      urls.py
      asgi.py
      wsgi.py
    chat/
      models.py
      serializers.py
      views.py
      urls.py
      knowledge_loader.py
    knowledge/
      detail.json
      detail.txt
      pricing.py
  frontend/
    index.html
    vite.config.js
    src/
      main.jsx
      index.css
      App.jsx
```

---

## 6) Backend setup

### Create virtual environment

From your project folder:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### Install backend packages

```bash
pip install django djangorestframework django-cors-headers requests
```

### Create Django project and app

```bash
django-admin startproject backend
cd backend
python manage.py startapp chat
```

---

## 7) Django settings

Edit `backend/settings.py`.

### Add apps and middleware

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-me"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "chat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

WSGI_APPLICATION = "backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
```

---

## 8) Models

Create `chat/models.py`

```python
from django.db import models


class Conversation(models.Model):
    title = models.CharField(max_length=200, default="New chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    ROLE_CHOICES = [
        ("system", "System"),
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
```

---

## 9) Serializers

Create `chat/serializers.py`

```python
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "messages"]
```

---

## 10) Knowledge loader

This file loads your `.json`, `.txt`, and `.py` files.

Create `chat/knowledge_loader.py`

```python
import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")


def load_all_knowledge():
    if not os.path.exists(KNOWLEDGE_DIR):
        return ""

    data = ""

    for file in os.listdir(KNOWLEDGE_DIR):
        path = os.path.join(KNOWLEDGE_DIR, file)

        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                data += f.read() + "\n"

        elif file.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                data += json.dumps(json_data, indent=2) + "\n"

        elif file.endswith(".py"):
            with open(path, "r", encoding="utf-8") as f:
                data += f.read() + "\n"

    return data


def search_knowledge(user_text):
    """
    Faster version:
    - if order number exists in the question, search detail.json only
    - otherwise return a smaller text snippet
    """
    if not os.path.exists(KNOWLEDGE_DIR):
        return ""

    result = ""

    match = re.search(r"\b\d{3,10}\b", user_text or "")
    if match:
        order_id = match.group()
        json_path = os.path.join(KNOWLEDGE_DIR, "detail.json")

        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                orders = json.load(f)

            if isinstance(orders, list):
                for order in orders:
                    if str(order.get("order_id")) == order_id:
                        return json.dumps(order, indent=2)
            elif isinstance(orders, dict):
                if str(orders.get("order_id")) == order_id:
                    return json.dumps(orders, indent=2)

    txt_path = os.path.join(KNOWLEDGE_DIR, "detail.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            result += f.read()

    return result[:3000]
```

---

## 11) ViewSet chatbot API

Create `chat/views.py`

This version is optimized:

- only keeps recent history
- avoids empty assistant messages
- uses a smaller prompt
- uses `qwen2.5:7b` by default
- avoids sending huge knowledge blocks every time unless you choose that route

```python
import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer
from .knowledge_loader import search_knowledge


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.prefetch_related("messages").all().order_by("-created_at")
    serializer_class = ConversationSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        conversation = self.get_object()
        user_text = (request.data.get("message") or "").strip()

        if not user_text:
            return Response(
                {"detail": "Message cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save user message
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_text,
        )

        # Fast knowledge lookup
        knowledge = search_knowledge(user_text)

        # Keep recent valid history only
        recent_messages = (
            conversation.messages
            .exclude(content="")
            .order_by("-created_at")[:4][::-1]
        )

        ollama_messages = [
            {
                "role": "system",
                "content": f"""
You are a helpful assistant.

Use company knowledge below to answer accurately.

COMPANY KNOWLEDGE:
{knowledge}

Rules:
1. If the answer exists in company knowledge, use it accurately.
2. If the answer is not found in company knowledge, politely say it is not available.
3. Do not invent company-related answers.
4. If the question is unrelated to company knowledge, answer from your general knowledge.
5. Always return a meaningful response.
6. Never return an empty response.
7. Keep responses short and useful.
""".strip()
            }
        ]

        for msg in recent_messages:
            if msg.role in ["user", "assistant", "system"] and msg.content.strip():
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content.strip(),
                })

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 150,
                "num_ctx": 2048,
            },
        }

        try:
            r = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=300,
            )
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as exc:
            return Response(
                {"detail": f"Ollama request failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assistant_text = data.get("message", {}).get("content", "").strip()

        if not assistant_text:
            return Response(
                {"detail": "Model returned an empty response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=assistant_text,
        )

        conversation.refresh_from_db()
        return Response(ConversationSerializer(conversation).data)
```

---

## 12) Router URLs

Create `chat/urls.py`

```python
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")

urlpatterns = router.urls
```

Edit `backend/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("chat.urls")),
]
```

---

## 13) Migrate backend

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8000
```

---

## 14) Frontend setup

### Create Vite React app

From your project root:

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### Install Tailwind CSS v4

```bash
npm install tailwindcss @tailwindcss/vite
```

### `vite.config.js`

Use the config you already have:

```js
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
})
```

### `src/index.css`

```css
@import "tailwindcss";
```

### `src/main.jsx`

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### `src/App.jsx`

```jsx
import { useEffect, useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000/api'

export default function App() {
  const [conversationId, setConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    createConversation()
  }, [])

  async function createConversation() {
    try {
      const res = await fetch(`${API_BASE}/conversations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New chat' }),
      })

      const data = await res.json()
      setConversationId(data.id)
      setMessages(data.messages || [])
    } catch (err) {
      setStatus('Failed to create conversation.')
    }
  }

  async function sendMessage(e) {
    e.preventDefault()
    if (!input.trim() || !conversationId || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)
    setStatus('')

    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])

    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      })

      const data = await res.json()

      if (!res.ok) {
        setStatus(data.detail || 'Something went wrong.')
        return
      }

      setMessages(data.messages || [])
    } catch (err) {
      setStatus('Backend not reachable.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col p-4">
        <header className="mb-4 rounded-3xl border border-white/10 bg-white/5 p-5 shadow-2xl">
          <h1 className="text-2xl font-bold">Local Chatbot</h1>
          <p className="mt-2 text-sm text-slate-300">
            React + Tailwind + Django REST + Ollama
          </p>
        </header>

        <main className="flex flex-1 flex-col rounded-3xl border border-white/10 bg-white/5 p-4 shadow-2xl">
          <div className="flex-1 space-y-3 overflow-y-auto p-2">
            {messages.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/15 p-6 text-slate-400">
                Start the conversation by sending a message.
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'ml-auto bg-blue-600 text-white'
                      : 'bg-slate-800 text-slate-100'
                  }`}
                >
                  <div className="mb-1 text-xs uppercase opacity-70">{msg.role}</div>
                  <div className="whitespace-pre-wrap">
                    {msg.content || 'Empty response'}
                  </div>
                </div>
              ))
            )}
          </div>

          {status ? (
            <div className="mt-3 rounded-2xl border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-200">
              {status}
            </div>
          ) : null}

          <form onSubmit={sendMessage} className="mt-4 flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 outline-none placeholder:text-slate-500 focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-2xl bg-blue-600 px-5 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Thinking...' : 'Send'}
            </button>
          </form>
        </main>
      </div>
    </div>
  )
}
```

---

## 15) Run the frontend

```bash
npm run dev
```

The app should open at:

```bash
http://localhost:5173
```

---

## 16) Add your own knowledge files

Create:

```txt
backend/knowledge/detail.json
backend/knowledge/detail.txt
backend/knowledge/pricing.py
```

### Example `detail.json`

```json
[
  {
    "order_id": "1024",
    "name": "Shikhar",
    "status": "Shipped",
    "address": "Kathmandu"
  }
]
```

### Example `detail.txt`

```txt
Return Policy:
Items can be returned within 7 days with invoice.
```

### Example `pricing.py`

```python
tax_rate = 0.13
discount = 0.10
```

---

## 17) Speed optimization tips

If the bot feels slow:

1. Use `qwen2.5:7b` instead of a heavier model.
2. Keep only the last 4 chat messages.
3. Search only the relevant knowledge instead of loading all files.
4. Lower `num_predict` if you want shorter answers.
5. Use streaming later if you want the UI to feel instant.
6. Make sure Ollama is already running before you ask the first question.

---

## 18) Common problems

### Problem: Empty response after one chat
Possible reasons:
- blank assistant response got saved
- too much history sent to Ollama
- huge knowledge text in system prompt

Fix:
- do not save empty assistant replies
- keep recent messages only
- use `search_knowledge(user_text)` instead of loading everything

### Problem: `JSONDecodeError: Extra data`
This usually means Ollama streamed multiple JSON objects.

Fix:
- set `"stream": False`

### Problem: Frontend cannot reach backend
Check:
- Django is running on `http://127.0.0.1:8000`
- frontend runs on `http://localhost:5173`
- `CORS_ALLOWED_ORIGINS` includes the frontend URL

### Problem: Ollama not found
Check:
- Ollama app is installed
- `ollama serve` is running
- `ollama list` shows your models

---

## 19) Helpful commands

### Show installed models

```bash
ollama list
```

### Start Ollama API server

```bash
ollama serve
```

### Pull a new model

```bash
ollama pull qwen2.5:7b
```

### Run Django backend

```bash
python manage.py runserver 8000
```

### Run React frontend

```bash
npm run dev
```

---

## 20) Suggested model choice

For this project:

- Best balance: `qwen2.5:7b`
- If you want faster: smaller models like `phi3:mini`
- If you want more general chat: `llama3:8b`

---

## 21) Final flow

1. Start Ollama
2. Start Django backend
3. Start React frontend
4. Create a conversation
5. Send a message
6. Django searches relevant knowledge
7. Django sends a compact prompt to Ollama
8. Ollama returns the answer
9. React displays the reply

---

## 22) Next upgrades

Later you can add:

- streaming responses
- conversation delete/edit
- markdown rendering
- file upload
- PDF support
- database-based order search
- admin dashboard
- login/authentication
- RAG with embeddings for larger knowledge bases
