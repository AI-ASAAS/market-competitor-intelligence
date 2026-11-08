from modules.analysis.schemas import CompetitiveReport


class MarkdownReportGenerator:
    """توليد تقرير ماركداون احترافي وشامل للذكاء التنافسي."""

    @staticmethod
    def generate(report: CompetitiveReport) -> str:
        target = report.target_analysis
        c1 = report.competitors[0] if len(report.competitors) > 0 else None
        c2 = report.competitors[1] if len(report.competitors) > 1 else None
        c3 = report.competitors[2] if len(report.competitors) > 2 else None

        md = []
        md.append(f"# 📊 التقرير التنافسي الشامل: {target.company_name}")
        md.append(f"> **تاريخ التقرير:** {report.created_at} | **المجال:** {target.industry} | **النطاق:** {target.geographic_scope}")
        md.append(f"> **التقييم التنافسي العام:** ⭐ `{report.overall_score}/10`")
        md.append("")
        md.append("---")
        md.append("")

        # 1. الملخص التنفيذي
        md.append("## 📌 1. الملخص التنفيذي (Executive Summary)")
        md.append(report.executive_summary)
        md.append("")

        # 2. ملف الموقع المحلل
        md.append("## 🏢 2. ملف الموقع المحلل (Target Company Profile)")
        md.append(f"- **اسم الشركة:** {target.company_name}")
        if target.website_url:
            md.append(f"- **الموقع الإلكتروني:** [{target.website_url}]({target.website_url})")
        md.append(f"- **الجمهور المستهدف:** {target.target_audience}")
        md.append(f"- **الرسالة التسويقية والقيمة المضافة:** {target.marketing_message}")
        md.append("")
        md.append("### 🛠 الخدمات والحلول المقدمة:")
        for s in target.services:
            features_str = "، ".join(s.features) if s.features else "حل متكامل"
            md.append(f"- **{s.name}:** {s.description}")
            md.append(f"  - *الميزات:* {features_str}")
            if s.pricing_hint:
                md.append(f"  - *السعر:* {s.pricing_hint}")
        md.append("")

        if target.pricing:
            md.append("### 💰 نموذج وباقات التسعير:")
            for p in target.pricing:
                p_feat = "، ".join(p.features) if p.features else "ميزات كاملة"
                md.append(f"- **{p.plan_name}:** `{p.price}` ({p.billing_cycle})")
                md.append(f"  - *المحتوى:* {p_feat}")
            md.append("")

        md.append("### 🌟 نقاط البيع الفريدة (USPs):")
        for usp in target.unique_selling_points:
            md.append(f"- ✅ {usp}")
        md.append("")

        # 3. جدول المقارنة التنافسي
        md.append("## ⚔️ 3. جدول المقارنة التنافسي المباشر (Competitive Matrix)")
        c1_name = c1.name if c1 else "المنافس 1"
        c2_name = c2.name if c2 else "المنافس 2"
        c3_name = c3.name if c3 else "المنافس 3"

        md.append(f"| المحور المقارن | {target.company_name} (موقعك) | {c1_name} | {c2_name} | {c3_name} | الخلاصة الاستراتيجية |")
        md.append("|---|---|---|---|---|---|")
        for row in report.comparison_table.dimensions:
            md.append(f"| **{row.dimension}** | {row.target_company} | {row.competitor_1} | {row.competitor_2} | {row.competitor_3} | {row.strategic_verdict} |")
        md.append("")

        # 4. المنافسون الـ 3 بالتفصيل
        md.append("## 🎯 4. تفاصيل أبرز 3 منافسين في السوق")
        for idx, comp in enumerate(report.competitors, 1):
            md.append(f"### {idx}. {comp.name}")
            md.append(f"- **الموقع:** [{comp.website}]({comp.website}) | **التواجد الرقمي:** `{comp.online_presence_score}/10`")
            md.append(f"- **الموقع السوقي:** {comp.market_position}")
            md.append(f"- **الخدمات:** {', '.join(comp.services)}")
            md.append(f"- **التسعير:** {comp.pricing_summary}")
            md.append(f"- **الرسالة التسويقية:** {comp.marketing_message}")
            md.append(f"- **نقاط القوة:** {', '.join(comp.strengths)}")
            md.append(f"- **نقاط الضعف:** {', '.join(comp.weaknesses)}")
            md.append("")

        # 5. تحليل SWOT
        md.append("## 🧭 5. مصفوفة التحليل الرباعي (SWOT Analysis)")
        md.append("| 💪 نقاط القوة (Strengths) | ⚠️ نقاط الضعف (Weaknesses) |")
        md.append("|---|---|")
        s_list = "<br>".join([f"• {s}" for s in report.swot.strengths])
        w_list = "<br>".join([f"• {w}" for w in report.swot.weaknesses])
        md.append(f"| {s_list} | {w_list} |")
        md.append("")
        md.append("| 🚀 الفرص السوقية (Opportunities) | 🔴 التهديدات والمخاطر (Threats) |")
        md.append("|---|---|")
        o_list = "<br>".join([f"• {o}" for o in report.swot.opportunities])
        t_list = "<br>".join([f"• {t}" for t in report.swot.threats])
        md.append(f"| {o_list} | {t_list} |")
        md.append("")

        # 6. تحليل الفجوات التنافسية
        md.append("## 🔍 6. الفجوات التنافسية (Competitive Gap Analysis)")
        for g in report.gap_analysis:
            impact_badge = "🔴 عالي" if g.impact_level == "عالي" else ("🟡 متوسط" if g.impact_level == "متوسط" else "🟢 منخفض")
            md.append(f"### ⚡ [{g.category}] {g.title} (الأثر: {impact_badge})")
            md.append(f"- **وصف الفجوة:** {g.description}")
            md.append(f"- **الإجراء العملي لسد الفجوة:** {g.action_to_close}")
            md.append("")

        # 7. التوصيات الاستراتيجية
        md.append("## 🚀 7. خارطة التوصيات الاستراتيجية (Actionable Recommendations)")
        for idx, rec in enumerate(report.recommendations, 1):
            priority_emoji = "🔥" if rec.priority == "عاجل" else ("⚡" if rec.priority == "مهم" else "🌱")
            md.append(f"### {idx}. {priority_emoji} [{rec.priority}] {rec.title}")
            md.append(f"- **الأثر المتوقع:** {rec.impact}")
            md.append(f"- **مستوى الجهد:** `{rec.effort}`")
            md.append("- **خطوات التنفيذ:**")
            for step in rec.action_steps:
                md.append(f"  1. {step}")
            md.append("")

        md.append("---")
        md.append("*تم إعداد هذا التقرير تلقائياً بواسطة مهندس تحليل الأعمال والمنافسين — منظومة أساس للذكاء الاصطناعي (ASAAS AI).*")
        return "\n".join(md)
