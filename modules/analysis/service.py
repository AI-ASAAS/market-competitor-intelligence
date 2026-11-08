import logging
from typing import Optional, List
from modules.analysis.schemas import (
    AnalyzeUrlRequest,
    AnalyzeTextRequest,
    CompetitiveReport,
    ReportSummaryItem
)
from modules.analysis.repository import AnalysisRepository
from agents.orchestrator import CompetitorIntelligenceOrchestrator

logger = logging.getLogger(__name__)


class AnalysisService:
    """خدمة إدارة وتنفيذ عمليات التحليل التنافسي."""

    def __init__(self):
        self.repo = AnalysisRepository()

    async def analyze_url(self, request: AnalyzeUrlRequest) -> CompetitiveReport:
        orchestrator = CompetitorIntelligenceOrchestrator(
            tavily_api_key=request.tavily_api_key,
            llm_api_key=request.llm_api_key,
            selected_model=request.selected_model
        )
        report = await orchestrator.run_from_url(
            url=request.url,
            geographic_scope=request.geographic_scope or "السوق العربي",
            extra_context=request.extra_context
        )
        await self.repo.save_report(report)
        return report

    async def analyze_text(self, request: AnalyzeTextRequest) -> CompetitiveReport:
        orchestrator = CompetitorIntelligenceOrchestrator(
            tavily_api_key=request.tavily_api_key,
            llm_api_key=request.llm_api_key,
            selected_model=request.selected_model
        )
        report = await orchestrator.run_from_text(
            content=request.content,
            company_name=request.company_name,
            website_url=request.website_url,
            geographic_scope=request.geographic_scope or "السوق العربي"
        )
        await self.repo.save_report(report)
        return report

    async def get_report(self, report_id: str) -> Optional[CompetitiveReport]:
        return await self.repo.get_report_by_id(report_id)

    async def list_reports(self) -> List[ReportSummaryItem]:
        return await self.repo.list_reports()

    async def delete_report(self, report_id: str) -> bool:
        return await self.repo.delete_report(report_id)


analysis_service = AnalysisService()
