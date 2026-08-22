import { FileText } from 'lucide-react';
import { Source } from '../types';

export function SourceBadge({ source }: { source: Source }) {
  return (
    <span className="inline-flex max-w-full items-center gap-1 rounded border border-slate-300 bg-white px-2 py-1 text-xs text-slate-700">
      <FileText size={13} aria-hidden="true" />
      <span className="truncate">
        {source.source_file} p.{source.page_number}
      </span>
      <span className="shrink-0 text-slate-500">{source.source_type}</span>
    </span>
  );
}
