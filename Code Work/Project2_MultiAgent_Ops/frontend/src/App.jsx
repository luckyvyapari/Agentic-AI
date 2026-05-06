import React, { useState } from 'react';
import './index.css';

function App() {
  const [threadId, setThreadId] = useState('');
  const [query, setQuery] = useState('');
  const [steps, setSteps] = useState([]);
  const [messages, setMessages] = useState([]);
  const [pendingApproval, setPendingApproval] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('IDLE');


  const startWorkflow = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8003/run', {

        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      setThreadId(data.thread_id);
      setSteps(data.logs);
      setMessages(data.messages);
      setPendingApproval(data.pending_approval);
      setStatus(data.next === 'FINISH' ? 'COMPLETED' : data.pending_approval ? 'WAITING APPROVAL' : 'PROCESSING');

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approve) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8003/approve', {

        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, approve })
      });
      const data = await res.json();
      setSteps(data.logs);
      setMessages(data.messages);
      setPendingApproval(null);
      setStatus('COMPLETED');

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="glass-card">
        <h1>Multi-Agent Ops Workflow</h1>
        <div className={`status-badge ${status.toLowerCase()}`}>{status}</div>
        <p>Supervisor Orchestration with Human-in-the-Loop</p>

      </header>

      <main>
        <div className="controls glass-card">
          <input 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            placeholder="Describe the operations task..."
          />
          <button className="btn-primary" onClick={startWorkflow} disabled={loading}>
            {loading ? 'Processing...' : 'Start Workflow'}
          </button>
        </div>

        <div className="dashboard-grid">
          <section className="audit-logs glass-card">
            <h2>Audit Logs</h2>
            <div className="log-list">
              {steps.map((log, i) => (
                <div key={i} className="log-item">
                  <span className="node-badge">{log.node}</span>
                  <span className="action-text">{log.action}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="interaction-panel glass-card">
            <h2>Workflow Interaction</h2>
            {pendingApproval ? (
              <div className="approval-ui animate-pulse">
                <p>⚠️ Tool execution requires your approval:</p>
                <pre>{JSON.stringify(pendingApproval, null, 2)}</pre>
                <div className="btn-group">
                  <button className="btn-success" onClick={() => handleApproval(true)}>Approve</button>
                  <button className="btn-danger" onClick={() => handleApproval(false)}>Reject</button>
                </div>
              </div>
            ) : (
              <div className="status-text">
                {steps.length > 0 ? (
                  <>
                    <p style={{ fontWeight: 'bold', marginBottom: '1rem' }}>Final Answer:</p>
                    <div className="answer-box" style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '1rem', borderRadius: '8px', borderLeft: '4px solid #3b82f6', color: '#e2e8f0', lineHeight: '1.6' }}>
                      {messages[messages.length - 1]}
                    </div>
                  </>
                ) : (
                  <p>Enter a task to begin.</p>
                )}
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
