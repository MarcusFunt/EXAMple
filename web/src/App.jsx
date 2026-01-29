import { useEffect, useMemo, useRef, useState } from "react";

const initialMessages = [
  {
    role: "assistant",
    content:
      "Hi! Ask a question about your notes or sync the index after adding new files."
  }
];

const statusVariants = {
  ready: "status-ready",
  warning: "status-warning",
  error: "status-error"
};

export default function App() {
  const [modelName, setModelName] = useState("loading...");
  const [backendStatus, setBackendStatus] = useState({
    state: "warning",
    message: "Checking backend status..."
  });
  const [messages, setMessages] = useState(initialMessages);
  const [prompt, setPrompt] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch("/api/status");
        if (!response.ok) {
          throw new Error("Unable to reach the backend.");
        }
        const data = await response.json();
        setModelName(data.model_name ?? "unknown");
        if (data.ready) {
          setBackendStatus({
            state: "ready",
            message: "Backend ready"
          });
        } else {
          setBackendStatus({
            state: "warning",
            message: data.error ?? "Backend initializing"
          });
        }
      } catch (error) {
        setBackendStatus({
          state: "error",
          message: error.message
        });
        setModelName("unavailable");
      }
    };

    checkStatus();
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isSending]);

  const canSend = useMemo(() => prompt.trim().length > 0 && !isSending, [prompt, isSending]);

  const handleSend = async (event) => {
    event.preventDefault();
    if (!canSend) {
      return;
    }

    const nextMessage = prompt.trim();
    setPrompt("");
    setMessages((prev) => [...prev, { role: "user", content: nextMessage }]);
    setIsSending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: nextMessage })
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || "Unable to get a response.");
      }
      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry, I couldn't answer that. ${error.message}`
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncResult(null);
    try {
      const response = await fetch("/api/index", { method: "POST" });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || "Sync failed.");
      }
      const data = await response.json();
      setSyncResult({
        type: "success",
        message: data.message || `Indexed ${data.indexed ?? 0} files.`
      });
    } catch (error) {
      setSyncResult({
        type: "error",
        message: error.message
      });
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar__header">
          <h1>AI Notes Assistant</h1>
          <p>Keep your notes searchable with local LLM answers.</p>
        </div>
        <div className={`status ${statusVariants[backendStatus.state]}`}>
          <span className="status__dot" />
          <span>{backendStatus.message}</span>
        </div>
        <div className="card">
          <h2>Active Model</h2>
          <p className="mono">{modelName}</p>
        </div>
        <div className="card">
          <h2>Note Management</h2>
          <p>Sync the vector store and central index after adding new files.</p>
          <button className="primary" onClick={handleSync} disabled={isSyncing}>
            {isSyncing ? "Syncing..." : "Sync & Re-index Notes"}
          </button>
          {syncResult && (
            <div className={`sync-result ${syncResult.type}`}>
              {syncResult.message}
            </div>
          )}
        </div>
        <div className="card tips">
          <h2>Tips</h2>
          <ul>
            <li>Drop new notes into the /notes folder.</li>
            <li>Ask a question and the assistant will search your notes.</li>
          </ul>
        </div>
      </aside>

      <main className="chat">
        <header className="chat__header">
          <div>
            <h2>Chat</h2>
            <p>Ask anything about your notes collection.</p>
          </div>
        </header>
        <section className="chat__messages">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <div className="message__meta">{message.role}</div>
              <div className="message__bubble">{message.content}</div>
            </div>
          ))}
          {isSending && (
            <div className="message assistant">
              <div className="message__meta">assistant</div>
              <div className="message__bubble">Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </section>
        <form className="chat__input" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Ask a question about your notes..."
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />
          <button type="submit" disabled={!canSend}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
