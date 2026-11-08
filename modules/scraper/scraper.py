import re
import logging
from typing import Dict, Any, Optional, List
import httpx
from bs4 import BeautifulSoup
from core.config import settings

logger = logging.getLogger(__name__)


class WebScraper:
    """محرك سحب وتحليل محتوى المواقع الإلكترونية مع معالجة الأخطاء."""

    def __init__(self):
        self.headers = {
            "User-Agent": settings.SCRAPER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def normalize_url(self, url: str) -> str:
        """تصحيح صيغة الرابط وإضافة البروتوكول إذا كان مفقوداً."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    async def scrape(self, url: str) -> Dict[str, Any]:
        """سحب وتحليل صفحة الويب واستخراج النصوص والعناوين والبيانات الوصفية."""
        target_url = self.normalize_url(url)
        logger.info("Scraping target URL: %s", target_url)

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=settings.SCRAPER_TIMEOUT_SECONDS,
                follow_redirects=True,
                verify=False,  # تجنب أخطاء شهادات SSL في بعض المواقع
            ) as client:
                response = await client.get(target_url)
                response.raise_for_status()
                html = response.text
                final_url = str(response.url)

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error while scraping %s: %s", target_url, e)
            raise ValueError(f"تعذر الوصول للموقع (كود الحالة: {e.response.status_code}): {target_url}")
        except httpx.RequestError as e:
            logger.error("Request error while scraping %s: %s", target_url, e)
            raise ValueError(f"فشل الاتصال بالموقع (تأكد من صحة الرابط أو توفر الخدمة): {str(e)}")
        except Exception as e:
            logger.error("Unexpected error scraping %s: %s", target_url, e)
            raise ValueError(f"خطأ غير متوقع أثناء سحب الموقع: {str(e)}")

        return self.parse_html(html, final_url)

    def parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """تنظيف الـ HTML واستخراج النصوص والعناوين المنظمة."""
        soup = BeautifulSoup(html, "html.parser")

        # 1. إزالة العناصر غير المفيدة
        for tag in soup(["script", "style", "noscript", "svg", "iframe", "form", "footer", "nav"]):
            tag.decompose()

        # 2. استخراج العنوان (Title)
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # 3. استخراج البيانات الوصفية (Meta Tags)
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        meta_keywords = ""
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_keywords = keywords_tag["content"].strip()

        site_name = ""
        site_name_tag = soup.find("meta", attrs={"property": "og:site_name"})
        if site_name_tag and site_name_tag.get("content"):
            site_name = site_name_tag["content"].strip()

        # 4. استخراج العناوين الرئيسية (h1, h2, h3)
        headings: List[str] = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text and len(text) > 3 and text not in headings:
                headings.append(text)

        # 5. استخراج النصوص الأساسية
        paragraphs = []
        for p in soup.find_all(["p", "li"]):
            text = p.get_text(strip=True)
            # تصفية النصوص القصيرة جداً أو المتكررة
            if len(text) > 25 and not any(text in existing for existing in paragraphs):
                paragraphs.append(text)

        full_text = " ".join(paragraphs)
        # تنظيف الفراغات الزائدة
        full_text = re.sub(r"\s+", " ", full_text)

        # تقليص النص إلى الحد الأقصى المسموح به لمنع تجاوز السياق
        if len(full_text) > settings.SCRAPER_MAX_CHARS:
            full_text = full_text[:settings.SCRAPER_MAX_CHARS] + " ... [تم اقتصار النص]"

        # 6. استخراج إشارات الأسعار
        pricing_signals = []
        price_patterns = [
            r"(\d+[\d,.]*\s*(?:ر\.س|ريال|دولار|\$|درهم|جنيه|USD|SAR|AED))",
            r"((?:باقة|خطة|اشتراك|تسعير|مجاناً|تجربة مجانية|شهرياً|سنوياً)[^\.\n]{5,50})",
        ]
        for pattern in price_patterns:
            matches = re.findall(pattern, full_text, flags=re.IGNORECASE)
            for m in matches:
                clean_m = m.strip() if isinstance(m, str) else m[0].strip()
                if clean_m and clean_m not in pricing_signals:
                    pricing_signals.append(clean_m)

        return {
            "url": url,
            "title": title,
            "site_name": site_name,
            "meta_description": meta_desc,
            "meta_keywords": meta_keywords,
            "headings": headings[:20],
            "paragraphs_count": len(paragraphs),
            "pricing_signals": pricing_signals[:10],
            "clean_text": full_text,
            "raw_summary": f"العنوان: {title}\nالوصف: {meta_desc}\nأهم العناوين:\n" + "\n".join(f"- {h}" for h in headings[:8]) + f"\n\nمحتوى النص:\n{full_text[:3000]}"
        }


scraper = WebScraper()
