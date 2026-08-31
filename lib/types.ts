export type LeadStatus =
  | 'new'
  | 'contacted'
  | 'engaged'
  | 'disqualified'
  | 'ready_to_close'
  | 'closed_won'
  | 'closed_lost'
  | 'human_handoff';

export type LeadSource =
  | 'hunting'
  | 'linkedin_organic'
  | 'paid_ad'
  | 'seo'
  | 'referral'
  | 'inbound_form'
  | 'manual_import'
  | 'marketplace';

export interface Lead {
  id: string;
  company_id?: string | null;
  contact_id?: string | null;
  source: LeadSource;
  status: LeadStatus;
  fit_score: number;
  lead_score: number;
  outreach_count: number;
  created_at: string;
  last_activity_date?: string | null;
}

export interface LeadListResponse {
  leads: Lead[];
  total: number;
  page: number;
  page_size: number;
}

export type ApprovalStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'expired'
  | 'executing'
  | 'completed'
  | 'failed'
  | 'rolled_back';

export type ApprovalCategory =
  | 'agent_behavior'
  | 'bug_fix'
  | 'typo'
  | 'ui_ux'
  | 'css'
  | 'system_config'
  | 'outreach'
  | 'marketing'
  | 'other';

export interface Approval {
  id: string;
  category: ApprovalCategory;
  title: string;
  description: string;
  proposed_fix: string;
  affected_system?: string | null;
  risk_level: string;
  status: ApprovalStatus;
  created_at: string;
  resolved_at?: string | null;
}

export interface ApprovalListResponse {
  approvals: Approval[];
  total: number;
  page: number;
  page_size: number;
}

export type AgentType =
  | 'hunting'
  | 'enrichment'
  | 'outreach'
  | 'content'
  | 'social_media'
  | 'seo'
  | 'paid_traffic'
  | 'engagement'
  | 'inbound_lead'
  | 'supervisor'
  | 'optimization'
  | 'marketplace';

export type AgentStatus = 'active' | 'idle' | 'paused' | 'failed' | 'maintenance';

export interface Agent {
  id: string;
  name: string;
  agent_type: AgentType;
  status: AgentStatus;
  health_score: number;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  last_run_at?: string | null;
  created_at: string;
}

export interface AgentHealthScore {
  agent_id: string;
  agent_name: string;
  availability: number;
  execution_success: number;
  task_completion: number;
  latency: number;
  error_rate: number;
  output_quality: number;
  cost_efficiency: number;
  policy_compliance: number;
  overall_score: number;
}

export interface AgentRun {
  id: string;
  agent_id: string;
  status: string;
  input_data?: Record<string, unknown> | null;
  output_data?: Record<string, unknown> | null;
  error_message?: string | null;
  tokens_used: number;
  cost: number;
  duration_ms?: number | null;
  started_at: string;
  completed_at?: string | null;
}

export interface DashboardOverview {
  leads: {
    total: number;
    contacted: number;
    engaged: number;
    ready_to_close: number;
    won: number;
    lost: number;
    human_handoffs: number;
  };
  agents: {
    active: number;
    failed: number;
  };
  approvals: {
    pending: number;
  };
  notifications: {
    unread: number;
  };
}

export interface Activity {
  id: string;
  lead_id: string;
  agent_name: string;
  action_type: string;
  channel?: string;
  summary?: string;
  created_at: string;
}
