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
        headers: {
          'Content-Type': 'application/json',
        },
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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      })

      const data = await res.json()

      if (!res.ok) {
        setStatus(data.detail || 'Something went wrong.')
        setLoading(false)
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
                  <div className="whitespace-pre-wrap">{msg.content}</div>
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