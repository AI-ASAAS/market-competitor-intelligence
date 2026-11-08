import os
import base64
import html
import subprocess
import tempfile
import logging
from typing import Optional
from modules.analysis.schemas import CompetitiveReport

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    توليد تقرير PDF رسمي فاخر ومحكم مطابق تماماً لقالب «ورقة التقارير - ASAAS»
    الميزات:
    1. ترويسة أساس الرسمية (image2.png) تظهر أعلى كل صفحة بالمقاس والنسبة الصحيحة.
    2. تذييل أساس الرسمي (image3.png) يظهر أسفل كل صفحة بالمقاس والنسبة الصحيحة.
    3. العلامة المائية الشفافة (image1.png) ثابتة في خلفية كل صفحة بدون تشويش.
    4. خطوط ثمانية (Thmanyah) الرسمية مضمنة داخل الملف.
    5. ألوان مريحة ومتناسقة مستوحاة من هوية أساس (Ink, Gold, Sand, Cream, Paper) بدون أي تضليل أسود.
    """

    @staticmethod
    def _get_base64_file(file_path: str, mime: str = "image/png") -> str:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{encoded}"
        return ""

    @classmethod
    def generate_html_for_pdf(cls, report: CompetitiveReport) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        assets_dir = os.path.join(base_dir, "data", "report_assets")
        fonts_dir = os.path.join(base_dir, "frontend", "src", "asaas-ui", "fonts", "thmanyah")
        robot_dir = os.path.join(base_dir, "frontend", "public", "robot")
        
        watermark_b64 = cls._get_base64_file(os.path.join(assets_dir, "image1.png"))
        header_b64 = cls._get_base64_file(os.path.join(assets_dir, "image2.png"))
        footer_b64 = cls._get_base64_file(os.path.join(assets_dir, "image3.png"))
        consultant_b64 = cls._get_base64_file(os.path.join(robot_dir, "08_ثقة.png"))

        font_sans_reg = cls._get_base64_file(os.path.join(fonts_dir, "sans", "thmanyahsans-Regular.woff2"), "font/woff2")
        font_sans_bold = cls._get_base64_file(os.path.join(fonts_dir, "sans", "thmanyahsans-Bold.woff2"), "font/woff2")
        font_serif_bold = cls._get_base64_file(os.path.join(fonts_dir, "serif-display", "thmanyahserifdisplay-Bold.woff2"), "font/woff2")

        target = report.target_analysis

        # 1. سطور جدول المقارنة المباشرة (8 محاور)
        matrix_rows = []
        for r in report.comparison_table.dimensions:
            matrix_rows.append(f"""
            <tr>
              <td class="col-dim"><strong>{html.escape(r.dimension)}</strong></td>
              <td class="col-target">{html.escape(r.target_company)}</td>
              <td class="col-comp">{html.escape(r.competitor_1)}</td>
              <td class="col-comp">{html.escape(r.competitor_2)}</td>
              <td class="col-comp">{html.escape(r.competitor_3)}</td>
              <td class="col-verdict">{html.escape(r.strategic_verdict)}</td>
            </tr>
            """)

        # 2. بطاقات المنافسين الـ 3 المباشرين
        comp_cards = []
        for idx, comp in enumerate(report.competitors, 1):
            comp_cards.append(f"""
            <div class="comp-box">
              <div class="comp-top">
                <span class="comp-badge">المنافس #{idx}</span>
                <span class="comp-name">{html.escape(comp.name)}</span>
                <span class="comp-score">التواجد الرقمي: {comp.online_presence_score}/10</span>
              </div>
              <div class="comp-site">{html.escape(comp.website)}</div>
              <div class="comp-msg">"{html.escape(comp.marketing_message)}"</div>
              <div class="comp-details">
                <div><strong>الموقع السوقي:</strong> {html.escape(comp.market_position)}</div>
                <div><strong>نموذج التسعير:</strong> {html.escape(comp.pricing_summary)}</div>
              </div>
              <div class="comp-services">
                <strong>الخدمات الرئيسية:</strong> {', '.join([html.escape(s) for s in comp.services])}
              </div>
              <div class="sw-row">
                <div class="sw-s"><strong>نقاط القوة:</strong> {'; '.join([html.escape(s) for s in comp.strengths])}</div>
                <div class="sw-w"><strong>نقاط الضعف:</strong> {'; '.join([html.escape(w) for w in comp.weaknesses])}</div>
              </div>
            </div>
            """)

        # 3. الفجوات التنافسية
        gaps_rows = []
        for g in report.gap_analysis:
            impact_color = "#b0342c" if g.impact_level == "عالي" else ("#ba9555" if g.impact_level == "متوسط" else "#5c554e")
            gaps_rows.append(f"""
            <div class="gap-item">
              <div class="gap-top">
                <span class="gap-badge">[{html.escape(g.category)}]</span>
                <span class="gap-title">{html.escape(g.title)}</span>
                <span class="gap-impact" style="color: {impact_color};">الأثر: {html.escape(g.impact_level)}</span>
              </div>
              <div class="gap-text">{html.escape(g.description)}</div>
              <div class="gap-rec"><strong>الإجراء المقترح:</strong> {html.escape(g.action_to_close)}</div>
            </div>
            """)

        # 4. التوصيات الاستراتيجية
        recs_rows = []
        for idx, rec in enumerate(report.recommendations, 1):
            steps_list = "".join([f"<li>{html.escape(st)}</li>" for st in rec.action_steps])
            recs_rows.append(f"""
            <div class="rec-item">
              <div class="rec-top">
                <span class="rec-num">{idx}</span>
                <span class="rec-title">{html.escape(rec.title)}</span>
                <span class="rec-badges">الأولوية: <strong>{html.escape(rec.priority)}</strong> | الجهد: <strong>{html.escape(rec.effort)}</strong></span>
              </div>
              <div class="rec-impact"><strong>الأثر المتوقع:</strong> {html.escape(rec.impact)}</div>
              <div class="rec-steps-box">
                <div class="rec-steps-lbl">خطوات التنفيذ:</div>
                <ol class="rec-steps">{steps_list}</ol>
              </div>
            </div>
            """)

        # 5. نقاط SWOT
        swot_s_html = "".join([f"<li>{html.escape(s)}</li>" for s in report.swot.strengths])
        swot_w_html = "".join([f"<li>{html.escape(w)}</li>" for w in report.swot.weaknesses])
        swot_o_html = "".join([f"<li>{html.escape(o)}</li>" for o in report.swot.opportunities])
        swot_t_html = "".join([f"<li>{html.escape(t)}</li>" for t in report.swot.threats])

        return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>تقرير التحليل التنافسي المعتمد — {html.escape(target.company_name)} | منظومة أساس</title>
  <style>
    @font-face {{
      font-family: 'Thmanyah Sans';
      src: url('{font_sans_reg}') format('woff2');
      font-weight: 400;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Thmanyah Sans';
      src: url('{font_sans_bold}') format('woff2');
      font-weight: 700;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Thmanyah Serif Display';
      src: url('{font_serif_bold}') format('woff2');
      font-weight: 700;
      font-style: normal;
    }}

    @page {{
      size: A4 portrait;
      margin-top: 32mm;
      margin-bottom: 24mm;
      margin-left: 12mm;
      margin-right: 12mm;
    }}
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    body {{
      font-family: 'Thmanyah Sans', -apple-system, 'Segoe UI', Tahoma, Arial, sans-serif;
      font-size: 9.5pt;
      line-height: 1.6;
      color: #221f1f;
      background-color: #ffffff;
      position: relative;
    }}

    /* ترويسة قالب أساس الرسمية - مكررة وثابتة أعلى كل صفحة بالمقاس الدقيق */
    .print-page-header {{
      position: fixed;
      top: -28mm;
      left: 0;
      right: 0;
      height: 26mm;
      text-align: center;
      z-index: 9999;
    }}
    .print-page-header img {{
      width: 100%;
      height: 26mm;
      object-fit: contain;
    }}

    /* تذييل قالب أساس الرسمي - مكرر وثابت أسفل كل صفحة بالمقاس الدقيق */
    .print-page-footer {{
      position: fixed;
      bottom: -20mm;
      left: 0;
      right: 0;
      height: 18mm;
      text-align: center;
      z-index: 9999;
    }}
    .print-page-footer img {{
      width: 100%;
      height: 18mm;
      object-fit: contain;
    }}

    /* العلامة المائية الشفافة الفاخرة لأساس - تتكرر في خلفية كل صفحة */
    .print-watermark {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 440px;
      opacity: 0.04;
      z-index: -1;
      pointer-events: none;
    }}

    /* فواصل الصفحات المنظمة */
    .page-break {{
      page-break-after: always;
    }}

    /* البطاقة التعريفية النظيفة للتقرير */
    .report-meta-box {{
      background: #faf7f2;
      border: 1px solid #ede7da;
      border-right: 4.5px solid #ba9555;
      padding: 12px 16px;
      margin-bottom: 12px;
      border-radius: 6px;
    }}
    .meta-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}
    .report-meta-title {{
      font-family: 'Thmanyah Serif Display', serif;
      font-size: 14pt;
      font-weight: bold;
      color: #221f1f;
    }}
    .doc-ref-badge {{
      font-size: 8.5pt;
      color: #ba9555;
      font-weight: bold;
      background: rgba(186, 149, 85, 0.12);
      border: 1px solid #ba9555;
      padding: 2px 8px;
      border-radius: 999px;
    }}
    .report-meta-sub {{
      font-size: 8.5pt;
      color: #5c554e;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .report-meta-sub strong {{
      color: #221f1f;
    }}

    /* العناوين المنظمة */
    .section-header {{
      font-family: 'Thmanyah Serif Display', serif;
      font-size: 11pt;
      font-weight: bold;
      color: #ba9555;
      border-bottom: 1px solid #ede7da;
      padding-bottom: 3px;
      margin-top: 10px;
      margin-bottom: 8px;
      page-break-after: avoid;
    }}

    /* الملخص التنفيذي */
    .exec-summary-wrap {{
      background: #fdfbf8;
      border: 1px solid #ede7da;
      padding: 10px 14px;
      border-radius: 6px;
      display: flex;
      gap: 12px;
      align-items: flex-start;
      margin-bottom: 10px;
    }}
    .consultant-img {{
      width: 42px;
      height: auto;
      flex-shrink: 0;
    }}
    .exec-summary {{
      font-size: 8.5pt;
      line-height: 1.65;
      text-align: justify;
      color: #221f1f;
    }}

    /* شبكة SWOT */
    .swot-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 10px;
      page-break-inside: avoid;
    }}
    .swot-col {{
      background: #fdfbf8;
      border: 1px solid #ede7da;
      border-radius: 6px;
      padding: 8px 12px;
    }}
    .swot-col--s {{ border-top: 3px solid #23744a; }}
    .swot-col--w {{ border-top: 3px solid #b0342c; }}
    .swot-col--o {{ border-top: 3px solid #ba9555; }}
    .swot-col--t {{ border-top: 3px solid #c3ad8d; }}
    .swot-title {{
      font-weight: bold;
      font-size: 8.5pt;
      margin-bottom: 4px;
      color: #221f1f;
    }}
    .swot-list {{
      padding-right: 16px;
      font-size: 8pt;
      color: #3b3633;
    }}
    .swot-list li {{
      margin-bottom: 2px;
    }}

    /* جدول المقارنة المباشرة */
    .matrix-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
      margin-bottom: 12px;
      font-size: 8pt;
      page-break-inside: avoid;
    }}
    .matrix-table th {{
      background: #faf7f2;
      color: #221f1f;
      border: 1px solid #d3c6b4;
      padding: 6px 8px;
      text-align: right;
      font-weight: bold;
    }}
    .matrix-table td {{
      border: 1px solid #ede7da;
      padding: 6px 8px;
      vertical-align: top;
      color: #221f1f;
    }}
    .matrix-table tr:nth-child(even) {{
      background: #fdfbf8;
    }}
    .col-dim {{
      width: 15%;
      background: #faf7f2;
      color: #ba9555;
    }}
    .col-target {{
      width: 18%;
      background: rgba(186, 149, 85, 0.05);
      font-weight: bold;
    }}
    .col-comp {{
      width: 17%;
    }}
    .col-verdict {{
      width: 16%;
      font-size: 7.5pt;
      color: #5c554e;
    }}

    /* بطاقات المنافسين */
    .comp-box {{
      background: #fdfbf8;
      border: 1px solid #ede7da;
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 8px;
      page-break-inside: avoid;
    }}
    .comp-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 3px;
    }}
    .comp-badge {{
      background: rgba(186, 149, 85, 0.15);
      color: #ba9555;
      font-size: 7.5pt;
      font-weight: bold;
      padding: 1px 6px;
      border-radius: 4px;
    }}
    .comp-name {{
      font-size: 9.5pt;
      font-weight: bold;
      color: #221f1f;
      flex: 1;
      margin-right: 8px;
    }}
    .comp-score {{
      font-size: 7.5pt;
      color: #ba9555;
      font-weight: bold;
    }}
    .comp-site {{
      font-size: 7.5pt;
      color: #ba9555;
      direction: ltr;
      text-align: right;
      margin-bottom: 4px;
    }}
    .comp-msg {{
      font-style: italic;
      color: #5c554e;
      font-size: 8pt;
      margin-bottom: 4px;
    }}
    .comp-details {{
      display: flex;
      gap: 16px;
      font-size: 8pt;
      color: #3b3633;
      margin-bottom: 4px;
    }}
    .comp-services {{
      font-size: 8pt;
      color: #3b3633;
      margin-bottom: 4px;
    }}
    .sw-row {{
      display: flex;
      gap: 10px;
      font-size: 7.5pt;
      border-top: 1px dashed #ede7da;
      padding-top: 4px;
    }}
    .sw-s {{
      flex: 1;
      color: #23744a;
    }}
    .sw-w {{
      flex: 1;
      color: #b0342c;
    }}

    /* الفجوات التنافسية */
    .gap-item {{
      background: #fdfbf8;
      border: 1px solid #ede7da;
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 6px;
      page-break-inside: avoid;
    }}
    .gap-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 3px;
    }}
    .gap-badge {{
      font-weight: bold;
      color: #ba9555;
      font-size: 8pt;
    }}
    .gap-title {{
      font-weight: bold;
      color: #221f1f;
      font-size: 9pt;
      flex: 1;
      margin-right: 8px;
    }}
    .gap-impact {{
      font-size: 8pt;
      font-weight: bold;
    }}
    .gap-text {{
      font-size: 8pt;
      color: #3b3633;
      margin-bottom: 3px;
    }}
    .gap-rec {{
      font-size: 8pt;
      color: #221f1f;
      background: #faf7f2;
      padding: 3px 6px;
      border-radius: 4px;
    }}

    /* التوصيات */
    .rec-item {{
      background: #fdfbf8;
      border: 1px solid #ede7da;
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 8px;
      page-break-inside: avoid;
    }}
    .rec-top {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}
    .rec-num {{
      background: #ba9555;
      color: #ffffff;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      text-align: center;
      line-height: 18px;
      font-size: 8pt;
      font-weight: bold;
    }}
    .rec-title {{
      font-weight: bold;
      color: #221f1f;
      font-size: 9pt;
      flex: 1;
    }}
    .rec-badges {{
      font-size: 7.5pt;
      color: #5c554e;
    }}
    .rec-impact {{
      font-size: 8pt;
      color: #3b3633;
      margin-bottom: 4px;
    }}
    .rec-steps-box {{
      background: #faf7f2;
      padding: 5px 8px;
      border-radius: 4px;
    }}
    .rec-steps-lbl {{
      font-size: 7.5pt;
      font-weight: bold;
      color: #ba9555;
      margin-bottom: 2px;
    }}
    .rec-steps {{
      padding-right: 16px;
      font-size: 7.5pt;
      color: #221f1f;
    }}

    /* الملاحظة النهائية */
    .closing-note {{
      margin-top: 12px;
      padding: 8px 12px;
      border-top: 1px solid #ede7da;
      text-align: center;
      font-size: 7.5pt;
      color: #7a6e5f;
    }}
  </style>
</head>
<body>
  <!-- ترويسة وتذييل وعلامة مائية ثابتة ومكررة في كل صفحة مطبوعة -->
  <div class="print-page-header">
    <img src="{header_b64}" alt="ترويسة أساس الرسمية">
  </div>
  <div class="print-page-footer">
    <img src="{footer_b64}" alt="تذييل أساس الرسمي">
  </div>
  <img src="{watermark_b64}" alt="" class="print-watermark" aria-hidden="true">

  <!-- ==================== الصفحة 1: ملخص الاستخبارات والـ SWOT ==================== -->
  <div class="report-meta-box">
    <div class="meta-top-row">
      <h1 class="report-meta-title">{html.escape(target.company_name)}</h1>
      <span class="doc-ref-badge">التقييم التنافسي: {report.overall_score}/10</span>
    </div>
    <div class="report-meta-sub">
      <span><strong>القطاع:</strong> {html.escape(target.industry)}</span>
      <span><strong>نطاق التحليل:</strong> {html.escape(target.geographic_scope)}</span>
      <span><strong>تاريخ التقرير:</strong> {html.escape(report.created_at)}</span>
      {f'<span><strong>الموقع:</strong> {html.escape(target.website_url)}</span>' if target.website_url else ''}
    </div>
  </div>

  <div class="section-header">الملخص التنفيذي الاستراتيجي (Executive Summary)</div>
  <div class="exec-summary-wrap">
    <img src="{consultant_b64}" class="consultant-img" alt="مستشار أساس">
    <p class="exec-summary">{html.escape(report.executive_summary)}</p>
  </div>

  <div class="section-header">التحليل الرباعي التنافسي الشامل (SWOT Analysis)</div>
  <div class="swot-grid">
    <div class="swot-col swot-col--s">
      <div class="swot-title">نقاط القوة (Strengths)</div>
      <ul class="swot-list">{swot_s_html}</ul>
    </div>
    <div class="swot-col swot-col--w">
      <div class="swot-title">نقاط الضعف (Weaknesses)</div>
      <ul class="swot-list">{swot_w_html}</ul>
    </div>
    <div class="swot-col swot-col--o">
      <div class="swot-title">الفرص الواعدة (Opportunities)</div>
      <ul class="swot-list">{swot_o_html}</ul>
    </div>
    <div class="swot-col swot-col--t">
      <div class="swot-title">التهديدات المحتملة (Threats)</div>
      <ul class="swot-list">{swot_t_html}</ul>
    </div>
  </div>

  <!-- ==================== فاصل إلى الصفحة 2: جدول المقارنة والمنافسون ==================== -->
  <div class="page-break"></div>

  <div class="section-header">مصفوفة المقارنة المباشرة (8 محاور جوهرية)</div>
  <table class="matrix-table">
    <thead>
      <tr>
        <th>المحور الاستراتيجي</th>
        <th>{html.escape(target.company_name)}</th>
        <th>{html.escape(report.competitors[0].name if len(report.competitors) > 0 else "المنافس #1")}</th>
        <th>{html.escape(report.competitors[1].name if len(report.competitors) > 1 else "المنافس #2")}</th>
        <th>{html.escape(report.competitors[2].name if len(report.competitors) > 2 else "المنافس #3")}</th>
        <th>الحكم الاستراتيجي</th>
      </tr>
    </thead>
    <tbody>
      {''.join(matrix_rows)}
    </tbody>
  </table>

  <div class="section-header">تحليل المنافسين الفعليين في السوق المستهدف</div>
  {''.join(comp_cards)}

  <!-- ==================== فاصل إلى الصفحة 3: الفجوات والتوصيات ==================== -->
  <div class="page-break"></div>

  <div class="section-header">الفجوات التسويقية والخدمية المرصودة (Market Gap Analysis)</div>
  {''.join(gaps_rows)}

  <div class="section-header">خارطة التوصيات الاستراتيجية والتنفيذية (Actionable Roadmap)</div>
  {''.join(recs_rows)}

  <div class="closing-note">
    تم إعداد وتدقيق هذا التقرير آلياً بواسطة طاقم وكلاء الذكاء الاصطناعي التابع لمنظومة أساس وفق معايير الحوكمة وسرية الأعمال.
  </div>
</body>
</html>"""

    @classmethod
    def generate_pdf(cls, report: CompetitiveReport) -> bytes:
        """توليد ملف PDF عبر محرك Chromium / Edge بدون أي برامج وسيطة معقدة."""
        html_content = cls.generate_html_for_pdf(report)
        
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as f:
            f.write(html_content)
            temp_html_path = f.name

        temp_pdf_path = temp_html_path.replace(".html", ".pdf")

        browser_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        browser_exe = None
        for b in browser_paths:
            if os.path.exists(b):
                browser_exe = b
                break

        if not browser_exe:
            raise FileNotFoundError("لم يتم العثور على متصفح Microsoft Edge أو Google Chrome لتوليد الـ PDF.")

        file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"

        cmd = [
            browser_exe,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={temp_pdf_path}",
            file_url
        ]

        logger.info("Generating PDF with command: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
        
        if not os.path.exists(temp_pdf_path) or os.path.getsize(temp_pdf_path) == 0:
            logger.error("PDF generation failed: %s", proc.stderr.decode('utf-8', errors='ignore'))
            raise RuntimeError("فشل توليد ملف الـ PDF عبر المحرك")

        with open(temp_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        try:
            os.remove(temp_html_path)
            os.remove(temp_pdf_path)
        except Exception:
            pass

        return pdf_bytes
