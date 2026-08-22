import { CheckCircle2, Wrench } from 'lucide-react';
import { ToolStep } from '../types';

export function ToolCallTrace({ steps }: { steps: ToolStep[] }) {
  if (!steps.length) return null;
  return (
    <ol className="mt-3 grid gap-2 border-l border-slate-200 pl-3">
      {steps.map((step, index) => (
        <li key={`${step.tool}-${index}`} className="flex min-h-8 items-center gap-2 text-xs text-slate-600">
          {step.status === 'done' ? <CheckCircle2 size={15} className="text-emerald-600" /> : <Wrench size={15} />}
          <span className="font-medium text-slate-800">{step.tool}</span>
          <span className="truncate">{step.result_summary}</span>
        </li>
      ))}
    </ol>
  );
}
