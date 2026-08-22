import { Shield } from 'lucide-react';
import { TokenKey } from '../types';

const OPTIONS: { value: TokenKey; label: string }[] = [
  { value: 'customer_northstar', label: 'Northstar customer' },
  { value: 'customer_lumenworks', label: 'LumenWorks customer' },
  { value: 'internal_support', label: 'Support agent' },
  { value: 'internal_ops', label: 'Ops manager' }
];

export function AuthSwitch({ token, onChange }: { token: TokenKey; onChange: (token: TokenKey) => void }) {
  return (
    <label className="flex items-center gap-2 text-sm text-slate-700">
      <Shield size={17} aria-hidden="true" />
      <select
        className="h-9 rounded border border-slate-300 bg-white px-2"
        value={token}
        onChange={(event) => onChange(event.target.value as TokenKey)}
      >
        {OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
