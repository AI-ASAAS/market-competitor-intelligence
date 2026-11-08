import os
import sys
import asyncio
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import init_db


async def run_suite():
    await init_db()
    print("=" * 60)
    print("بدء اختبار شامل لكافة مسارات النظام والوكلاء...")
    print("=" * 60)

    base_url = "http://127.0.0.1:8008"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. فحص الحالة
        print("\n[1/5] فحص حالة الخادم ومفاتيح الـ API...")
        res_status = await client.get(f"{base_url}/api/status")
        assert res_status.status_code == 200, f"Status check failed: {res_status.text}"
        print("  -> الحالة سليمة:", res_status.json())

        # 2. فحص سحب وتحليل محتوى جديد
        print("\n[2/5] تشغيل طاقم الوكلاء الـ 3 (تحليل + منافسين + مقارنة استراتيجية)...")
        payload = {
            "content": "نحن منصة تميز الرقمية لخدمات التجارة السحابية وإدارة المخازن والمبيعات للشركات في الخليج العربي. نقدم أنظمة ERP متكاملة وإدارة المخزون وبوابات الدفع. باقاتنا تبدأ من 299 ر.س شهرياً.",
            "company_name": "منصة تميز الرقمية",
            "geographic_scope": "المملكة العربية السعودية والخليج",
            "llm_api_key": os.environ.get("OPENROUTER_API_KEY", ""),
            "selected_model": "nvidia/nemotron-3.5-lightning:free"
        }
        res_analyze = await client.post(f"{base_url}/api/analyze/text", json=payload)
        assert res_analyze.status_code == 200, f"Analysis failed: {res_analyze.text}"
        report = res_analyze.json()
        report_id = report["id"]
        print(f"  -> تم إنجاز التحليل بنجاح! معرف التقرير: {report_id}")
        print(f"  -> اسم الشركة: {report['target_analysis']['company_name']}")
        print(f"  -> المنافسون: {[c['name'] for c in report['competitors']]}")
        print(f"  -> عدد أبعاد المقارنة: {len(report['comparison_table']['dimensions'])}")
        print(f"  -> نقاط SWOT: {len(report['swot']['strengths'])} قوة / {len(report['swot']['weaknesses'])} ضعف")
        print(f"  -> الفجوات المرصودة: {len(report['gap_analysis'])}")
        print(f"  -> التوصيات الاستراتيجية: {len(report['recommendations'])}")

        # 3. فحص تصدير PDF الرسمي بقالب أساس
        print("\n[3/5] فحص توليد وتصدير ملف PDF بقالب أساس الرسمي...")
        res_pdf = await client.get(f"{base_url}/api/reports/{report_id}/pdf")
        assert res_pdf.status_code == 200, f"PDF export failed: {res_pdf.text}"
        assert res_pdf.headers.get("content-type") == "application/pdf"
        print(f"  -> تم توليد ملف PDF بنجاح! الحجم: {len(res_pdf.content)} بايت")

        # 4. فحص تصدير HTML الفاخر
        print("\n[4/5] فحص تصدير صفحة HTML التفاعلية...")
        res_html = await client.get(f"{base_url}/api/reports/{report_id}/html")
        assert res_html.status_code == 200
        print(f"  -> صفحة HTML سليمة! الحجم: {len(res_html.content)} بايت")

        # 5. فحص تصدير Markdown
        print("\n[5/5] فحص تصدير تقرير Markdown...")
        res_md = await client.get(f"{base_url}/api/reports/{report_id}/markdown")
        assert res_md.status_code == 200
        print(f"  -> ملف Markdown سليم! الحجم: {len(res_md.content)} بايت")

    print("\n" + "=" * 60)
    print("جميع الاختبارات الخمسة اكتملت بنجاح 100%! النظام جاهز تماماً.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_suite())
