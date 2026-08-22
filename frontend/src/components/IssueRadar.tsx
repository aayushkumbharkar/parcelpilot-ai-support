import { RefreshCcw, Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { loadIssues } from '../api';
import { IssueSignal, TokenKey } from '../types';

export function IssueRadar({ token, onInvestigate }: { token: TokenKey; onInvestigate: (query: string) => void }) {
  const [signals, setSignals] = useState<IssueSignal[]>([]);

  const refresh = () => {
    loadIssues(token).then(setSignals).catch(() => setSignals([]));
  };

  useEffect(refresh, [token]);

  if (!token.startsWith('internal')) return null;

  return (
    <aside className="w-full border-l border-slate-200 bg-white p-4 lg:w-96">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Issue radar</h2>
        <button className="grid h-8 w-8 place-items-center rounded border border-slate-300" onClick={refresh} title="Refresh">
          <RefreshCcw size={16} />
        </button>
      </div>
      <div className="mt-3 grid gap-3">
        {signals.map((signal) => (
          <article key={`${signal.signal_type}-${signal.ticket_ids.join('-')}`} className="rounded border border-slate-200 p-3">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900">{signal.signal_type.replace(/_/g, ' ')}</h3>
              <span className="text-sm font-semibold text-rose-700">{signal.urgency_score}</span>
            </div>
            <p className="mt-1 text-xs text-slate-600">{signal.affected_accounts.join(', ')}</p>
            <p className="mt-1 text-xs text-slate-500">{signal.ticket_ids.join(', ')}</p>
            <button
              className="mt-3 inline-flex h-8 items-center gap-1 rounded border border-slate-300 px-2 text-xs"
              onClick={() => onInvestigate(signal.query)}
            >
              <Search size={14} /> Investigate
            </button>
          </article>
        ))}
      </div>
    </aside>
  );
}

