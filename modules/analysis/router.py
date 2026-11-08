from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from typing import List, Dict, Any
import httpx
import logging
from core.config import settings
from modules.analysis.schemas import (
    AnalyzeUrlRequest,
    AnalyzeTextRequest,
    CompetitiveReport,
    ReportSummaryItem,
    TestKeysRequest,
    TestKeysResponse
)
from modules.analysis.service import analysis_service
from modules.reports.markdown_generator import MarkdownReportGenerator
from modules.reports.html_generator import HTMLReportGenerator
from modules.reports.pdf_generator import PDFReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["التحليل التنافسي"])


@router.post("/analyze/url", response_model=CompetitiveReport, summary="تحليل موقع عبر الرابط والبحث عن المنافسين")
async def analyze_by_url(payload: AnalyzeUrlRequest):
    try:
        report = await analysis_service.analyze_url(payload)
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze/text", response_model=CompetitiveReport, summary="تحليل محتوى مدخل يدوياً والبحث عن المنافسين")
async def analyze_by_text(payload: AnalyzeTextRequest):
    try:
        report = await analysis_service.analyze_text(payload)
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports", response_model=List[ReportSummaryItem], summary="قائمة التقارير السابقة")
async def get_all_reports():
    return await analysis_service.list_reports()


@router.get("/reports/{report_id}", response_model=CompetitiveReport, summary="عرض تفاصيل تقرير محدد")
async def get_single_report(report_id: str):
    report = await analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    return report


@router.get("/reports/{report_id}/markdown", response_class=PlainTextResponse, summary="تصدير التقرير كـ Markdown")
async def export_report_markdown(report_id: str):
    import urllib.parse
    report = await analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    md_content = MarkdownReportGenerator.generate(report)
    safe_name = urllib.parse.quote(report.target_analysis.company_name)
    return PlainTextResponse(
        content=md_content,
        headers={"Content-Disposition": f"attachment; filename=\"competitor-report.md\"; filename*=UTF-8''competitor-report-{safe_name}.md"}
    )


@router.get("/reports/{report_id}/html", response_class=HTMLResponse, summary="تصدير التقرير كـ صفحة HTML تفاعلية بهوية أساس")
async def export_report_html(report_id: str):
    report = await analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    html_content = HTMLReportGenerator.generate(report)
    return HTMLResponse(content=html_content)


@router.get("/reports/{report_id}/pdf", summary="تصدير التقرير كـ PDF رسمي بقالب أساس")
async def export_report_pdf(report_id: str):
    import urllib.parse
    report = await analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    try:
        pdf_bytes = PDFReportGenerator.generate_pdf(report)
        safe_name = urllib.parse.quote(report.target_analysis.company_name)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"competitor-report.pdf\"; filename*=UTF-8''competitor-report-{safe_name}.pdf"
            }
        )
    except Exception as e:
        logger.error("Error generating PDF: %s", e)
        raise HTTPException(status_code=500, detail=f"تعذر توليد ملف الـ PDF: {str(e)}")


@router.delete("/reports/{report_id}", summary="حذف تقرير")
async def delete_single_report(report_id: str):
    success = await analysis_service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="التقرير غير موجود")
    return {"message": "تم حذف التقرير بنجاح", "id": report_id}


@router.get("/status", summary="حالة النظام وتكوين المفاتيح")
async def get_system_status():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tavily_configured": bool(settings.TAVILY_API_KEY),
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "default_region": settings.DEFAULT_REGION,
        "default_llm_model": settings.DEFAULT_LLM_MODEL
    }


@router.post("/test-keys", response_model=TestKeysResponse, summary="فحص صلاحية مفاتيح الـ API والاتصال الحي")
async def test_api_keys(payload: TestKeysRequest):
    """
    فحص فوري لصلاحية مفتاح OpenRouter / LLM ومفتاح Tavily إن وجد،
    وإرجاع تقرير بحالة الاتصال وجودة الخدمة.
    """
    key = (payload.llm_api_key or "").strip() or settings.OPENROUTER_API_KEY
    model = (payload.selected_model or "").strip() or settings.DEFAULT_LLM_MODEL

    llm_valid = False
    llm_message = ""

    # 1. فحص مفتاح النموذج اللغوي (OpenRouter)
    if not key:
        llm_valid = False
        llm_message = "لم يتم تحديد أي مفتاح. يعتمد النظام تلقائياً على المحرك التحليلي الاستدلالي المدمج."
    else:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    "https://openrouter.ai/api/v1/auth/key",
                    headers={"Authorization": f"Bearer {key}"}
                )
                if res.status_code == 200:
                    data = res.json().get("data", {})
                    label = data.get("label") or "مفتاح OpenRouter معتمد"
                    usage = data.get("usage", 0)
                    limit = data.get("limit")
                    limit_str = f" (الحد: {limit})" if limit else ""
                    llm_valid = True
                    llm_message = f"الاتصال نشط وسليم! تم التحقق من {label}{limit_str} — جاهز للعمل مع {model}."
                elif res.status_code == 401:
                    llm_valid = False
                    llm_message = "المفتاح غير صالح أو منتهي الصلاحية (رمز 401: Unauthorized). يرجى مراجعة المفتاح."
                elif res.status_code == 402:
                    llm_valid = True
                    llm_message = "المفتاح معتمد لكن رصيد الحساب غير كافٍ للموديلات المدفوعة. يُنصح باختيار نموذج مجاني مثل google/gemma-4-31b-it:free."
                else:
                    # اختبار إرسال استعلام خفيف
                    chat_res = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": "مرحبا"}],
                            "max_tokens": 5
                        }
                    )
                    if chat_res.status_code in (200, 201):
                        llm_valid = True
                        llm_message = f"تم فحص الاستجابة الحية من نموذج {model} بنجاح!"
                    elif chat_res.status_code == 402:
                        llm_valid = True
                        llm_message = "المفتاح صالح. يُفضل اختيار نموذج مجاني لضمان عدم توقف الاستعلامات."
                    else:
                        llm_valid = False
                        llm_message = f"استجاب الخادم برمز خطأ {chat_res.status_code}."
        except Exception as e:
            llm_valid = False
            llm_message = f"تعذر الاتصال بخادم OpenRouter: {str(e)}"

    # 2. فحص أداة البحث Tavily إن تم إدخالها
    tavily_key = (payload.tavily_api_key or "").strip() or settings.TAVILY_API_KEY
    tavily_valid = None
    tavily_message = None

    if tavily_key:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                t_res = await client.post(
                    "https://api.tavily.com/search",
                    headers={"Content-Type": "application/json"},
                    json={"api_key": tavily_key, "query": "Saudi tech business", "max_results": 1}
                )
                if t_res.status_code == 200:
                    tavily_valid = True
                    tavily_message = "أداة Tavily API نشطة — البحث الذكي والحي في الويب جاهز ومفعّل."
                else:
                    tavily_valid = False
                    tavily_message = f"مفتاح Tavily غير صالح أو انتهت حصته (رمز {t_res.status_code}). سيتم استخدام محرك البحث الاستدلالي المدمج."
        except Exception as e:
            tavily_valid = False
            tavily_message = f"تعذر فحص Tavily: {str(e)}"
    else:
        tavily_valid = True
        tavily_message = "محرك البحث التنافسي المدمج (قاعدة بيانات الأسواق العربية) نشط وجاهز."

    return TestKeysResponse(
        llm_valid=llm_valid,
        llm_message=llm_message,
        tavily_valid=tavily_valid,
        tavily_message=tavily_message,
        selected_model=model
    )
