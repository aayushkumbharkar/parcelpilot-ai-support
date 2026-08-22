import { Check, X } from 'lucide-react';

export function ConfirmationModal({
  draft,
  onConfirm,
  onCancel
}: {
  draft: Record<string, unknown>;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4">
      <section className="w-full max-w-lg rounded border border-slate-300 bg-white p-4 shadow-xl">
        <h2 className="text-base font-semibold text-slate-900">Confirm action</h2>
        <pre className="mt-3 max-h-64 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-100">
          {JSON.stringify(draft, null, 2)}
        </pre>
        <div className="mt-4 flex justify-end gap-2">
          <button className="inline-flex h-9 items-center gap-1 rounded border border-slate-300 px-3" onClick={onCancel}>
            <X size={16} /> No
          </button>
          <button className="inline-flex h-9 items-center gap-1 rounded bg-slate-900 px-3 text-white" onClick={onConfirm}>
            <Check size={16} /> Yes
          </button>
        </div>
      </section>
    </div>
  );
}
