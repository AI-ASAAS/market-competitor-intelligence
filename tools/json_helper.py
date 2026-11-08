import json
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def safe_load_json(text: str) -> Any:
    """
    محلل JSON فائق الصلابة ومحصن ضد أخطاء النماذج اللغوية في اللغة العربية:
    1. يتجاهل كتل الماركداون (```json ... ```).
    2. يستخرج نطاق الـ JSON الفعلي بين أول { أو [ وآخر } أو ].
    3. يعالج علامات التنصيص المزدوجة غير المحمية داخل النصوص العربية عبر ماسح الحالات المتقدم (State-machine scanner).
    4. يعالج الفواصل الزائدة (trailing commas).
    5. يعالج الانقطاع المبكر للتوكنات (Truncated JSON) عبر موازن الأقواس الذكي (Stack-based closer).
    """
    if not text or not isinstance(text, str):
        raise ValueError("النص المدخل لتحليل JSON فارغ")

    clean = text.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()

    # 1. محاولة التحليل المباشر السريع
    try:
        return json.loads(clean)
    except Exception:
        pass

    # 2. استخراج النطاق الحقيقي لـ JSON
    start_brace = clean.find("{")
    start_bracket = clean.find("[")
    start_pos = -1
    is_array = False
    if start_brace != -1 and start_bracket != -1:
        if start_bracket < start_brace:
            start_pos = start_bracket
            is_array = True
        else:
            start_pos = start_brace
    elif start_bracket != -1:
        start_pos = start_bracket
        is_array = True
    elif start_brace != -1:
        start_pos = start_brace

    if start_pos != -1:
        clean = clean[start_pos:]

    # 3. معالجة علامات التنصيص المزدوجة الداخلية عبر الماسح الذكي
    result = []
    i = 0
    n = len(clean)
    in_string = False

    while i < n:
        ch = clean[i]
        if ch == '\\' and i + 1 < n:
            result.append(ch)
            result.append(clean[i+1])
            i += 2
            continue

        if ch == '"':
            if not in_string:
                in_string = True
                result.append(ch)
                i += 1
                continue
            else:
                j = i + 1
                while j < n and clean[j] in ' \t\r\n':
                    j += 1
                next_char = clean[j] if j < n else ''

                if next_char in [',', ':', '}', ']'] or j >= n:
                    in_string = False
                    result.append(ch)
                    i += 1
                    continue
                else:
                    # علامة تنصيص داخلية في النص العربي
                    result.append("'")
                    i += 1
                    continue
        else:
            result.append(ch)
            i += 1

    repaired = "".join(result)
    # إزالة الفواصل الزائدة قبل الإغلاق
    repaired = re.sub(r',\s*([\}\]])', r'\1', repaired)

    try:
        return json.loads(repaired)
    except Exception:
        pass

    # 4. معالجة الانقطاع في نهاية النص (Truncated JSON) باستخدام مكدس الأقواس
    repaired = repaired.rstrip()
    if repaired.endswith(","):
        repaired = repaired[:-1].rstrip()
    if re.search(r'"[^"]*"\s*:\s*$', repaired):
        repaired = re.sub(r',?\s*"[^"]*"\s*:\s*$', '', repaired).rstrip()

    stack = []
    in_str = False
    escape = False
    for ch in repaired:
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if not in_str:
            if ch == '{':
                stack.append('}')
            elif ch == '[':
                stack.append(']')
            elif ch in ['}', ']']:
                if stack and stack[-1] == ch:
                    stack.pop()

    if in_str:
        repaired += '"'

    repaired += "".join(reversed(stack))
    repaired = re.sub(r',\s*([\}\]])', r'\1', repaired)

    try:
        return json.loads(repaired)
    except Exception as final_err:
        logger.error("safe_load_json completely failed. Text snippet: %s", text[:300])
        raise final_err
