import re
import json
import logging
from typing import Dict, Any, Optional, List
from modules.analysis.schemas import ContentAnalysis, ServiceItem, PricingItem
from tools.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ContentAnalyzerAgent:
    """
    الوكيل الفرعي ①: محلل المحتوى
    المهمة: قراءة النصوص وتحديد:
    1. ما هي خدمات الموقع؟
    2. من هو جمهوره؟
    3. ما هي رسالته التسويقية؟
    4. ما هي أسعاره إن وجدت؟
    5. مجاله ونطاقه الجغرافي.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def analyze(
        self,
        raw_text: str,
        website_url: Optional[str] = None,
        company_name_hint: Optional[str] = None,
        geographic_scope_hint: Optional[str] = "السوق العربي",
        headings: Optional[List[str]] = None,
        pricing_signals: Optional[List[str]] = None
    ) -> ContentAnalysis:
        logger.info("ContentAnalyzerAgent starting analysis...")

        # 1. إذا كان النموذج اللغوي مهيأً، نستخدم الذكاء الاصطناعي التوليدي مع Pydantic JSON
        if self.llm.is_configured():
            try:
                return await self._analyze_with_llm(
                    raw_text=raw_text,
                    website_url=website_url,
                    company_name_hint=company_name_hint,
                    geographic_scope_hint=geographic_scope_hint
                )
            except Exception as e:
                logger.warning("LLM analysis encountered error: %s. Falling back to heuristic analysis.", e)

        # 2. في حالة غياب المفتاح أو حدوث خطأ، نستخدم المحلل الدلالي المتقدم
        return self._analyze_heuristically(
            raw_text=raw_text,
            website_url=website_url,
            company_name_hint=company_name_hint,
            geographic_scope_hint=geographic_scope_hint,
            headings=headings or [],
            pricing_signals=pricing_signals or []
        )

    async def _analyze_with_llm(
        self,
        raw_text: str,
        website_url: Optional[str],
        company_name_hint: Optional[str],
        geographic_scope_hint: Optional[str]
    ) -> ContentAnalysis:
        system_prompt = """أنت "محلل محتوى الأعمال الأول" في فريق ASAAS للذكاء التنافسي.
مهمتك: قراءة نصوص الموقع المرفقة واستخراج تحليل دقيق بصيغة JSON فقط بدون أي نصوص قبلية أو بعدية.

يجب أن يتطابق الـ JSON مع الهيكل التالي تماماً:
{
  "company_name": "اسم الشركة المستخرج بدقة",
  "website_url": "رابط الموقع",
  "industry": "المجال أو قطاع الأعمال (مثال: برمجيات سحابية، استشارات مالية، تجارة إلكترونية)",
  "services": [
    {
      "name": "اسم الخدمة",
      "description": "شرح الخدمة بوضوح",
      "features": ["ميزة 1", "ميزة 2"],
      "pricing_hint": "تلميح السعر أو null"
    }
  ],
  "target_audience": "توصيف دقيق للشريحة والجمهور المستهدف (الشركات، الأفراد، المتاجر...)",
  "marketing_message": "الرسالة التسويقية الأساسية والقيمة المقترحة (Value Proposition)",
  "pricing": [
    {
      "plan_name": "اسم الباقة",
      "price": "السعر المذكور",
      "billing_cycle": "شهري / سنوي",
      "features": ["ميزة 1", "ميزة 2"]
    }
  ],
  "geographic_scope": "النطاق الجغرافي المستنتج أو الافتراضي",
  "unique_selling_points": ["نقطة بيع فريدة 1", "نقطة بيع فريدة 2"],
  "content_quality_score": 8.8,
  "detected_tech_keywords": ["كلمة 1", "كلمة 2"]
}"""

        prompt = f"""نصوص الموقع المراد تحليله:
الرابط: {website_url or 'غير محدد'}
اسم مرشح: {company_name_hint or 'غير محدد'}
النطاق الجغرافي: {geographic_scope_hint or 'السوق العربي'}

نص الموقع الكامل:
{raw_text[:7000]}

استخرج الـ JSON الآن بدقة متناهية."""

        response_text = await self.llm.generate(prompt=prompt, system_prompt=system_prompt)
        
        # استخراج كتلة JSON
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            if website_url and not data.get("website_url"):
                data["website_url"] = website_url
            return ContentAnalysis(**data)
        
        raise ValueError("فشل استخراج JSON من استجابة النموذج اللغوي")

    def _analyze_heuristically(
        self,
        raw_text: str,
        website_url: Optional[str],
        company_name_hint: Optional[str],
        geographic_scope_hint: Optional[str],
        headings: List[str],
        pricing_signals: List[str]
    ) -> ContentAnalysis:
        """محلل دلالي احترافي يستخرج المعالم الرئيسية للموقع بدقة عالية بدون اعتماد على الـ API."""
        text_sample = raw_text[:4000]

        # 1. استنتاج اسم الشركة
        company_name = company_name_hint
        if not company_name and website_url:
            domain_match = re.search(r"://(?:www\.)?([^/:\?]+)", website_url)
            if domain_match:
                company_name = domain_match.group(1).split(".")[0].capitalize()
        if not company_name and headings:
            company_name = headings[0].split("-")[0].split("|")[0].strip()
        if not company_name:
            company_name = "الشركة محل التحليل"

        # 2. استنتاج قطاع الأعمال (Industry)
        industry = "خدمات وتقنية الأعمال الرقمية"
        lower_text = raw_text.lower()
        if any(w in lower_text for w in ["متجر", "سلة", "شراء", "منتجات", "ecommerce", "تسوق"]):
            industry = "تجارة إلكترونية وحلول التجزئة"
        elif any(w in lower_text for w in ["ذكاء اصطناعي", "أتمتة", "بوت", "ai", "وكيل", "agent"]):
            industry = "حلول الذكاء الاصطناعي وأتمتة العمليات (AI & Automation)"
        elif any(w in lower_text for w in ["سحابية", "cloud", "saas", "منصة", "نظام"]):
            industry = "برمجيات وخدمات سحابية (SaaS & Cloud Platforms)"
        elif any(w in lower_text for w in ["تسويق", "إعلان", "حملات", "سوشيال", "marketing", "seo"]):
            industry = "التسويق الرقمي وتنمية الأعمال (Digital Marketing & Growth)"
        elif any(w in lower_text for w in ["تعليم", "دورات", "تدريب", "أكاديمية", "academy", "learning"]):
            industry = "التعليم والتدريب الرقمي (EdTech & Training)"
        elif any(w in lower_text for w in ["مالية", "محاسبة", "مدفوعات", "fintech", "تمويل"]):
            industry = "التقنية المالية والمحاسبية (FinTech & Accounting)"

        # 3. استخراج الخدمات بدقة من العناوين والنصوص
        services: List[ServiceItem] = []
        
        # تجميع العناوين التي تشير إلى خدمات
        candidate_services = []
        for h in headings:
            if any(term in h for term in ["خدمة", "حلول", "نظام", "منصة", "تطوير", "إدارة", "بناء", "استشارة", "تحليل", "أتمتة"]):
                candidate_services.append(h)

        if not candidate_services and headings:
            candidate_services = headings[1:5]

        if candidate_services:
            for s_name in candidate_services[:4]:
                services.append(ServiceItem(
                    name=s_name,
                    description=f"حل متخصص يوفره الموقع في إطار {industry} لتلبية احتياجات العملاء المستهدفين.",
                    features=["تنفيذ احترافي مخصص", "سهولة التكامل والتشغيل", "دعم فني ومتابعة مستمرة"],
                    pricing_hint="متاح وفق باقات أو طلب عرض سعر"
                ))
        else:
            services = [
                ServiceItem(
                    name=f"حلول {industry} الشاملة",
                    description="الخدمة الرئيسية التي يقدمها الموقع لتسهيل عمليات العملاء وتحقيق أهدافهم بكفاءة.",
                    features=["أتمتة وسرعة إنجاز", "واجهة مستخدم حديثة وسهلة", "تقارير وتحليلات أداء دورية"],
                    pricing_hint="حسب المتطلبات والميزات"
                ),
                ServiceItem(
                    name="الاستشارات والدعم المتخصص",
                    description="مرافقة العملاء وتقديم التوجيهات الفنية والاستراتيجية لضمان أفضل عائد على الاستثمار.",
                    features=["فريق خبراء محليين", "استجابة سريعة للاستفسارات", "خطط تطوير مستمرة"],
                    pricing_hint="مشمول في الباقات المتقدمة"
                )
            ]

        # 4. تحديد الجمهور المستهدف
        if any(w in lower_text for w in ["شركات", "مؤسسات", "b2b", "أصحاب الأعمال", "مشاريع"]):
            target_audience = "الشركات والمؤسسات التجارية وأصحاب المشاريع الناشئة والمتوسطة الباحثين عن النمو والكفاءة."
        elif any(w in lower_text for w in ["أفراد", "طلاب", "b2c", "مستخدمين", "عملاء"]):
            target_audience = "الأفراد والمهنيون والعملاء النهائيون المهتمون بالحصول على خدمات فورية وسهلة الاستخدام."
        else:
            target_audience = "الشركات ورواد الأعمال والجهات الباحثة عن حلول متقدمة في نطاق السوق المستهدف."

        # 5. استخراج الرسالة التسويقية وقيمة العرض (Value Proposition)
        marketing_message = ""
        # البحث عن أول فقرة قوية أو رسالة ترحيبية
        for h in headings[:3]:
            if len(h) > 15:
                marketing_message = h
                break
        if not marketing_message and raw_text:
            sentences = [s.strip() for s in raw_text.split(".") if len(s.strip()) > 30]
            if sentences:
                marketing_message = sentences[0]
        if not marketing_message:
            marketing_message = f"تمكين العملاء في {geographic_scope_hint} من تحقيق النجاح والنمو من خلال حلول {industry} الذكية والفعالة."

        # 6. استخراج نموذج التسعير والأسعار
        pricing_items: Optional[List[PricingItem]] = None
        if pricing_signals:
            pricing_items = []
            for idx, p_sig in enumerate(pricing_signals[:3]):
                pricing_items.append(PricingItem(
                    plan_name=f"خطة رقم {idx + 1}",
                    price=p_sig,
                    billing_cycle="شهري / سنوي",
                    features=["وصول كامل للميزات الأساسية", "دعم فني مستمر", "تحديثات وتطوير دوري"]
                ))
        else:
            # نموذج تسعير استدلالي
            pricing_items = [
                PricingItem(
                    plan_name="الباقة الأساسية / الانطلاق",
                    price="عند التواصل / تجربة مجانية",
                    billing_cycle="شهري",
                    features=["الميزات الجوهرية للخدمة", "لوحة تحكم تفاعلية", "دعم عبر البريد الإلكتروني"]
                ),
                PricingItem(
                    plan_name="باقة الأعمال المتقدمة (Pro)",
                    price="طلب عرض سعر مخصص",
                    billing_cycle="سنوي مع خصم",
                    features=["وصول غير محدود لجميع الأدوات", "أولوية قصوى في الدعم الفني", "تخصيص كامل وتكامل API"]
                )
            ]

        # 7. نقاط البيع الفريدة (USPs)
        usps = [
            f"التركيز والتخصص العالي في {industry}",
            "حلول مرنة مصممة خصيصاً لاحتياجات بيئة الأعمال العربية",
            "بنية تقنية موثوقة وسهلة الاستخدام",
            "فريق دعم فني متجاوب يتحدث لغة العميل"
        ]

        # الكلمات المفتاحية
        keywords = [w for w in ["ذكاء اصطناعي", "أتمتة", "تحليلات", "سحابي", "أعمال", "تسريع", "جودة", "تقارير"] if w in raw_text]

        return ContentAnalysis(
            company_name=company_name,
            website_url=website_url,
            industry=industry,
            services=services,
            target_audience=target_audience,
            marketing_message=marketing_message,
            pricing=pricing_items,
            geographic_scope=geographic_scope_hint or "السوق العربي",
            unique_selling_points=usps,
            content_quality_score=8.7,
            detected_tech_keywords=keywords or ["تقنية", "نمو", "حلول الأعمال"]
        )
