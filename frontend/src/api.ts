import type {
  CompetitiveReport,
  ReportSummaryItem,
  SystemStatus,
} from './types';

const API_BASE = '/api';

export async function checkSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error('فشل التحقق من حالة الخادم');
  return res.json();
}

export async function analyzeByUrl(payload: {
  url: string;
  geographic_scope?: string;
  extra_context?: string;
  tavily_api_key?: string;
  llm_api_key?: string;
}): Promise<CompetitiveReport> {
  const res = await fetch(`${API_BASE}/analyze/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'فشل في تحليل الموقع عبر الرابط');
  }
  return res.json();
}

export async function analyzeByText(payload: {
  content: string;
  company_name?: string;
  website_url?: string;
  geographic_scope?: string;
  tavily_api_key?: string;
  llm_api_key?: string;
}): Promise<CompetitiveReport> {
  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'فشل في تحليل المحتوى المدخل');
  }
  return res.json();
}

export async function fetchReports(): Promise<ReportSummaryItem[]> {
  const res = await fetch(`${API_BASE}/reports`);
  if (!res.ok) throw new Error('فشل جلب قائمة التقارير');
  return res.json();
}

export async function fetchReportById(id: string): Promise<CompetitiveReport> {
  const res = await fetch(`${API_BASE}/reports/${id}`);
  if (!res.ok) throw new Error('فشل جلب بيانات التقرير');
  return res.json();
}

export async function deleteReportById(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/reports/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('فشل حذف التقرير');
}

export interface TestKeysResult {
  llm_valid: boolean;
  llm_message: string;
  tavily_valid?: boolean;
  tavily_message?: string;
  selected_model: string;
}

export async function testApiKeys(payload: {
  llm_api_key?: string;
  selected_model?: string;
  tavily_api_key?: string;
}): Promise<TestKeysResult> {
  const res = await fetch(`${API_BASE}/test-keys`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'فشل فحص مفاتيح الـ API');
  }
  return res.json();
}

export function getHtmlExportUrl(id: string): string {
  return `${API_BASE}/reports/${id}/html`;
}

export function getPdfExportUrl(id: string): string {
  return `${API_BASE}/reports/${id}/pdf`;
}
