import { useRef, useEffect } from 'react';
import {
  Calendar,
  Home,
  LogOut,
  Shield,
  Sparkles,
  Stethoscope,
} from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

const SUGGESTIONS = [
  {
    icon: Calendar,
    text: 'What is the annual leave policy at SWS AI?',
  },
  {
    icon: Stethoscope,
    text: 'How many days of sick leave do employees get?',
  },
  {
    icon: LogOut,
    text: 'What is the notice period for resignation?',
  },
  {
    icon: Shield,
    text: 'What is the password policy for company systems?',
  },
  {
    icon: Home,
    text: 'What are the WFH guidelines?',
  },
  {
    icon: Sparkles,
    text: 'Does SWS AI offer health insurance?',
  },
];

function WelcomeScreen({ onSuggestionClick }) {
  return (
    <div className="welcome-container">
      <div className="welcome-icon">
        <Sparkles size={40} strokeWidth={1.75} />
      </div>
      <h1 className="welcome-title">How can I help you today?</h1>
      <p className="welcome-subtitle">
        Ask anything about HR, leave, IT security, benefits, or workplace policies.
        Every answer is retrieved from your company documents — no hallucinations.
      </p>
      <div className="welcome-suggestions">
        {SUGGESTIONS.map((s, i) => {
          const Icon = s.icon;
          return (
            <button
              key={i}
              type="button"
              className="welcome-suggestion"
              onClick={() => onSuggestionClick(s.text)}
            >
              <div className="welcome-suggestion-icon">
                <Icon size={14} />
              </div>
              <span className="welcome-suggestion-text">{s.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading, loadingStage, onSuggestionClick }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, loadingStage]);

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-window">
      <div className="chat-window-inner">
        {isEmpty && !isLoading ? (
          <WelcomeScreen onSuggestionClick={onSuggestionClick} />
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble key={`${msg.timestamp}-${i}`} message={msg} />
            ))}
            {isLoading && <TypingIndicator stage={loadingStage} />}
          </>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
