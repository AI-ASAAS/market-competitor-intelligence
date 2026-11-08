import json
import logging
from typing import List, Optional, Dict, Any
from core.database import get_db
from modules.analysis.schemas import CompetitiveReport, ReportSummaryItem

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """مستودع حفظ واسترجاع تقارير التحليل التنافسي من قاعدة بيانات SQLite."""

    @staticmethod
    async def save_report(report: CompetitiveReport) -> None:
        async with get_db() as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO analyses (
                    id, url, company_name, industry, geographic_scope,
                    content_analysis, competitors, comparison_table, swot,
                    gap_analysis, strategic_recommendations, executive_summary,
                    overall_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.id,
                    report.target_analysis.website_url,
                    report.target_analysis.company_name,
                    report.target_analysis.industry,
                    report.target_analysis.geographic_scope,
                    json.dumps(report.target_analysis.model_dump(), ensure_ascii=False),
                    json.dumps([c.model_dump() for c in report.competitors], ensure_ascii=False),
                    json.dumps(report.comparison_table.model_dump(), ensure_ascii=False),
                    json.dumps(report.swot.model_dump(), ensure_ascii=False),
                    json.dumps([g.model_dump() for g in report.gap_analysis], ensure_ascii=False),
                    json.dumps([r.model_dump() for r in report.recommendations], ensure_ascii=False),
                    report.executive_summary,
                    report.overall_score,
                    report.created_at,
                )
            )
            await db.commit()
            logger.info("Report %s saved successfully in database", report.id)

    @staticmethod
    async def get_report_by_id(report_id: str) -> Optional[CompetitiveReport]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM analyses WHERE id = ?", (report_id,))
            row = await cursor.fetchone()
            if not row:
                return None

            return CompetitiveReport(
                id=row["id"],
                created_at=row["created_at"],
                executive_summary=row["executive_summary"],
                overall_score=row["overall_score"],
                target_analysis=json.loads(row["content_analysis"]),
                competitors=json.loads(row["competitors"]),
                comparison_table=json.loads(row["comparison_table"]),
                swot=json.loads(row["swot"]),
                gap_analysis=json.loads(row["gap_analysis"]),
                recommendations=json.loads(row["strategic_recommendations"]),
            )

    @staticmethod
    async def list_reports() -> List[ReportSummaryItem]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT id, company_name, url, industry, geographic_scope, overall_score, competitors, created_at FROM analyses ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            summaries = []
            for r in rows:
                comps = json.loads(r["competitors"])
                comp_names = [c.get("name", "") for c in comps]
                summaries.append(ReportSummaryItem(
                    id=r["id"],
                    company_name=r["company_name"],
                    url=r["url"],
                    industry=r["industry"],
                    geographic_scope=r["geographic_scope"],
                    overall_score=r["overall_score"],
                    competitors_names=comp_names,
                    created_at=r["created_at"]
                ))
            return summaries

    @staticmethod
    async def delete_report(report_id: str) -> bool:
        async with get_db() as db:
            cursor = await db.execute("DELETE FROM analyses WHERE id = ?", (report_id,))
            await db.commit()
            return cursor.rowcount > 0
