import { Loader2, Search, Sparkles } from 'lucide-react';

const STAGE_ICONS = {
  embed: Loader2,
  search: Search,
  generate: Sparkles,
};

export default function TypingIndicator({ stage = 'search' }) {
  const labels = {
    embed: 'Understanding your question…',
    search: 'Searching company documents…',
    generate: 'Generating grounded answer…',
  };

  const StageIcon = STAGE_ICONS[stage] || Search;
  const spinning = stage === 'embed';

  return (
    <div className="typing-indicator-row">
      <div className="message-avatar">
        <Sparkles size={18} />
      </div>
      <div className="typing-indicator">
        <StageIcon
          size={16}
          className={`typing-stage-icon ${spinning ? 'spin' : 'pulse'}`}
        />
        <span className="typing-label">{labels[stage] || labels.search}</span>
        <div className="typing-dots">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </div>
    </div>
  );
}
