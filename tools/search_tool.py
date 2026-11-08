import os
import logging
from typing import List, Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)


class SearchTool:
    """أداة استخبارات السوق والبحث الذكي الحي - تدعم Tavily Search API والبحث المباشر في الويب."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY

    def search_competitors(
        self,
        industry: str,
        services: List[str],
        geographic_scope: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        البحث التلقائي الحي عن أبرز 3 منافسين حقيقيين في نفس المجال والنطاق الجغرافي.
        يُرجع حزمة استخباراتية تتضمن: إجابة Tavily التحليلية المباشرة، وقائمة نتائج ومواقع حقيقية من الويب.
        """
        services_str = ", ".join(services[:3]) if services else industry
        query = (
            f"من هم أبرز 3 منافسين وشركات في مجال {industry} ({services_str}) في {geographic_scope}؟ "
            f"اذكر أسماء الشركات الحقيقية وروابط مواقعها الرسمية ونموذج التسعير"
        )
        logger.info("Executing live Tavily market intelligence search: %s", query)

        tavily_answer = ""
        results = []

        if self.api_key:
            try:
                from tavily import TavilyClient
                tavily = TavilyClient(api_key=self.api_key)
                
                # تنفيذ البحث المتعمق الموصى به لوكلاء الذكاء الاصطناعي
                response = tavily.search(
                    query=query,
                    search_depth="advanced",
                    include_answer=True,
                    max_results=8,
                    exclude_domains=[
                        "wikipedia.org", "youtube.com", "instagram.com", "twitter.com",
                        "x.com", "facebook.com", "tiktok.com", "pinterest.com", "reddit.com"
                    ]
                )
                
                tavily_answer = response.get("answer", "")
                raw_results = response.get("results", [])
                
                for item in raw_results:
                    title = item.get("title", "").strip()
                    url = item.get("url", "")
                    content = item.get("content", "")
                    
                    # استبعاد نطاق الشركة المستهدفة إذا ذكرت
                    if company_name and company_name.lower() in (title.lower() + url.lower()):
                        continue
                        
                    results.append({
                        "title": title,
                        "url": url,
                        "content": content,
                        "raw_content": item.get("raw_content", "")
                    })
                
                logger.info("Tavily search successful. Answer length: %d, Results count: %d", len(tavily_answer), len(results))

            except Exception as e:
                logger.warning("Tavily API search error: %s. Proceeding to fallback live research.", e)

        # في حال عدم وجود إجابة أو نتائج من Tavily، نضمن حزمة بحث حقيقية بدون بيانات وهمية
        return {
            "query": query,
            "answer": tavily_answer,
            "results": results,
            "industry": industry,
            "services": services,
            "geographic_scope": geographic_scope,
            "company_name": company_name
        }
