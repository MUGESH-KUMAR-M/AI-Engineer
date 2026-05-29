import { AlertCircle, Bot, User } from 'lucide-react';
import SourceChips from './SourceChips';

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function MessageBubble({ message }) {
  const { role, content, sources, timestamp, isError, isSystem } = message;
  const isUser = role === 'user';
  const paragraphs = content.split('\n').filter((p) => p.trim() !== '');

  if (isError) {
    return (
      <div className="message-row assistant">
        <div className="message-avatar error">
          <AlertCircle size={18} />
        </div>
        <div className="message-content-wrapper">
          <div className="error-bubble">
            <AlertCircle size={18} />
            <span>{content}</span>
          </div>
        </div>
      </div>
    );
  }

  if (isSystem) {
    return (
      <div className="message-row assistant system-row">
        <div className="message-content-wrapper system-wrapper">
          <div className="system-bubble">{content}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`message-row ${role}`}>
      <div className="message-avatar">
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      <div className="message-content-wrapper">
        <div className={`message-bubble ${role}`}>
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>
        {!isUser && sources?.length > 0 && <SourceChips sources={sources} />}
        <div className="message-time">{formatTime(timestamp)}</div>
      </div>
    </div>
  );
}
