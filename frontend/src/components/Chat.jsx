import { useState, useEffect, useRef } from 'react'
import Message from './Message'

export default function Chat({ activeDoc, messages, isAsking, askError, onAsk }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAsking])

  function submit() {
    const q = input.trim()
    if (!q || isAsking) return
    setInput('')
    onAsk(q)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  if (!activeDoc) {
    return (
      <div className="chat-empty">
        <div className="chat-empty-icon">📄</div>
        <p>Select a document to start asking questions</p>
      </div>
    )
  }

  return (
    <div className="chat">
      <div className="chat-header">
        <span className="chat-filename">{activeDoc.filename}</span>
        <span className="chat-chunks">{activeDoc.chunks} chunks</span>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}
        {isAsking && (
          <div className="message message-assistant">
            <div className="message-bubble loading-dots">
              <span>·</span><span>·</span><span>·</span>
            </div>
          </div>
        )}
        {askError && (
          <div className="ask-error">{askError}</div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-bar">
        <input
          className="chat-input"
          type="text"
          placeholder="Ask a question…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isAsking}
        />
        <button
          className="chat-send"
          onClick={submit}
          disabled={!input.trim() || isAsking}
        >
          Send
        </button>
      </div>
    </div>
  )
}
