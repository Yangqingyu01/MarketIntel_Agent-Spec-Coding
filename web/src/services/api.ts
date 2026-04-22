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
};

export type AnalyzeResponse = {
  task_id: string;
  report: {
    report_id: string;
    report_type: string;
    target: string;
    executive_summary: string;
    changes_summary: string;
    chart_data: Array<Record<string, unknown>>;
    recommended_actions: Array<Record<string, unknown>>;
  };
  alerts: AlertItem[];
  intel_count: number;
};

const API_BASE = "/api";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
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

