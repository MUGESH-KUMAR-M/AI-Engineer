import { FileText } from 'lucide-react';

function formatFilename(filename) {
  return filename
    .replace(/\.pdf$/i, '')
    .replace(/^SWS-AI-/i, '')
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function SourceChips({ sources }) {
  if (!sources?.length) return null;

  return (
    <div className="source-chips">
      <div className="source-chips-label">
        <FileText size={12} />
        Sources
      </div>
      {sources.map((source, index) => (
        <span className="source-chip" key={`${source.filename}-${source.page}-${index}`}>
          <FileText size={12} />
          {formatFilename(source.filename)}
          {source.page != null && (
            <span className="source-chip-page">p.{source.page}</span>
          )}
        </span>
      ))}
    </div>
  );
}
