import { useRef } from 'react'

export default function Sidebar({
  documents,
  activeDocId,
  isUploading,
  uploadError,
  onSelect,
  onUpload,
  onDelete,
}) {
  const inputRef = useRef(null)

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (file) onUpload(file)
    e.target.value = ''
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-title">Docquery</span>
        <span className="sidebar-subtitle">Ask questions about your PDFs</span>
      </div>

      <hr className="sidebar-divider" />

      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <button
        className="upload-btn"
        disabled={isUploading}
        onClick={() => inputRef.current.click()}
      >
        {isUploading ? (
          <>
            <span className="spinner" /> Uploading…
          </>
        ) : (
          '+ Upload PDF'
        )}
      </button>

      {uploadError && <p className="upload-error">{uploadError}</p>}

      <div className="doc-list">
        {documents.length === 0 ? (
          <p className="empty-state">No documents yet. Upload a PDF to get started.</p>
        ) : (
          documents.map(doc => (
            <div
              key={doc.doc_id}
              className={`doc-item${doc.doc_id === activeDocId ? ' active' : ''}`}
              onClick={() => onSelect(doc.doc_id)}
            >
              <div className="doc-item-body">
                <span className="doc-filename">{doc.filename}</span>
                <span className="doc-chunks">{doc.chunks} chunks</span>
              </div>
              <button
                className="doc-delete"
                onClick={e => {
                  e.stopPropagation()
                  onDelete(doc.doc_id)
                }}
                title="Delete document"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  )
}
