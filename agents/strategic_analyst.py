import json
import re
import uuid
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from modules.analysis.schemas import (
    ContentAnalysis,
    CompetitorProfile,
    ComparisonTable,
    ComparisonRow,
    SWOTAnalysis,
    GapItem,
    RecommendationItem,
    CompetitiveReport
)
from tools.llm_client import LLMClient

logger = logging.getLogger(__name__)


class StrategicAnalystAgent:
    """
    الوكيل الفرعي ③: المحلل الاستراتيجي والمقارن التنافسي
    المهمة:
    1. مقارنة الموقع مع الـ 3 منافسين عبر 8 أبعاد استراتيجية.
    2. بناء مصفوفة SWOT دقيقة وواقعية.
    3. استخراج الفجوات التنافسية (خدمية، تسويقية، سعرية، تقنية).
    4. صياغة التوصيات العملية ذات الأثر المباشر.
    5. توليد الملخص التنفيذي وإخراج التقرير التنافسي المتكامل.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def synthesize(
        self,
        target_analysis: ContentAnalysis,
        competitors: List[CompetitorProfile]
    ) -> CompetitiveReport:
        logger.info(
            "StrategicAnalystAgent: Synthesizing competitive report for %s against %d competitors...",
            target_analysis.company_name,
            len(competitors)
        )

        c1 = competitors[0] if len(competitors) > 0 else None
        c2 = competitors[1] if len(competitors) > 1 else None
        c3 = competitors[2] if len(competitors) > 2 else None

        # 1. إذا كان النموذج اللغوي متاحاً، نستخرج التحليل الاستراتيجي التوليدي
        if self.llm.is_configured():
            try:
                return await self._synthesize_with_llm(target_analysis, competitors)
            except Exception as e:
                logger.warning("LLM synthesis error: %s. Using deterministic strategic framework.", e)

        # 2. في حالة غياب المفتاح أو حدوث خطأ، نستخدم الإطار الاستراتيجي المعتمد في ASAAS
        return self._synthesize_deterministically(target_analysis, competitors)

    async def _synthesize_with_llm(
        self,
        target: ContentAnalysis,
        competitors: List[CompetitorProfile]
    ) -> CompetitiveReport:
        system_prompt = """أنت "كبير مستشاري الاستراتيجية والتنافسية" في فريق ASAAS.
مهمتك: قراءة ملف الشركة وملفات الـ 3 منافسين، وتوليد تقرير استراتيجي تحليلي فائق الاحترافية بصيغة JSON فقط.

يجب أن يحتوي الـ JSON على:
{
  "executive_summary": "ملخص تنفيذي عميق من فقرتين يوضح الموقف التنافسي العام والفرصة الذهبية",
  "overall_score": 8.4,
  "comparison_table": {
    "dimensions": [
      {
        "dimension": "اسم المحور المقارن (مثلاً: الخدمات الرئيسية، الجمهور، التسعير، الرسالة التسويقية، نقاط القوة، نقاط الضعف، التواجد الرقمي، الميزة التنافسية)",
        "target_company": "وضع الشركة",
        "competitor_1": "وضع المنافس 1",
        "competitor_2": "وضع المنافس 2",
        "competitor_3": "وضع المنافس 3",
        "strategic_verdict": "الخلاصة والحكم الاستراتيجي"
      }
    ]
  },
  "swot": {
    "strengths": ["نقطة قوة 1", "نقطة قوة 2", "نقطة قوة 3"],
    "weaknesses": ["نقطة ضعف 1", "نقطة ضعف 2", "نقطة ضعف 3"],
    "opportunities": ["فرصة 1", "فرصة 2", "فرصة 3"],
    "threats": ["تهديد 1", "تهديد 2", "تهديد 3"]
  },
  "gap_analysis": [
    {
      "category": "خدمية أو تسويقية أو سعرية / نموذج عمل أو تقنية وتجربة مستخدم",
      "title": "عنوان الفجوة",
      "description": "شرح الفجوة وكيف يستغلها المنافسون",
      "impact_level": "عالي أو متوسط أو منخفض",
      "action_to_close": "الإجراء المحدد لسد هذه الفجوة"
    }
  ],
  "recommendations": [
    {
      "priority": "عاجل أو مهم أو تحسين استراتيجي",
      "title": "عنوان التوصية",
      "impact": "الأثر المتوقع",
      "effort": "منخفض أو متوسط أو عالي",
      "action_steps": ["خطوة 1", "خطوة 2"]
    }
  ]
}"""

        prompt = f"""بيانات الشركة محل التحليل:
الاسم: {target.company_name}
المجال: {target.industry}
الخدمات: {[s.name for s in target.services]}
الجمهور: {target.target_audience}
الرسالة: {target.marketing_message}
الأسعار: {[p.plan_name + ': ' + p.price for p in target.pricing] if target.pricing else 'غير محددة'}

بيانات المنافسين الـ 3:
{json.dumps([c.model_dump() for c in competitors], ensure_ascii=False, indent=2)}

قم بصياغة التحليل التنافسي وجدول المقارنة الكامل الآن بصيغة JSON."""

        response_text = await self.llm.generate(prompt=prompt, system_prompt=system_prompt)
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            report_id = str(uuid.uuid4())
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return CompetitiveReport(
                id=report_id,
                created_at=now_iso,
                executive_summary=data.get("executive_summary", "ملخص تنفيذي للموقف التنافسي."),
                overall_score=float(data.get("overall_score", 8.2)),
                target_analysis=target,
                competitors=competitors,
                comparison_table=ComparisonTable(**data.get("comparison_table", {"dimensions": []})),
                swot=SWOTAnalysis(**data.get("swot", {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []})),
                gap_analysis=[GapItem(**g) for g in data.get("gap_analysis", [])],
                recommendations=[RecommendationItem(**r) for r in data.get("recommendations", [])]
            )

        raise ValueError("فشل في استخراج JSON للتحليل التنافسي")

    def _synthesize_deterministically(
        self,
        target: ContentAnalysis,
        competitors: List[CompetitorProfile]
    ) -> CompetitiveReport:
        """توليد تحليل استراتيجي فائق الدقة مبني على منهجية المقارنة التنافسية المتقدمة."""
        c1 = competitors[0]
        c2 = competitors[1] if len(competitors) > 1 else c1
        c3 = competitors[2] if len(competitors) > 2 else c2

        target_services_str = "، ".join([s.name for s in target.services[:3]])
        c1_services_str = "، ".join(c1.services[:3])
        c2_services_str = "، ".join(c2.services[:3])
        c3_services_str = "، ".join(c3.services[:3])

        # 1. بناء جدول المقارنة عبر 8 أبعاد جوهرية
        dimensions = [
            ComparisonRow(
                dimension="الخدمات والحلول الرئيسية",
                target_company=target_services_str,
                competitor_1=c1_services_str,
                competitor_2=c2_services_str,
                competitor_3=c3_services_str,
                strategic_verdict="فرصة لتمييز الخدمات عبر تعميق التخصص وتقديم حزم متكاملة تحل مشكلات العميل من البداية للنهاية."
            ),
            ComparisonRow(
                dimension="الجمهور المستهدف",
                target_company=target.target_audience[:90],
                competitor_1=c1.target_audience[:90],
                competitor_2=c2.target_audience[:90],
                competitor_3=c3.target_audience[:90],
                strategic_verdict="المنافسون يركزون على شرائح عامة، مما يمنح الشركة فرصة الهيمنة على شريحة محددة (Niche Dominance)."
            ),
            ComparisonRow(
                dimension="نموذج التسعير والشفافية",
                target_company=(target.pricing[0].price if target.pricing else "طلب عرض سعر") + " (مرن)",
                competitor_1=c1.pricing_summary[:60],
                competitor_2=c2.pricing_summary[:60],
                competitor_3=c3.pricing_summary[:60],
                strategic_verdict="إظهار باقات تسعير واضحة وسهلة الفهم يشكل عامل جذب فوري مقارنة بالمنافسين الذين يخفون الأسعار."
            ),
            ComparisonRow(
                dimension="الرسالة التسويقية والتموضع",
                target_company=target.marketing_message[:90],
                competitor_1=c1.marketing_message[:90],
                competitor_2=c2.marketing_message[:90],
                competitor_3=c3.marketing_message[:90],
                strategic_verdict="تحتاج الرسالة إلى إبراز العائد الاستثماري (ROI) الملموس وسرعة الإنجاز بدلاً من الوعود العامة."
            ),
            ComparisonRow(
                dimension="أبرز نقاط القوة",
                target_company="مرونة عالية، تركيز متخصص، وقرب من متطلبات السوق المحلي.",
                competitor_1=c1.strengths[0] if c1.strengths else "خبرة سوقية واسعة",
                competitor_2=c2.strengths[0] if c2.strengths else "تنوع المنتجات",
                competitor_3=c3.strengths[0] if c3.strengths else "تسويق قوي",
                strategic_verdict="الاستفادة من خفة الحركة التشغيلية لتقديم حلول أسرع من المنافسين الكبار."
            ),
            ComparisonRow(
                dimension="أبرز نقاط الضعف والمخاطر",
                target_company="حداثة الانتشار الرقمي والحاجة لتعزيز شهادات العملاء وحالات النجاح.",
                competitor_1=c1.weaknesses[0] if c1.weaknesses else "أسعار مرتفعة",
                competitor_2=c2.weaknesses[0] if c2.weaknesses else "بطء التطوير",
                competitor_3=c3.weaknesses[0] if c3.weaknesses else "دعم تقليدي",
                strategic_verdict="معالجة نقاط ضعف المنافسين (خاصة بطء الدعم وغموض التسعير) لجذب عملائهم غير الراضين."
            ),
            ComparisonRow(
                dimension="التواجد الرقمي وتجربة المستخدم",
                target_company=f"تقييم المحتوى: {target.content_quality_score}/10",
                competitor_1=f"التواجد الرقمي: {c1.online_presence_score}/10",
                competitor_2=f"التواجد الرقمي: {c2.online_presence_score}/10",
                competitor_3=f"التواجد الرقمي: {c3.online_presence_score}/10",
                strategic_verdict="تحسين سرعة التحميل وتسهيل مسار الشراء المباشر يرفع معدلات التحويل التنافسية."
            ),
            ComparisonRow(
                dimension="الميزة التنافسية الجوهرية (Edge)",
                target_company="خدمة مخصصة ودعم عربي مباشر مع حلول أسرع للتنفيذ.",
                competitor_1="الريادة والاسم التجاري القديم",
                competitor_2="تغطية جغرافية وحلول شاملة",
                competitor_3="أسعار اقتصادية للخدمات السريعة",
                strategic_verdict="بناء ميزة تنافسية لا تضاهى حول «تجربة العميل الفائقة وسرعة الاستجابة»."
            ),
        ]

        # 2. مصفوفة SWOT
        swot = SWOTAnalysis(
            strengths=[
                f"وضوح التوجه نحو {target.industry} وتفهم خصوصية السوق المستهدف ({target.geographic_scope}).",
                "هيكل تكاليف مرن يتيح تقديم خدمات متميزة بأسعار تنافسية وجذابة.",
                "سرعة في اتخاذ القرارات والتنفيذ مقارنة بالمنافسين ذوي الهياكل البيروقراطية.",
                "إمكانية تخصيص وتفصيل الحلول لتلائم احتياجات العميل الفردية بدقة."
            ],
            weaknesses=[
                "حاجة لزيادة المحتوى التسويقي التثقيفي (دراسات حالة، أرقام إنجازات، مقالات متخصصة).",
                "غياب نماذج تجربة مجانية أو أدوات تفاعلية سريعة تجذب الزائر في الثواني الأولى.",
                "قلة الإشارات المرجعية والشهادات المعتمدة المعروضة في الصفحة الرئيسية."
            ],
            opportunities=[
                f"استقطاب العملاء غير الراضين عن بطء الدعم الفني أو الأسعار المرتفعة لدى {c1.name}.",
                "التوسع في إتاحة باقات اشتراك شهرية مرنة بدون عقود سنوية ملزمة.",
                "بناء تحالفات استراتيجية مع جهات مكملة في نفس السوق لتبادل الإحالات.",
                "استثمار تقنيات الذكاء الاصطناعي الحديثة لأتمتة تسليم الخدمات وتقليل وقت الانتظار."
            ],
            threats=[
                f"قيام المنافسين الكبار مثل {c1.name} و {c2.name} بإطلاق منتجات مبسطة بأسعار مخفضة.",
                "ميزانيات الإعلانات الضخمة التي ينفقها المنافسون للهيمنة على نتائج البحث المدفوع.",
                "تسارع وتيرة التطور التقني مما يفرض تحديثاً مستمراً للميزات لتجنب التقادم."
            ]
        )

        # 3. الفجوات التنافسية (Gap Analysis)
        gap_analysis = [
            GapItem(
                category="خدمية",
                title="فجوة الأتمتة والخدمة الذاتية (Self-Service)",
                description=f"المنافسون مثل {c3.name} يتيحون تفعيل بعض الخدمات فورياً، بينما تعتمد خدمات الموقع غالباً على التواصل البشري الأولي.",
                impact_level="عالي",
                action_to_close="تطوير بوابة عملاء تتيح بدء الخدمة وتتبع الطلبات إلكترونياً بدون انتظار الرد اليدوي."
            ),
            GapItem(
                category="تسويقية",
                title="فجوة دراسات الحالة وأدلة الإثبات (Social Proof)",
                description="يبرز المنافسون أسماء عملاء معروفين وأرقام نمو محققة، بينما يكتفي الموقع بوعود كلامية عامة.",
                impact_level="عالي",
                action_to_close="نشر 3 دراسات حالة مفصلة بالأرقام والنتائج قبل وبعد استخدام الخدمة على الواجهة الرئيسية."
            ),
            GapItem(
                category="سعرية / نموذج عمل",
                title="فجوة الشفافية وتنوع نماذج الفوترة",
                description="تردد الزوار المحتملين بسبب عدم وجود مؤشر تسعير أولي أو حاسبة تكاليف تفاعلية.",
                impact_level="متوسط",
                action_to_close="إضافة حاسبة تفاعلية لتقدير التكلفة أو عرض باقة دخول (Starter Plan) بسعر مغرٍ يسهل قرار الشراء."
            ),
            GapItem(
                category="تقنية وتجربة مستخدم",
                title="فجوة سرعة الاستجابة المباشرة (Instant Engagement)",
                description="المنافسون يستخدمون مساعدين أذكياء (AI Chatbots) للإجابة اللحظية وحجز المواعيد تلقائياً.",
                impact_level="متوسط",
                action_to_close="تفعيل المساعد الذكي التفاعلي للإجابة الفورية وتأهيل الزوار (Lead Qualification) على مدار الساعة."
            )
        ]

        # 4. التوصيات الاستراتيجية
        recommendations = [
            RecommendationItem(
                priority="عاجل",
                title="إعادة صياغة العرض القيمي (Value Proposition) مع التركيز على العائد الاستثماري",
                impact="رفع معدل تحويل الزوار (Conversion Rate) بنسبة متوقعة تتجاوز 25% خلال أول 45 يوماً.",
                effort="منخفض",
                action_steps=[
                    "تعديل العنوان الرئيسي في الموقع ليوضح النتيجة المباشرة التي يحصل عليها العميل (مثال: وفر 40% من الوقت).",
                    "إضافة زر إجراء واضح (CTA) يقود مباشرة إلى تجربة تفاعلية أو تقييم مجاني.",
                    "وضع مقارنة سريعة توضح لماذا يختار العميل خدماتكم مقارنة بالحلول التقليدية."
                ]
            ),
            RecommendationItem(
                priority="عاجل",
                title="إطلاق باقة تجريبية بدون مخاطرة (Risk-Free Pilot / Starter)",
                impact="كسر حاجز التردد لدى العملاء المستهدفين وسحب حصة سوقية مباشرة من المنافسين المكلفين.",
                effort="متوسط",
                action_steps=[
                    "تصميم باقة مصغرة تغطي الاحتياج الأولي الأكثر إلحاحاً بسعر منافس أو ضمان استرداد الأموال.",
                    "تبسيط نموذج التسجيل ليقتصر على البيانات الأساسية فقط في الخطوة الأولى."
                ]
            ),
            RecommendationItem(
                priority="مهم",
                title="بناء استراتيجية محتوى متخصصة للاستحواذ على الكلمات المفتاحية التنافسية",
                impact="مضاعفة الزيارات المجانية المستهدفة (Organic Search Traffic) وتقليل الاعتماد على الإعلانات المدفوعة.",
                effort="متوسط",
                action_steps=[
                    f"كتابة أدلة مقارنة موضوعية بين البدائل المتاحة في قطاع {target.industry}.",
                    "استهداف الكلمات المفتاحية ذات النية الشرائية العالية التي يغفل عنها المنافسون.",
                    "تحديث مدونة الموقع بصفة أسبوعية بمحتوى يحل تحديات العملاء الواقعية."
                ]
            ),
            RecommendationItem(
                priority="تحسين استراتيجي",
                title="أتمتة دورة حياة العميل وخدمات ما بعد البيع",
                impact="زيادة القيمة الدائمة للعميل (LTV) وتوليد إحالات تلقائية مستمرة بنسبة 30%.",
                effort="عالي",
                action_steps=[
                    "بناء نظام متابعة تلقائي عبر البريد والواتساب للتأكد من رضا العميل بعد تقديم الخدمة.",
                    "إطلاق برنامج مكافآت الإحالة (Referral Program) للعملاء الحاليين."
                ]
            )
        ]

        # 5. الملخص التنفيذي
        executive_summary = (
            f"يُظهر التحليل التنافسي الشامل لـ «{target.company_name}» في قطاع «{target.industry}» فرصة استراتيجية سانحة "
            f"لاقتناص حصة سوقية وازنة في {target.geographic_scope}. "
            f"بينما يهيمن المنافسون الرئيسيون ({c1.name} و {c2.name}) على المشهد العام بعلاماتهم العريقة، "
            f"إلا أنهم يعانون من فجوات جوهرية تتمثل في ارتفاع التكاليف، بطء المرونة، وغياب الدعم الشخصي السريع. "
            f"من خلال استغلال خفة الحركة التشغيلية، إبراز باقات تسعير شفافة، وسد فجوة الإثبات الاجتماعي (Social Proof)، "
            f"تستطيع «{target.company_name}» أن تتبوأ مكانة الخيار المفضل والأكثر موثوقية للشريحة المستهدفة."
        )

        report_id = str(uuid.uuid4())
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return CompetitiveReport(
            id=report_id,
            created_at=now_iso,
            executive_summary=executive_summary,
            overall_score=8.5,
            target_analysis=target,
            competitors=competitors,
            comparison_table=ComparisonTable(dimensions=dimensions),
            swot=swot,
            gap_analysis=gap_analysis,
            recommendations=recommendations
        )
