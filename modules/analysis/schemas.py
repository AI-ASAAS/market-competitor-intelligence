from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


# ==========================================
# مدخلات التحليل (Analysis Inputs)
# ==========================================

class AnalyzeUrlRequest(BaseModel):
    url: str = Field(..., description="رابط الموقع الإلكتروني المراد تحليله")
    geographic_scope: Optional[str] = Field("السوق العربي", description="النطاق الجغرافي المستهدف للبحث")
    extra_context: Optional[str] = Field(None, description="أي سياق أو معلومات إضافية عن الشركة")
    tavily_api_key: Optional[str] = Field(None, description="مفتاح Tavily API اختياري من الواجهة")
    llm_api_key: Optional[str] = Field(None, description="مفتاح LLM اختياري من الواجهة")
    selected_model: Optional[str] = Field(None, description="النموذج المختار")


class AnalyzeTextRequest(BaseModel):
    content: str = Field(..., min_length=20, description="نص المحتوى المسحوب أو المدخل يدوياً")
    company_name: Optional[str] = Field(None, description="اسم الشركة أو المشروع إن وجد")
    website_url: Optional[str] = Field(None, description="رابط الموقع إن وجد")
    geographic_scope: Optional[str] = Field("السوق العربي", description="النطاق الجغرافي المستهدف")
    tavily_api_key: Optional[str] = Field(None, description="مفتاح Tavily API اختياري")
    llm_api_key: Optional[str] = Field(None, description="مفتاح LLM اختياري")
    selected_model: Optional[str] = Field(None, description="النموذج المختار")


# ==========================================
# مخرجات الوكيل ①: تحليل المحتوى (Content Analysis)
# ==========================================

class ServiceItem(BaseModel):
    name: str = Field(..., description="اسم الخدمة أو المنتج")
    description: str = Field(..., description="شرح الخدمة")
    features: List[str] = Field(default_factory=list, description="أهم ميزات الخدمة")
    pricing_hint: Optional[str] = Field(None, description="تلميح أو نطاق السعر إن وجد")


class PricingItem(BaseModel):
    plan_name: str = Field(..., description="اسم الباقة أو الخطة")
    price: str = Field(..., description="السعر (مثال: 199 ر.س / شهرياً)")
    billing_cycle: Optional[str] = Field("شهري / سنوي", description="دورة الفوترة")
    features: List[str] = Field(default_factory=list, description="الميزات المضمنة في الباقة")


class ContentAnalysis(BaseModel):
    company_name: str = Field(..., description="اسم الشركة أو الموقع المستخرج بدقة")
    website_url: Optional[str] = Field(None, description="رابط الموقع")
    industry: str = Field(..., description="المجال أو قطاع الأعمال الرئيسي")
    services: List[ServiceItem] = Field(default_factory=list, description="قائمة الخدمات والحلول المقدمة")
    target_audience: str = Field(..., description="الجمهور المستهدف وتوصيف الشريحة")
    marketing_message: str = Field(..., description="الرسالة التسويقية والقيمة المضافة (Value Proposition)")
    pricing: Optional[List[PricingItem]] = Field(None, description="تفاصيل الأسعار أو نموذج التسعير")
    geographic_scope: str = Field(..., description="النطاق الجغرافي للعمليات والخدمات")
    unique_selling_points: List[str] = Field(default_factory=list, description="نقاط البيع الفريدة (USPs)")
    content_quality_score: float = Field(8.5, ge=0.0, le=10.0, description="تقييم جودة ووضوح المحتوى من 10")
    detected_tech_keywords: List[str] = Field(default_factory=list, description="الكلمات المفتاحية والتقنية المكتشفة")


# ==========================================
# مخرجات الوكيل ②: ملف المنافس (Competitor Profile)
# ==========================================

class CompetitorProfile(BaseModel):
    name: str = Field(..., description="اسم المنافس")
    website: str = Field(..., description="رابط موقع المنافس")
    industry: str = Field(..., description="المجال")
    services: List[str] = Field(default_factory=list, description="أبرز الخدمات التي يقدمها")
    pricing_summary: str = Field(..., description="ملخص نموذج التسعير أو الأسعار المعروضة")
    target_audience: str = Field(..., description="الشريحة المستهدفة لدى المنافس")
    marketing_message: str = Field(..., description="رسالته التسويقية وموقعه الذهني")
    strengths: List[str] = Field(default_factory=list, description="أهم نقاط قوته")
    weaknesses: List[str] = Field(default_factory=list, description="أبرز نقاط ضعفه أو الفجوات لديه")
    market_position: str = Field(..., description="مكانته في السوق (رائد، منافس مباشر، مبتكر، اقتصادي)")
    online_presence_score: float = Field(..., ge=0.0, le=10.0, description="تقييم قوة تواجده الرقمي من 10")


# ==========================================
# مخرجات الوكيل ③: المقارنة والتحليل الاستراتيجي
# ==========================================

class ComparisonRow(BaseModel):
    dimension: str = Field(..., description="المحور المقارن (مثل: الخدمات، الجمهور، التسعير، التواجد الرقمي)")
    target_company: str = Field(..., description="وضع الموقع المحلل في هذا المحور")
    competitor_1: str = Field(..., description="وضع المنافس الأول")
    competitor_2: str = Field(..., description="وضع المنافس الثاني")
    competitor_3: str = Field(..., description="وضع المنافس الثالث")
    strategic_verdict: str = Field(..., description="الحكم الاستراتيجي والفرصة المتاحة")


class ComparisonTable(BaseModel):
    dimensions: List[ComparisonRow] = Field(default_factory=list)


class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list, description="نقاط القوة الداخلية للموقع المحلل")
    weaknesses: List[str] = Field(default_factory=list, description="نقاط الضعف الداخلية")
    opportunities: List[str] = Field(default_factory=list, description="الفرص الخارجية في السوق")
    threats: List[str] = Field(default_factory=list, description="التهديدات الخارجية من المنافسين")


class GapItem(BaseModel):
    category: str = Field(..., description="نوع الفجوة (خدمية، تسويقية، سعرية، تقنية)")
    title: str = Field(..., description="عنوان الفجوة")
    description: str = Field(..., description="شرح الفجوة وكيف يستغلها المنافسون")
    impact_level: str = Field("عالي", description="مستوى التأثير (عالي، متوسط، منخفض)")
    action_to_close: str = Field(..., description="الإجراء العملي لسد هذه الفجوة")


class RecommendationItem(BaseModel):
    priority: str = Field("مهم", description="مستوى الأولوية (عاجل، مهم، تحسين استراتيجي)")
    title: str = Field(..., description="عنوان التوصية")
    impact: str = Field(..., description="الأثر المتوقع على الحصة السوقية أو الإيرادات")
    effort: str = Field("متوسط", description="الجهد والموارد المطلوبة (منخفض، متوسط، عالي)")
    action_steps: List[str] = Field(default_factory=list, description="خطوات التنفيذ العملية")


# ==========================================
# التقرير التنافسي المتكامل (Full Competitive Report)
# ==========================================

class CompetitiveReport(BaseModel):
    id: str = Field(..., description="معرف التقرير الفريد")
    created_at: str = Field(..., description="تاريخ ووقت إعداد التقرير")
    executive_summary: str = Field(..., description="الملخص التنفيذي للتقرير التنافسي")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="التقييم التنافسي الشامل للموقع من 10")
    target_analysis: ContentAnalysis = Field(..., description="تحليل الموقع الأصلي")
    competitors: List[CompetitorProfile] = Field(..., min_length=1, max_length=5, description="قائمة المنافسين الـ 3")
    comparison_table: ComparisonTable = Field(..., description="جدول المقارنة متعدد الأبعاد")
    swot: SWOTAnalysis = Field(..., description="مصفوفة SWOT")
    gap_analysis: List[GapItem] = Field(default_factory=list, description="قائمة الفجوات التنافسية")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="التوصيات الاستراتيجية")


class ReportSummaryItem(BaseModel):
    id: str
    company_name: str
    url: Optional[str]
    industry: str
    geographic_scope: str
    overall_score: float
    competitors_names: List[str]
    created_at: str


class TestKeysRequest(BaseModel):
    llm_api_key: Optional[str] = Field(None, description="مفتاح OpenRouter المراد فحصه")
    selected_model: Optional[str] = Field(None, description="النموذج اللغوي المختار")
    tavily_api_key: Optional[str] = Field(None, description="مفتاح Tavily المراد فحصه إن وجد")


class TestKeysResponse(BaseModel):
    llm_valid: bool
    llm_message: str
    tavily_valid: Optional[bool] = None
    tavily_message: Optional[str] = None
    selected_model: str
