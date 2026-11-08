
import { useState } from "react";
import "./App.css";

// Convert the API's plain-text response into readable sections.
function formatResponse(text) {
  if (!text) return [];

  const cleanedText = text
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/\\n/g, "\n")
    .replace(/\\"/g, '"');

  return cleanedText
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

// Render bold text safely without using HTML injection.
function renderInlineText(text) {
  return text.split(/(\*\*.*?\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    return part;
  });
}

function FormattedResponse({ text }) {
  const lines = formatResponse(text);

  return (
    <div className="formatted-response">
      {lines.map((line, index) => {
        const cleanLine = line.replace(/^[-•]\s*/, "");
        const isBullet = /^[-•]\s*/.test(line);

        const isHeading =
          /^(Root causes|Immediate countermeasures|Permanent countermeasures|Impact|Equipment|Devices|Location|Summary|Details|Incident:|Date and time:)/i.test(
            line
          );

        if (isBullet) {
          return (
            <div className="response-bullet" key={index}>
              <span className="bullet-point">•</span>
              <span>{renderInlineText(cleanLine)}</span>
            </div>
          );
        }

        if (isHeading) {
          return (
            <p className="response-heading" key={index}>
              {renderInlineText(line)}
            </p>
          );
        }

        return (
          <p className="response-paragraph" key={index}>
            {renderInlineText(line)}
          </p>
        );
      })}
    </div>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", text: userQuestion },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userQuestion }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          status: data.status,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: error.message || "Unable to connect to the backend. Please check whether the API server is running.",
          status: "error",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>GraphRAG</h2>
        <p className="subtitle">Enterprise Knowledge System</p>

        <button
          className="new-chat"
          onClick={() => setMessages([])}
        >
          + New Chat
        </button>

        <div className="sidebar-info">
          <h4>Knowledge Assistant</h4>
          <p>
            Ask questions about manufacturing incidents, equipment and failure causes.
          </p>
        </div>

        <div className="sidebar-footer">
          Powered by GraphRAG
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h3>Enterprise Knowledge Assistant</h3>
            <p>Manufacturing Intelligence</p>
          </div>

          <span className="status">● Assistant</span>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <h1>Welcome to GraphRAG</h1>
              <p>
                Your enterprise knowledge assistant. Ask a question
                about incidents, equipment or manufacturing failures.
              </p>

              <div className="suggestions">
                <button
                  onClick={() =>
                    setQuestion("Show details for incident INC001")
                  }
                >
                  Incident details
                </button>

                <button
                  onClick={() =>
                    setQuestion("Show incidents for Hydraulic Press #3")
                  }
                >
                  Equipment history
                </button>

                <button
                  onClick={() =>
                    setQuestion("What are the common causes for Hydraulic Press #3?")
                  }
                >
                  Common failure causes
                </button>
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.role}`}
                >
                  <div className="message-label">
                    {message.role === "user"
                      ? "You"
                      : "GraphRAG Assistant"}
                  </div>

                  <div className="message-content">
                    {message.role === "assistant" ? (
                      <FormattedResponse text={message.text} />
                    ) : (
                      message.text
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message assistant">
                  <div className="message-label">
                    GraphRAG Assistant
                  </div>
                  <div className="message-content">
                    Searching enterprise knowledge...
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <div className="input-area">
          <div className="input-box">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask about incidents, equipment or failure causes..."
              rows="2"
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={loading || !question.trim()}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>

          <p className="disclaimer">
            Responses are based on available enterprise knowledge graph data.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
