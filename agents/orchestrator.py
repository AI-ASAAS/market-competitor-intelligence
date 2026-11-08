import logging
from typing import Optional, Dict, Any, Callable
from modules.analysis.schemas import CompetitiveReport, ContentAnalysis
from agents.content_analyzer import ContentAnalyzerAgent
from agents.competitor_finder import CompetitorFinderAgent
from agents.strategic_analyst import StrategicAnalystAgent
from modules.scraper.scraper import scraper
from tools.llm_client import LLMClient
from tools.search_tool import SearchTool

logger = logging.getLogger(__name__)


class CompetitorIntelligenceOrchestrator:
    """
    المنسق العام لطاقم وكلاء الذكاء التنافسي (Multi-Agent Crew Orchestrator).
    يدير تسلسل المراحل:
    1. سحب وتجهيز نصوص الموقع.
    2. تشغيل الوكيل ① (محلل المحتوى) لاستخراج الخدمات والجمهور والرسالة والأسعار.
    3. تشغيل الوكيل ② (باحث المنافسين) والبحث التلقائي في الويب عبر Tavily API لاكتشاف 3 منافسين.
    4. تشغيل الوكيل ③ (المحلل الاستراتيجي) لإنتاج جدول المقارنة وSWOT والفجوات والتوصيات.
    5. تجميع التقرير النهائي.
    """

    def __init__(self, tavily_api_key: Optional[str] = None, llm_api_key: Optional[str] = None, selected_model: Optional[str] = None):
        self.llm_client = LLMClient(api_key=llm_api_key, model=selected_model)
        self.search_tool = SearchTool(api_key=tavily_api_key)
        
        self.agent_content = ContentAnalyzerAgent(llm_client=self.llm_client)
        self.agent_finder = CompetitorFinderAgent(search_tool=self.search_tool, llm_client=self.llm_client)
        self.agent_analyst = StrategicAnalystAgent(llm_client=self.llm_client)

    async def run_from_url(
        self,
        url: str,
        geographic_scope: str = "السوق العربي",
        extra_context: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> CompetitiveReport:
        """تشغيل الطاقم بالكامل انطلاقاً من رابط موقع إلكتروني."""
        logger.info("Starting intelligence workflow for URL: %s", url)

        # المرحلة 1: سحب الموقع
        if progress_callback:
            progress_callback("جاري سحب وفحص محتوى الموقع الإلكتروني...", 15)
        
        scraped_data = await scraper.scrape(url)
        raw_text = scraped_data["clean_text"]
        if extra_context:
            raw_text = f"سياق إضافي مقدم من المستخدم:\n{extra_context}\n\n---\nمحتوى الموقع:\n{raw_text}"

        # المرحلة 2: تشغيل الوكيل ① (محلل المحتوى)
        if progress_callback:
            progress_callback("الوكيل ①: تحليل الخدمات، الجمهور المستهدف، ونموذج التسعير...", 40)
        
        content_analysis = await self.agent_content.analyze(
            raw_text=raw_text,
            website_url=scraped_data["url"],
            company_name_hint=scraped_data["site_name"] or scraped_data["title"],
            geographic_scope_hint=geographic_scope,
            headings=scraped_data["headings"],
            pricing_signals=scraped_data["pricing_signals"]
        )

        # المرحلة 3: تشغيل الوكيل ② (باحث المنافسين)
        if progress_callback:
            progress_callback("الوكيل ②: البحث في الويب واكتشاف أبرز 3 منافسين وسحب بياناتهم...", 65)

        competitors = await self.agent_finder.find_competitors(
            target_analysis=content_analysis
        )

        # المرحلة 4: تشغيل الوكيل ③ (المحلل الاستراتيجي)
        if progress_callback:
            progress_callback("الوكيل ③: إعداد جدول المقارنة، تحليل SWOT، والفجوات التنافسية...", 85)

        report = await self.agent_analyst.synthesize(
            target_analysis=content_analysis,
            competitors=competitors
        )

        if progress_callback:
            progress_callback("اكتمل التقرير التنافسي بنجاح!", 100)

        return report

    async def run_from_text(
        self,
        content: str,
        company_name: Optional[str] = None,
        website_url: Optional[str] = None,
        geographic_scope: str = "السوق العربي",
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> CompetitiveReport:
        """تشغيل الطاقم بالكامل انطلاقاً من نص محتوى مدخل يدوياً."""
        logger.info("Starting intelligence workflow from manual text input...")

        # المرحلة 1: تحليل المحتوى المباشر
        if progress_callback:
            progress_callback("الوكيل ①: قراءة النص وتحديد الخدمات والجمهور والرسالة...", 30)

        content_analysis = await self.agent_content.analyze(
            raw_text=content,
            website_url=website_url,
            company_name_hint=company_name,
            geographic_scope_hint=geographic_scope
        )

        # المرحلة 2: تشغيل الوكيل ② (باحث المنافسين)
        if progress_callback:
            progress_callback("الوكيل ②: البحث في الويب عن 3 منافسين وسحب بياناتهم...", 60)

        competitors = await self.agent_finder.find_competitors(
            target_analysis=content_analysis
        )

        # المرحلة 3: تشغيل الوكيل ③ (المحلل الاستراتيجي)
        if progress_callback:
            progress_callback("الوكيل ③: إعداد جدول المقارنة وتحليل SWOT والفجوات...", 85)

        report = await self.agent_analyst.synthesize(
            target_analysis=content_analysis,
            competitors=competitors
        )

        if progress_callback:
            progress_callback("اكتمل التقرير التنافسي بنجاح!", 100)

        return report
