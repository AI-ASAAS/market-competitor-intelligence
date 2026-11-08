import os
import json
import logging
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """عميل موحد للتعامل مع النماذج اللغوية (OpenRouter أو Google Gemini)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY or settings.GEMINI_API_KEY
        self.default_model = model or settings.DEFAULT_LLM_MODEL

    def is_configured(self) -> bool:
        """التحقق مما إذا كان هناك مفتاح API مهيأ."""
        return bool(self.api_key)

    async def generate(self, prompt: str, system_prompt: str = "", model: Optional[str] = None) -> str:
        """إرسال طلب إلى النموذج اللغوي وإرجاع النص المولد."""
        if not self.api_key:
            raise ValueError("لم يتم توفير مفتاح API للنموذج اللغوي (OPENROUTER_API_KEY أو GEMINI_API_KEY).")

        chosen_model = model or self.default_model

        # إذا كان المفتاح يبدأ بـ sk-or فهو OpenRouter
        if self.api_key.startswith("sk-or-") or (settings.OPENROUTER_API_KEY and self.api_key == settings.OPENROUTER_API_KEY):
            return await self._call_openrouter(prompt, system_prompt, chosen_model)
        else:
            # استخدام Gemini المباشر
            return await self._call_gemini(prompt, system_prompt, chosen_model or "gemini-2.5-flash")

    async def _call_openrouter(self, prompt: str, system_prompt: str, model: str) -> str:
        import httpx
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ai-asaas.com",
            "X-Title": "ASAAS Competitor Intelligence",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # تحديد سقف معقول للتوكنات مع تعطيل التفكير الزائد لضمان سرعة الاستجابة وامتلاء JSON
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 3500,
            "reasoning": {"effort": "none"}
        }

        fallback_models = [
            "nvidia/nemotron-3.5-lightning:free",
            "openrouter/free"
        ]

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            # إذا واجهنا خطأ رصيد غير كافٍ (402) أو خطأ في النموذج (400/404/429)، ننتقل للنماذج المجانية المعتمدة
            if response.status_code in [400, 402, 404, 429]:
                logger.warning("Primary model %s failed with status %d: %s. Trying free fallbacks...", model, response.status_code, response.text[:200])
                for fb in fallback_models:
                    if fb == model:
                        continue
                    payload["model"] = fb
                    logger.info("Attempting fallback with model: %s", fb)
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        break

            response.raise_for_status()
            data = response.json()
            choice_msg = data["choices"][0]["message"]
            content = choice_msg.get("content") or ""
            if not content.strip() and choice_msg.get("reasoning"):
                content = choice_msg.get("reasoning")
            return content

    async def _call_gemini(self, prompt: str, system_prompt: str, model: str) -> str:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"تعليمات النظام الأساسية:\n{system_prompt}\n\n---\nالمهمة المطلوبة:\n{prompt}"}]
            })
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.95,
                "maxOutputTokens": 3000
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            raise ValueError("استجابة غير متوقعة من نموذج Gemini")
