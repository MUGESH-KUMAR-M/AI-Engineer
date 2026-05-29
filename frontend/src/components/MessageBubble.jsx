import SourceChips from './SourceChips';

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// User avatar icon
function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

// Assistant avatar icon (sparkle / star)
function AssistantIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
    </svg>
  );
}

export default function MessageBubble({ message }) {
  const { role, content, sources, timestamp } = message;
  const isUser = role === 'user';

  // Split content into paragraphs for nicer rendering
  const paragraphs = content.split('\n').filter((p) => p.trim() !== '');

  return (
    <div className={`message-row ${role}`}>
      <div className="message-avatar">
        {isUser ? <UserIcon /> : <AssistantIcon />}
      </div>
      <div className="message-content-wrapper">
        <div className={`message-bubble ${role}`}>
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>
        {!isUser && sources && <SourceChips sources={sources} />}
        <div className="message-time">{formatTime(timestamp)}</div>
      </div>
    </div>
  );
}
