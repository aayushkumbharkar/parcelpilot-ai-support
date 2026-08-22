import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './main.css';
import { AuthSwitch } from './components/AuthSwitch';
import { ChatWindow } from './components/ChatWindow';
import { IssueRadar } from './components/IssueRadar';
import { TokenKey } from './types';

function App() {
  const [token, setToken] = useState<TokenKey>('customer_northstar');
  const [draftQuery, setDraftQuery] = useState('');

  return (
    <div className="flex h-full flex-col">
      <header className="flex min-h-14 items-center justify-between border-b border-slate-200 bg-white px-4">
        <h1 className="text-base font-semibold text-slate-950">ParcelPilot Support</h1>
        <AuthSwitch token={token} onChange={setToken} />
      </header>
      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <ChatWindow token={token} draftQuery={draftQuery} />
        <IssueRadar token={token} onInvestigate={setDraftQuery} />
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
