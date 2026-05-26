import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import './App.css'

const API = 'http://localhost:8000'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [activeDocId, setActiveDocId] = useState(null)
  const [chatHistory, setChatHistory] = useState({})
  const [isUploading, setIsUploading] = useState(false)
  const [isAsking, setIsAsking] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [askError, setAskError] = useState(null)

  useEffect(() => {
    fetch(`${API}/documents`)
      .then(r => r.json())
      .then(setDocuments)
      .catch(() => {})
  }, [])

  async function handleUpload(file) {
    setIsUploading(true)
    setUploadError(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const r = await fetch(`${API}/upload`, { method: 'POST', body: form })
      if (!r.ok) {
        const err = await r.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const doc = await r.json()
      setDocuments(prev => [...prev, doc])
      setActiveDocId(doc.doc_id)
    } catch (e) {
      setUploadError(e.message)
    } finally {
      setIsUploading(false)
    }
  }

  async function handleDelete(docId) {
    await fetch(`${API}/document/${docId}`, { method: 'DELETE' })
    setDocuments(prev => prev.filter(d => d.doc_id !== docId))
    if (activeDocId === docId) setActiveDocId(null)
    setChatHistory(prev => {
      const next = { ...prev }
      delete next[docId]
      return next
    })
  }

  async function handleAsk(question) {
    setIsAsking(true)
    setAskError(null)
    setChatHistory(prev => ({
      ...prev,
      [activeDocId]: [
        ...(prev[activeDocId] || []),
        { role: 'user', content: question },
      ],
    }))
    try {
      const r = await fetch(`${API}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: activeDocId, question }),
      })
      if (!r.ok) {
        const err = await r.json()
        throw new Error(err.detail || 'Request failed')
      }
      const { answer, sources } = await r.json()
      setChatHistory(prev => ({
        ...prev,
        [activeDocId]: [
          ...(prev[activeDocId] || []),
          { role: 'assistant', content: answer, sources },
        ],
      }))
    } catch (e) {
      setAskError(e.message)
      setChatHistory(prev => ({
        ...prev,
        [activeDocId]: (prev[activeDocId] || []).slice(0, -1),
      }))
    } finally {
      setIsAsking(false)
    }
  }

  const activeDoc = documents.find(d => d.doc_id === activeDocId) || null
  const messages = activeDocId ? (chatHistory[activeDocId] || []) : []

  return (
    <div className="app-layout">
      <Sidebar
        documents={documents}
        activeDocId={activeDocId}
        isUploading={isUploading}
        uploadError={uploadError}
        onSelect={setActiveDocId}
        onUpload={handleUpload}
        onDelete={handleDelete}
      />
      <main className="main">
        <Chat
          activeDoc={activeDoc}
          messages={messages}
          isAsking={isAsking}
          askError={askError}
          onAsk={handleAsk}
        />
      </main>
    </div>
  )
}
