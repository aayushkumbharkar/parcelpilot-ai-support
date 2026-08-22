export type TokenKey = 'customer_northstar' | 'customer_lumenworks' | 'internal_support' | 'internal_ops';

export type ToolStep = {
  tool: string;
  status: string;
  result_summary: string;
};

export type Source = {
  source_file: string;
  source_type: string;
  page_number: number;
  authority_rank: number;
};

export type ChatResponse = {
  answer: string;
  tool_trace: ToolStep[];
  sources: Source[];
  conflict_report: { has_conflicts: boolean; conflicts: unknown[] } | null;
  pending_action: Record<string, unknown> | null;
  escalation_required: boolean;
};

export type IssueSignal = {
  signal_type: string;
  affected_accounts: string[];
  ticket_ids: string[];
  urgency_score: number;
  query: string;
};
