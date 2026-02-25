const { useState } = React;

function Dashboard() {
  const [message, setMessage] = useState("");

  const prompts = [
    "Explain quantum physics concepts",
    "Help me prepare for my exam",
    "Predict my learning progress",
    "What are the best study techniques?"
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">N</div>
          <div>
            <h1>NAZZ.ai</h1>
            <span>AI Study Platform</span>
          </div>
        </div>

        <nav className="nav">
          <button className="active"><span className="dot"></span> AI Chat</button>
          <button>Study Materials</button>
          <button>Predictions</button>
          <button>Q&A Library</button>
        </nav>

        <div className="section-title">RECENT WORK</div>
        <div className="recent-list">
          <div className="recent-item">Quantum Physics Discussion<span>2 hours ago</span></div>
          <div className="recent-item">Calculus Chapter 5<span>5 hours ago</span></div>
          <div className="recent-item">Organic Chemistry Q&A<span>1 day ago</span></div>
          <div className="recent-item">Exam Performance Analysis<span>2 days ago</span></div>
        </div>

        <div className="sidebar-footer">
          <div className="avatar">N</div>
          <div>
            <div style={{fontWeight: 600}}>nebnaz</div>
            <div style={{fontSize: 10, color: "var(--sidebar-muted)"}}>nebnashadow@gmail.com</div>
          </div>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <h2>AI Chat Assistant</h2>
          <div className="profile-mini">
            <div className="avatar" style={{width: 26, height: 26}}>N</div>
            <div>
              <div style={{fontWeight: 600, color: "var(--text)"}}>nebnaz</div>
              <div>nebnashadow@gmail.com</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="welcome">
            <div className="ai-pill">AI</div>
            <div>
              <div style={{fontWeight: 600, marginBottom: 6}}>Hello! I’m NAZZ.ai, your intelligent study assistant.</div>
              <div style={{color: "var(--muted)", lineHeight: 1.5}}>
                I can help you with questions, provide study materials, make predictions, and much more.
                How can I assist you today?
              </div>
            </div>
          </div>

          <div style={{marginTop: 16}} className="chat-box"></div>
        </div>

        <div>
          <div className="section-title" style={{color: "var(--muted)", marginBottom: 8}}>Suggested prompts:</div>
          <div className="prompt-grid">
            {prompts.map((p) => (
              <button key={p} className="chip" onClick={() => setMessage(p)}>{p}</button>
            ))}
          </div>
        </div>

        <div className="input-row">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me anything about your studies..."
          />
          <button className="send">Send</button>
        </div>

        <div className="footer-note">
          NAZZ.ai is powered by advanced AI. Responses are generated based on study materials and analysis.
        </div>
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Dashboard />);
