export type AnalyzeRequest = {
  targets: string[];
  dimensions: string[];
  time_range?: string;
};

export type AlertItem = {
  alert_id: string;
  severity: string;
  company: string;
  title: string;
  description: string;
  detected_at: string;
  source_url?: string;
};

export type AuthUser = {
  user_id: string;
  email: string;
  full_name: string;
  organization_id: string;
  organization_name: string;
  role: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type AnalyzeResponse = {
  task_id: string;
  report: {
    report_id: string;
    report_type: string;
    target: string;
    executive_summary: string;
    changes_summary: string;
    data_quality_note: string;
    chart_data: Array<Record<string, unknown>>;
    recommended_actions: Array<Record<string, unknown>>;
  };
  alerts: AlertItem[];
  intel_count: number;
};

export type SchedulerStatusResponse = {
  scheduler: {
    enabled: boolean;
    jobs: Array<{ id: string; name: string; trigger: string }>;
  };
  competitor_count: number;
  frequency_counts: Record<string, number>;
};

export type SchedulerSummaryResponse = {
  summary: {
    summary_type: string;
    report_count: number;
    alert_count: number;
    headline: string;
    reports: Array<Record<string, unknown>>;
    alerts: Array<Record<string, unknown>>;
  };
};

export type FeishuStatusResponse = {
  configured: boolean;
  delivery_mode: string;
  app_id_configured: boolean;
  app_secret_configured: boolean;
  target_chat_configured: boolean;
  target_chat_masked: string;
  webhook_endpoint: string;
  preview_delivery: {
    ok: boolean;
    delivery_mode: string;
    chat_id: string;
  };
  sample_card: Record<string, unknown>;
};

export type HistoryResponse = {
  history: {
    company: string;
    snapshots: Array<{
      snapshot_id: string;
      snapshot_date: string;
      source_count: number;
      overall_confidence: number;
      dimensions: string[];
      items: Array<{
        dimension: string;
        extracted_data: string;
        evidence_quote: string;
        source_url: string;
        source_name: string;
        publish_date: string;
        crawl_date: string;
        credibility: number;
      }>;
    }>;
    timeline: Array<{
      snapshot_id: string;
      snapshot_date: string;
      source_count: number;
      product_count: number;
      pricing_count: number;
    }>;
    comparisons: Array<{
      snapshot_id: string;
      snapshot_date: string;
      product: { count: number; delta: number; highlights: string[]; removed: string[] };
      pricing: { count: number; delta: number; highlights: string[]; removed: string[] };
    }>;
    alerts: AlertItem[];
  };
};

export type HistoryOverviewResponse = {
  overview: {
    companies: string[];
    rows: Array<{
      company: string;
      snapshot_id: string;
      snapshot_date: string;
      product_count: number;
      pricing_count: number;
      source_count: number;
    }>;
  };
};

const API_BASE = "/api";
const AUTH_TOKEN_KEY = "marketintel.auth.token";

type RequestJsonOptions = RequestInit & {
  skipAuth?: boolean;
};

export function getStoredAuthToken(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.localStorage.getItem(AUTH_TOKEN_KEY) || "";
}

export function setStoredAuthToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearStoredAuthToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}

async function requestJson<T>(path: string, init?: RequestJsonOptions): Promise<T> {
  const headers = new Headers(init?.headers || {});
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (!init?.skipAuth) {
    const token = getStoredAuthToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function registerAccount(payload: {
  organization_name: string;
  full_name: string;
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return requestJson<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
    skipAuth: true,
  });
}

export function loginAccount(payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return requestJson<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
    skipAuth: true,
  });
}

export function fetchCurrentUser(): Promise<{ user: AuthUser }> {
  return requestJson<{ user: AuthUser }>("/auth/me");
}

export function analyzeCompetitors(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  return requestJson<AnalyzeResponse>("/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchAlerts(): Promise<{ alerts: AlertItem[] }> {
  return requestJson<{ alerts: AlertItem[] }>("/alerts");
}

export function fetchCompetitors(): Promise<{ competitors: Array<Record<string, unknown>> }> {
  return requestJson<{ competitors: Array<Record<string, unknown>> }>("/config/competitors");
}

export function saveCompetitor(payload: Record<string, unknown>): Promise<{ ok: boolean }> {
  return requestJson<{ ok: boolean }>("/config/competitors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchSchedulerStatus(): Promise<SchedulerStatusResponse> {
  return requestJson<SchedulerStatusResponse>("/scheduler/status");
}

export function fetchSchedulerSummary(
  frequency: "daily" | "weekly",
): Promise<SchedulerSummaryResponse> {
  return requestJson<SchedulerSummaryResponse>(`/scheduler/summary?frequency=${frequency}`);
}

export function fetchFeishuStatus(): Promise<FeishuStatusResponse> {
  return requestJson<FeishuStatusResponse>("/feishu/status");
}

export function fetchCompanyHistory(company: string): Promise<HistoryResponse> {
  return requestJson<HistoryResponse>(`/history?company=${encodeURIComponent(company)}`);
}

export function fetchHistoryOverview(companies: string[]): Promise<HistoryOverviewResponse> {
  const query = companies.length > 0 ? `?companies=${encodeURIComponent(companies.join(","))}` : "";
  return requestJson<HistoryOverviewResponse>(`/history/overview${query}`);
}
