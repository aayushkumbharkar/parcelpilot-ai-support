import { Send } from 'lucide-react';
import { FormEvent, useEffect, useState } from 'react';
import { confirmAction, sendChat } from '../api';
import { ChatResponse, TokenKey } from '../types';
import { ConfirmationModal } from './ConfirmationModal';
import { SourceBadge } from './SourceBadge';
import { ToolCallTrace } from './ToolCallTrace';

type Message = { role: 'user' | 'assistant'; text: string; response?: ChatResponse };

export function ChatWindow({ token, draftQuery }: { token: TokenKey; draftQuery: string }) {
  const [input, setInput] = useState('Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.');
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingAction, setPendingAction] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (draftQuery) setInput(draftQuery);
  }, [draftQuery]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text) return;
    setMessages((current) => [...current, { role: 'user', text }]);
    setInput('');
    setBusy(true);
    try {
      const response = await sendChat(token, text);
      setPendingAction(response.pending_action);
      setMessages((current) => [...current, { role: 'assistant', text: response.answer, response }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: error instanceof Error ? error.message : 'Request failed' }]);
    } finally {
      setBusy(false);
    }
  }

  async function answerConfirmation(confirmed: boolean) {
    if (!pendingAction) return;
    const result = await confirmAction(token, pendingAction, confirmed);
    setPendingAction(null);
    setMessages((current) => [
      ...current,
      { role: 'assistant', text: result.executed ? `Action executed: ${result.action_type}` : 'Action cancelled.' }
    ]);
  }

  return (
    <main className="flex min-w-0 flex-1 flex-col">
      {pendingAction ? (
        <ConfirmationModal draft={pendingAction} onConfirm={() => answerConfirmation(true)} onCancel={() => answerConfirmation(false)} />
      ) : null}
      <div className="flex-1 overflow-auto p-4">
        <div className="mx-auto grid max-w-4xl gap-3">
          {messages.map((message, index) => (
            <article
              key={index}
              className={`rounded border p-3 ${message.role === 'user' ? 'ml-auto max-w-2xl border-slate-300 bg-white' : 'border-slate-200 bg-slate-50'}`}
            >
              <p className="whitespace-pre-wrap text-sm leading-6">{message.text}</p>
              {message.response ? (
                <>
                  <ToolCallTrace steps={message.response.tool_trace} />
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.response.sources.map((source) => (
                      <SourceBadge key={source.source_file + source.page_number} source={source} />
                    ))}
                  </div>
                </>
              ) : null}
            </article>
          ))}
        </div>
      </div>
      <form className="border-t border-slate-200 bg-white p-3" onSubmit={submit}>
        <div className="mx-auto flex max-w-4xl gap-2">
          <textarea
            className="min-h-12 flex-1 resize-none rounded border border-slate-300 px-3 py-2 text-sm"
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button className="grid h-12 w-12 place-items-center rounded bg-slate-900 text-white disabled:bg-slate-400" disabled={busy} title="Send">
            <Send size={18} />
          </button>
        </div>
      </form>
    </main>
  );
}
