import { useState, useEffect } from 'react'
import './App.css'

function parseClassification(str) {
  try {
    const parsed = JSON.parse(str)
    return {
      category: parsed.category || 'Unknown',
      urgency: (parsed.urgency || 'Medium'),
      confidence: parsed.confidence ?? 100
    }
  } catch {
    return { category: 'Unknown', urgency: 'Medium', confidence: 100 }
  }
}

const IconCheck = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <path d="M20 6L9 17l-5-5" />
  </svg>
)
const IconAlert = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
    <path d="M12 9v4M12 17h.01M10.3 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L14.7 3.86a2 2 0 0 0-3.4 0z" />
  </svg>
)
const IconCopy = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="9" y="9" width="13" height="13" rx="2" />
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
  </svg>
)
const IconChevron = ({ open }) => (
  <svg className={`chevron ${open ? 'open' : ''}`} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M6 9l6 6 6-6" />
  </svg>
)
const IconTrash = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z" />
  </svg>
)
const IconSearch = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8" />
    <path d="M21 21l-4.35-4.35" />
  </svg>
)

const SAMPLE_TICKETS = [
  { label: 'Urgent crash', text: 'My app keeps crashing every time I try to open it, this is really urgent, I use it for work!' },
  { label: 'Vague issue', text: "it's not working can you help" },
  { label: 'Billing', text: 'I was charged twice for my subscription this month, can you refund the extra charge?' },
  { label: 'Product Q', text: 'Does your product support integration with Google Calendar?' },
]

function App() {
  const [view, setView] = useState('new')
  const [ticketText, setTicketText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [expandedId, setExpandedId] = useState(null)
  const [toast, setToast] = useState(null)

  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [sortOrder, setSortOrder] = useState('newest')

  const [lookupId, setLookupId] = useState('')
  const [lookupResult, setLookupResult] = useState(null)
  const [lookupError, setLookupError] = useState('')

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 2200)
  }

  const handleSubmit = async () => {
    setLoading(true)
    setResult(null)
    try {
      const response = await fetch('http://127.0.0.1:8000/process-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_text: ticketText })
      })
      const data = await response.json()
      setResult(data)
      showToast('Ticket processed', 'success')
    } catch (error) {
      showToast('Error: ' + error.message, 'error')
    }
    setLoading(false)
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    showToast('Draft copied to clipboard', 'success')
  }

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    try {
      await fetch(`http://127.0.0.1:8000/tickets/${id}`, { method: 'DELETE' })
      setHistory(prev => prev.filter(t => t.id !== id))
      showToast('Ticket removed', 'info')
    } catch {
      showToast('Failed to delete', 'error')
    }
  }

  const handleLookup = async () => {
    setLookupError('')
    setLookupResult(null)
    try {
      const response = await fetch(`http://127.0.0.1:8000/tickets/${lookupId}`)
      const data = await response.json()
      if (data.error) {
        setLookupError(data.error)
      } else {
        setLookupResult(data)
      }
    } catch {
      setLookupError('Failed to fetch ticket')
    }
  }

  const fetchHistory = () => {
    setHistoryLoading(true)
    fetch('http://127.0.0.1:8000/tickets')
      .then(res => res.json())
      .then(data => {
        setHistory(data)
        setHistoryLoading(false)
      })
      .catch(() => setHistoryLoading(false))
  }

  useEffect(() => {
    if (view === 'history') fetchHistory()
  }, [view])

  const escalatedCount = history.filter(t => t.escalation_status?.includes('ESCALATED')).length
  const approvedCount = history.length - escalatedCount

  const visibleHistory = history
    .filter(t => t.ticket_text.toLowerCase().includes(searchQuery.toLowerCase()))
    .filter(t => {
      if (filterStatus === 'all') return true
      const isEsc = t.escalation_status?.includes('ESCALATED')
      return filterStatus === 'escalated' ? isEsc : !isEsc
    })
    .sort((a, b) => {
      if (sortOrder === 'newest') return new Date(b.created_at) - new Date(a.created_at)
      return new Date(a.created_at) - new Date(b.created_at)
    })

  const renderResultCards = (r) => {
    const { category, urgency, confidence } = parseClassification(r.classification)
    const urgencyKey = urgency.toLowerCase()
    const isEscalated = r.escalation_status?.includes('ESCALATED')

    return (
      <div className="result">
        <div className={`card urgency-${urgencyKey}`}>
          <p className="card-label">Classification</p>
          <div className="badge-row">
            <span className="badge">{category}</span>
            <span className="badge">
              <span className={`dot ${urgencyKey}`}></span>
              {urgency} urgency
            </span>
          </div>
          <div className="confidence-bar-wrap">
            <div className="confidence-bar-bg">
              <div
                className="confidence-bar-fill"
                style={{ width: `${confidence}%`, background: confidence < 70 ? '#E8B84B' : '#45D6C0' }}
              ></div>
            </div>
            <span className="confidence-label">{confidence}% confident</span>
          </div>
        </div>

        <div className={`card urgency-${urgencyKey}`}>
          <p className="card-label">
            Draft response
            <button className="copy-btn" onClick={() => handleCopy(r.draft_response)}>
              <IconCopy /> Copy
            </button>
          </p>
          <p className="card-body">{r.draft_response}</p>
        </div>

        <div className={`card urgency-${urgencyKey}`}>
          <p className="card-label">Escalation status</p>
          <div className={`escalation-line ${isEscalated ? 'escalated' : 'approved'}`}>
            {isEscalated ? <IconAlert /> : <IconCheck />}
            {r.escalation_status}
          </div>
        </div>

        <div className="card">
          <p className="card-label">Similar past tickets</p>
          {r.similar_tickets?.map((t, i) => (
            <div className="similar-item" key={i}>
              <span className="similar-rank">{i + 1}</span>
              <div>
                <p className="similar-meta">{t.category} · {t.priority} priority</p>
                <p className="similar-text">{t.description.slice(0, 140)}...</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="brand-row">
        <span className="brand-dot"></span>
        <h1 className="brand">Triage</h1>
      </div>
      <p className="tagline">AI-assisted support ticket classification and response drafting</p>

      <div className="tabs">
        <button className={`tab ${view === 'new' ? 'active' : ''}`} onClick={() => setView('new')}>
          New ticket
        </button>
        <button className={`tab ${view === 'history' ? 'active' : ''}`} onClick={() => setView('history')}>
          History
        </button>
      </div>

      {view === 'new' && (
        <>
          <div className="sample-row">
            {SAMPLE_TICKETS.map((s, i) => (
              <button key={i} className="sample-chip" onClick={() => setTicketText(s.text)}>
                {s.label}
              </button>
            ))}
          </div>

          <textarea
            value={ticketText}
            onChange={(e) => setTicketText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit()
            }}
            placeholder="Paste a customer support ticket here... (Ctrl+Enter to submit)"
            rows={4}
          />
          <div>
            <button className="process-btn" onClick={handleSubmit} disabled={loading || !ticketText}>
              {loading && <span className="spinner"></span>}
              {loading ? 'Processing' : 'Process ticket'}
            </button>
          </div>

          {result && renderResultCards(result)}
        </>
      )}

      {view === 'history' && (
        <>
          <div className="stats-row">
            <div className="stat-box">
              <div className="stat-num">{history.length}</div>
              <div className="stat-label">Total processed</div>
            </div>
            <div className="stat-box">
              <div className="stat-num" style={{ color: '#F2665C' }}>{escalatedCount}</div>
              <div className="stat-label">Escalated</div>
            </div>
            <div className="stat-box">
              <div className="stat-num" style={{ color: '#63C98C' }}>{approvedCount}</div>
              <div className="stat-label">Auto-approved</div>
            </div>
          </div>

          <div className="lookup-row">
            <input
              type="number"
              placeholder="Enter ticket # to jump to..."
              value={lookupId}
              onChange={(e) => setLookupId(e.target.value)}
            />
            <button className="lookup-btn" onClick={handleLookup} disabled={!lookupId}>
              Look up
            </button>
          </div>

          {lookupError && <p className="lookup-error">{lookupError}</p>}

          {lookupResult && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <p className="card-label">Ticket #{lookupResult.id}</p>
              <p className="card-body" style={{ fontSize: '15px' }}>{lookupResult.ticket_text}</p>
              <div className="badge-row" style={{ marginTop: '10px' }}>
                <span className="badge">
                  {lookupResult.escalation_status?.includes('ESCALATED') ? 'Escalated' : 'Auto-approved'}
                </span>
              </div>
            </div>
          )}

          <div className="filter-row">
            <div className="search-wrap">
              <IconSearch />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="all">All statuses</option>
              <option value="escalated">Escalated only</option>
              <option value="approved">Auto-approved only</option>
            </select>
            <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </div>

          <div className="history-list">
            {historyLoading && <p className="empty-state">Loading...</p>}
            {!historyLoading && visibleHistory.length === 0 && (
              <p className="empty-state">
                {history.length === 0
                  ? <>No tickets processed yet.<br />Process one to see it here.</>
                  : 'No tickets match your filters.'}
              </p>
            )}
            {visibleHistory.map((t) => {
              const { urgency } = parseClassification(t.classification)
              const urgencyKey = urgency.toLowerCase()
              const isOpen = expandedId === t.id
              return (
                <div
                  className={`history-row urgency-${urgencyKey}`}
                  key={t.id}
                  onClick={() => setExpandedId(isOpen ? null : t.id)}
                >
                  <div className="history-top">
                    <span className="badge">
                      <span className={`dot ${urgencyKey}`}></span>
                      #{t.id} · {t.escalation_status?.includes('ESCALATED') ? 'Escalated' : 'Auto-approved'}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="history-time">{new Date(t.created_at).toLocaleString()}</span>
                      <button className="icon-btn" onClick={(e) => handleDelete(t.id, e)} title="Delete">
                        <IconTrash />
                      </button>
                      <IconChevron open={isOpen} />
                    </div>
                  </div>
                  <p className="history-text">{t.ticket_text.slice(0, 160)}...</p>

                  {isOpen && (
                    <div className="history-expand" onClick={(e) => e.stopPropagation()}>
                      <div>
                        <p className="card-label">Draft response</p>
                        <p className="card-body" style={{ fontSize: '15px' }}>{t.draft_response}</p>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}

      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.message}</div>
      )}
    </div>
  )
}

export default App