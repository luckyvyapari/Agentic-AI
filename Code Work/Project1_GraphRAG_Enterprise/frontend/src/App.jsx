import React, { useState } from 'react';
import './index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8001/ingest', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      alert(`Success! Ingested ${data.nodes_created} graph nodes.`);
    } catch (err) {
      console.error(err);
      alert('Upload failed');
    }
  };

  const handleSend = async () => {
    if (!input) return;
    setLoading(true);
    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages);
    setInput('');

    try {
      const res = await fetch('http://localhost:8001/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await res.json();
      setMessages([...newMessages, { role: 'ai', text: data.answer, sources: data.sources, path: data.graph_path }]);
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { role: 'ai', text: 'Error: Could not get response.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header style={{ padding: '1rem', borderBottom: '1px solid var(--glass-border)' }}>
        <h1 style={{ textAlign: 'center', margin: 0 }}>Enterprise GraphRAG Agent</h1>
      </header>

      <div className="chat-container glass-card">
        <div className="upload-section" style={{ padding: '1rem', borderBottom: '1px solid var(--glass-border)', display: 'flex', gap: '1rem' }}>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <button className="btn-primary" onClick={handleUpload}>Ingest Doc</button>
        </div>

        <div className="message-list">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-muted)' }}>
              Ask anything about your ingested documents...
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              <div>{m.text}</div>
              {m.sources && (
                <div style={{ marginTop: '0.5rem' }}>
                  {m.sources.slice(0, 2).map((s, idx) => (
                    <span key={idx} className="source-tag">{s}</span>
                  ))}
                </div>
              )}
              {m.path && m.path.length > 0 && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <strong>Graph Path:</strong> {m.path.join(' → ')}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="message ai">Thinking...</div>}
        </div>

        <div className="input-area" style={{ display: 'flex', gap: '1rem', padding: '1rem' }}>
          <input 
            style={{ flexGrow: 1, padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)', color: 'white' }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question..."
          />
          <button className="btn-primary" onClick={handleSend} disabled={loading}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
