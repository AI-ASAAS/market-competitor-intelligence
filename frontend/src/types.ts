export interface ServiceItem {
  name: string;
  description: string;
  features: string[];
  pricing_hint?: string;
}

export interface PricingItem {
  plan_name: string;
  price: string;
  billing_cycle?: string;
  features: string[];
}

export interface ContentAnalysis {
  company_name: string;
  website_url?: string;
  industry: string;
  services: ServiceItem[];
  target_audience: string;
  marketing_message: string;
  pricing?: PricingItem[];
  geographic_scope: string;
  unique_selling_points: string[];
  content_quality_score: number;
  detected_tech_keywords: string[];
}

export interface CompetitorProfile {
  name: string;
  website: string;
  industry: string;
  services: string[];
  pricing_summary: string;
  target_audience: string;
  marketing_message: string;
  strengths: string[];
  weaknesses: string[];
  market_position: string;
  online_presence_score: number;
}

export interface ComparisonRow {
  dimension: string;
  target_company: string;
  competitor_1: string;
  competitor_2: string;
  competitor_3: string;
  strategic_verdict: string;
}

export interface ComparisonTable {
  dimensions: ComparisonRow[];
}

export interface SWOTAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface GapItem {
  category: "خدمية" | "تسويقية" | "سعرية / نموذج عمل" | "تقنية وتجربة مستخدم";
  title: string;
  description: string;
  impact_level: "عالي" | "متوسط" | "منخفض";
  action_to_close: string;
}

export interface RecommendationItem {
  priority: "عاجل" | "مهم" | "تحسين استراتيجي";
  title: string;
  impact: string;
  effort: "منخفض" | "متوسط" | "عالي";
  action_steps: string[];
}

export interface CompetitiveReport {
  id: string;
  created_at: string;
  executive_summary: string;
  overall_score: number;
  target_analysis: ContentAnalysis;
  competitors: CompetitorProfile[];
  comparison_table: ComparisonTable;
  swot: SWOTAnalysis;
  gap_analysis: GapItem[];
  recommendations: RecommendationItem[];
}

export interface ReportSummaryItem {
  id: string;
  company_name: string;
  url?: string;
  industry: string;
  geographic_scope: string;
  overall_score: number;
  competitors_names: string[];
  created_at: string;
}

export interface SystemStatus {
  app_name: string;
  version: string;
  tavily_configured: boolean;
  openrouter_configured: boolean;
  gemini_configured: boolean;
  default_region: string;
  default_llm_model: string;
}
