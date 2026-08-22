import { ChatResponse, IssueSignal, TokenKey } from './types';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8010';

const headers = (token: TokenKey) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`
});

export async function sendChat(token: TokenKey, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ message })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function loadIssues(token: TokenKey): Promise<IssueSignal[]> {
  const response = await fetch(`${API_URL}/issues`, { headers: headers(token) });
  if (!response.ok) return [];
  const data = await response.json();
  return data.signals;
}

export async function confirmAction(token: TokenKey, draft: Record<string, unknown>, confirmed: boolean) {
  const response = await fetch(`${API_URL}/confirm`, {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ draft, confirmed })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
