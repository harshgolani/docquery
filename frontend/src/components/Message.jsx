import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Message({ message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const { role, content, sources } = message;

  if (role === "user") {
    return (
      <div className="message message-user">
        <div className="message-bubble bubble-user">{content}</div>
      </div>
    );
  }

  return (
    <div className="message message-assistant">
      <div className="message-bubble bubble-assistant">
        <div className="message-text">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
        {sources && sources.length > 0 && (
          <div className="sources">
            <button
              className="sources-toggle"
              onClick={() => setSourcesOpen((o) => !o)}
            >
              {sourcesOpen ? "▼" : "▶"} Sources ({sources.length})
            </button>
            {sourcesOpen && (
              <div className="sources-list">
                {sources.map((s, i) => (
                  <div key={i} className="source-chunk">
                    {s}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
