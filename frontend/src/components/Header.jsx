export default function Header() {
  return (
    <header className="header">
      <div className="header-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
        </svg>
      </div>
      <div className="header-text">
        <div className="header-title">SWS AI Assistant</div>
        <div className="header-subtitle">Company Policy Chatbot</div>
      </div>
      <div className="header-status">
        <div className="header-status-dot" />
        <span className="header-status-text">Online</span>
      </div>
    </header>
  );
}
