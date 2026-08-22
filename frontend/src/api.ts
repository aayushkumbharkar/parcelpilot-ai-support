import { ChatResponse, IssueSignal, TokenKey } from './types';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8010';
const MONEY = String.fromCharCode(36);

type Draft = Record<string, unknown>;

const headers = (token: TokenKey) => ({
  'Content-Type': 'application/json',
  Authorization: 'Bearer ' + token
});

function shouldUseBrowserMock() {
  if (typeof window === 'undefined') return false;
  const host = window.location.hostname;
  const localPage = host === 'localhost' || host === '127.0.0.1';
  const localApi = API_URL.includes('localhost') || API_URL.includes('127.0.0.1');
  return !localPage && localApi;
}

function source(source_file: string, source_type: string, page_number: number, authority_rank = 100) {
  return { source_file, source_type, page_number, authority_rank };
}

function trace(tool: string, result_summary: string, status = 'done') {
  return { tool, status, result_summary };
}

function mockChat(token: TokenKey, message: string): ChatResponse {
  const text = message.toLowerCase();
  if (text.includes('escalat')) {
    return {
      answer: 'Escalation draft ready. Please confirm before I execute it.',
      tool_trace: [trace('structured_lookup', 'TCK-9001 selected'), trace('escalation_tool', 'Draft escalation ready', 'pending')],
      sources: [],
      conflict_report: null,
      pending_action: {
        requires_confirmation: true,
        awaiting_confirmation: true,
        action_type: 'create_escalation',
        payload: { ticket_id: 'TCK-9001', account_id: 'northstar', priority: 'high' }
      },
      escalation_required: false
    };
  }
  if (text.includes('credit') || text.includes('late') || text.includes('pickup')) {
    return {
      answer: 'Yes. ORD-1002 is eligible because pickup is 3 hours late due to carrier fault. Credit: ' + MONEY + '150.00 using subtotal * 15%. Source: 05_Northstar_Logistics_Enterprise_Agreement.pdf page 13.',
      tool_trace: [
        trace('structured_lookup', 'ORD-1002 active late pickup'),
        trace('document_search', 'Service credit terms retrieved'),
        trace('calculator', 'Eligibility True'),
        trace('calculator', 'Credit ' + MONEY + '150.00')
      ],
      sources: [source('05_Northstar_Logistics_Enterprise_Agreement.pdf', 'customer_agreement', 13)],
      conflict_report: {
        has_conflicts: true,
        conflicts: [{ topic: 'service_credit', highest_authority_source: '05_Northstar_Logistics_Enterprise_Agreement.pdf' }]
      },
      pending_action: null,
      escalation_required: false
    };
  }
  if (text.includes('ord-1001') || text.includes('cancel')) {
    return {
      answer: 'Northstar can cancel ORD-1001 without a cancellation fee. Fee: ' + MONEY + '0.00. 05_Northstar_Logistics_Enterprise_Agreement.pdf page 12 takes precedence over standard policy for this account.',
      tool_trace: [
        trace('structured_lookup', 'ORD-1001 found'),
        trace('document_search', 'Cancellation terms retrieved'),
        trace('calculator', 'Cancellation fee ' + MONEY + '0.00')
      ],
      sources: [source('05_Northstar_Logistics_Enterprise_Agreement.pdf', 'customer_agreement', 12)],
      conflict_report: {
        has_conflicts: true,
        conflicts: [{ topic: 'cancellation_fee', highest_authority_source: '05_Northstar_Logistics_Enterprise_Agreement.pdf' }]
      },
      pending_action: null,
      escalation_required: false
    };
  }
  return {
    answer: "I'm not confident enough to answer this reliably. I recommend escalating to the support team.",
    tool_trace: [],
    sources: [],
    conflict_report: null,
    pending_action: null,
    escalation_required: true
  };
}

function mockIssues(token: TokenKey): IssueSignal[] {
  if (!token.startsWith('internal')) return [];
  return [
    {
      signal_type: 'stale_high_priority',
      affected_accounts: ['northstar'],
      ticket_ids: ['TCK-9001'],
      urgency_score: 95,
      query: 'Investigate stale_high_priority for TCK-9001'
    },
    {
      signal_type: 'multi_customer_impact',
      affected_accounts: ['lumenworks', 'northstar'],
      ticket_ids: ['TCK-9001', 'TCK-9002'],
      urgency_score: 90,
      query: 'Investigate multi_customer_impact for TCK-9001, TCK-9002'
    }
  ];
}

export async function sendChat(token: TokenKey, message: string): Promise<ChatResponse> {
  if (shouldUseBrowserMock()) return mockChat(token, message);
  const response = await fetch(API_URL + '/chat', {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ message })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function loadIssues(token: TokenKey): Promise<IssueSignal[]> {
  if (shouldUseBrowserMock()) return mockIssues(token);
  const response = await fetch(API_URL + '/issues', { headers: headers(token) });
  if (!response.ok) return [];
  const data = await response.json();
  return data.signals;
}

export async function confirmAction(token: TokenKey, draft: Draft, confirmed: boolean) {
  if (shouldUseBrowserMock()) {
    return confirmed ? { executed: true, action_type: draft.action_type } : { executed: false, reason: 'cancelled' };
  }
  const response = await fetch(API_URL + '/confirm', {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ draft, confirmed })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
