import os
import base64
import html
from modules.analysis.schemas import CompetitiveReport


class HTMLReportGenerator:
    """
    توليد تقرير HTML تفاعلي فائق الفخامة بهوية أساس البصرية الرسمية (امتداد التصميم الرئيسي).
    الميزات:
    1. ألوان مريحة ومتناسقة بالكامل (Paper #fcf9f5, Cream #f5efe6, Gold #ba9555, Ink #221f1f) بدون أي تضليل أسود.
    2. ترويسة أساس الرسمية (image2.png) أعلى التقرير بالمقاس الصحيح.
    3. تذييل أساس الرسمي (image3.png) أسفل التقرير.
    4. تصميم متجاوب (Responsive) بنسبة 100% لكافة الشاشات والجوالات.
    5. طباعة نظيفة تكرر الترويسة والتذييل على كافة الصفحات.
    """

    @staticmethod
    def _get_base64_image(image_path: str) -> str:
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"
        return ""

    @classmethod
    def generate(cls, report: CompetitiveReport) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        assets_dir = os.path.join(base_dir, "data", "report_assets")
        robot_dir = os.path.join(base_dir, "frontend", "public", "robot")

        watermark_b64 = cls._get_base64_image(os.path.join(assets_dir, "image1.png"))
        header_b64 = cls._get_base64_image(os.path.join(assets_dir, "image2.png"))
        footer_b64 = cls._get_base64_image(os.path.join(assets_dir, "image3.png"))
        robot_consultant = cls._get_base64_image(os.path.join(robot_dir, "08_ثقة.png"))

        target = report.target_analysis

        # بناء سطور جدول المقارنة المباشرة
        table_rows_html = []
        for r in report.comparison_table.dimensions:
            table_rows_html.append(f"""
            <tr>
              <td class="dim-name">{html.escape(r.dimension)}</td>
              <td class="dim-target">{html.escape(r.target_company)}</td>
              <td>{html.escape(r.competitor_1)}</td>
              <td>{html.escape(r.competitor_2)}</td>
              <td>{html.escape(r.competitor_3)}</td>
              <td class="dim-verdict">{html.escape(r.strategic_verdict)}</td>
            </tr>
            """)

        # بناء بطاقات المنافسين الـ 3
        competitors_html = []
        for idx, comp in enumerate(report.competitors, 1):
            services_badges = "".join([f'<span class="badge badge--sand">{html.escape(s)}</span>' for s in comp.services])
            strengths_list = "".join([f'<li>{html.escape(s)}</li>' for s in comp.strengths])
            weaknesses_list = "".join([f'<li>{html.escape(w)}</li>' for w in comp.weaknesses])
            
            competitors_html.append(f"""
            <div class="competitor-card">
              <div class="competitor-header">
                <div>
                  <div class="competitor-num">المنافس #{idx}</div>
                  <h3 class="competitor-name">{html.escape(comp.name)}</h3>
                  <a href="{html.escape(comp.website)}" target="_blank" rel="noreferrer" class="competitor-link">{html.escape(comp.website)} ↗</a>
                </div>
                <div class="score-badge">
                  <div class="score-val">{comp.online_presence_score}</div>
                  <div class="score-lbl">التواجد الرقمي</div>
                </div>
              </div>

              <div class="competitor-body">
                <div class="field-group">
                  <label class="field-label">الموقع السوقي:</label>
                  <p class="field-val">{html.escape(comp.market_position)}</p>
                </div>
                <div class="field-group">
                  <label class="field-label">الرسالة التسويقية:</label>
                  <p class="field-val italic-msg">"{html.escape(comp.marketing_message)}"</p>
                </div>
                <div class="field-group">
                  <label class="field-label">الخدمات الرئيسية:</label>
                  <div class="badges-wrap">{services_badges}</div>
                </div>
                <div class="field-group">
                  <label class="field-label">نموذج التسعير:</label>
                  <p class="field-val pricing-text">{html.escape(comp.pricing_summary)}</p>
                </div>

                <div class="sw-grid">
                  <div class="sw-box sw-box--green">
                    <div class="sw-title">نقاط القوة التنافسية:</div>
                    <ul>{strengths_list}</ul>
                  </div>
                  <div class="sw-box sw-box--red">
                    <div class="sw-title">نقاط الضعف والفجوات:</div>
                    <ul>{weaknesses_list}</ul>
                  </div>
                </div>
              </div>
            </div>
            """)

        # بناء الفجوات
        gaps_html = []
        for g in report.gap_analysis:
            impact_cls = "badge--red" if g.impact_level == "عالي" else ("badge--gold" if g.impact_level == "متوسط" else "badge--sand")
            gaps_html.append(f"""
            <div class="gap-card">
              <div class="gap-header">
                <span class="badge badge--sand">{html.escape(g.category)}</span>
                <h4 class="gap-title">{html.escape(g.title)}</h4>
                <span class="badge {impact_cls}">الأثر: {html.escape(g.impact_level)}</span>
              </div>
              <p class="gap-desc">{html.escape(g.description)}</p>
              <div class="gap-action-box">
                <strong>الإجراء الاستراتيجي المقترح:</strong> {html.escape(g.action_to_close)}
              </div>
            </div>
            """)

        # بناء التوصيات
        recommendations_html = []
        for idx, rec in enumerate(report.recommendations, 1):
            steps = "".join([f'<li>{html.escape(s)}</li>' for s in rec.action_steps])
            recommendations_html.append(f"""
            <div class="rec-card">
              <div class="rec-header">
                <div class="rec-num">{idx}</div>
                <h4 class="rec-title">{html.escape(rec.title)}</h4>
                <div class="rec-badges">
                  <span class="badge badge--gold">الأولوية: {html.escape(rec.priority)}</span>
                  <span class="badge badge--sand">الجهد: {html.escape(rec.effort)}</span>
                </div>
              </div>
              <div class="rec-impact">
                <strong>الأثر المتوقع:</strong> {html.escape(rec.impact)}
              </div>
              <div class="rec-steps">
                <strong>خطوات التنفيذ الموصى بها:</strong>
                <ol>{steps}</ol>
              </div>
            </div>
            """)

        # عناصر SWOT
        swot_s = "".join([f'<li>{html.escape(s)}</li>' for s in report.swot.strengths])
        swot_w = "".join([f'<li>{html.escape(w)}</li>' for w in report.swot.weaknesses])
        swot_o = "".join([f'<li>{html.escape(o)}</li>' for o in report.swot.opportunities])
        swot_t = "".join([f'<li>{html.escape(t)}</li>' for t in report.swot.threats])

        return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>تقرير التحليل التنافسي: {html.escape(target.company_name)} | منظومة أساس</title>
  <style>
    :root {{
      --brand-ink: #221f1f;
      --brand-gold: #ba9555;
      --brand-gold-glow: rgba(186, 149, 85, 0.28);
      --brand-sand: #d3c6b4;
      --brand-clay: #c3ad8d;
      --brand-cream: #ede7da;
      --brand-paper: #fcf9f5;
      --bg: #f5efe6;
      --surface: #ffffff;
      --surface-thick: #faf7f2;
      --hairline: rgba(186, 149, 85, 0.2);
      --hairline-soft: rgba(211, 198, 180, 0.4);
      --text: #221f1f;
      --text-2: rgba(34, 31, 31, 0.75);
      --text-3: rgba(34, 31, 31, 0.52);
      --radius-lg: 16px;
      --radius-md: 12px;
      --radius-sm: 8px;
      --radius-pill: 999px;
      --font-display: 'Thmanyah Serif Display', 'Amiri', 'Traditional Arabic', serif;
      --font-sans: 'Thmanyah Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.8;
      padding: 20px 14px 60px;
      min-height: 100vh;
      position: relative;
    }}

    /* العلامة المائية الشفافة الفاخرة لأساس */
    .watermark-bg {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: min(550px, 80vw);
      opacity: 0.035;
      pointer-events: none;
      z-index: 0;
    }}

    .container {{
      max-width: 1140px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }}

    /* ورقة التقرير الفاخرة (Paper Document Container) */
    .report-paper {{
      background: var(--surface);
      border: 1px solid var(--hairline-soft);
      border-radius: var(--radius-lg);
      box-shadow: 0 4px 24px rgba(74, 54, 22, 0.06);
      padding: 24px 32px 36px;
      margin-bottom: 24px;
    }}

    /* الترويسة الرسمية لأساس - بالمقاس الطبيعي المتناسق */
    .official-header-banner {{
      width: 100%;
      text-align: center;
      margin-bottom: 24px;
      padding-bottom: 14px;
      border-bottom: 1.5px solid var(--brand-gold);
    }}
    .official-header-banner img {{
      max-width: 100%;
      height: auto;
      max-height: 72px;
      object-fit: contain;
    }}

    /* التذييل الرسمي لأساس */
    .official-footer-banner {{
      width: 100%;
      text-align: center;
      margin-top: 36px;
      padding-top: 18px;
      border-top: 1px solid var(--brand-sand);
    }}
    .official-footer-banner img {{
      max-width: 100%;
      height: auto;
      max-height: 48px;
      object-fit: contain;
    }}
    .footer-note {{
      font-size: 11px;
      color: var(--text-3);
      margin-top: 8px;
    }}

    /* شريط أدوات التقرير العلوي */
    .top-actions-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 10px 18px;
      background: var(--surface);
      border: 1px solid var(--hairline);
      border-radius: var(--radius-pill);
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
      flex-wrap: wrap;
      gap: 12px;
    }}

    .doc-status-badge {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--brand-gold);
      font-weight: 700;
    }}
    .pulse-dot {{
      width: 8px;
      height: 8px;
      background: var(--brand-gold);
      border-radius: 50%;
    }}

    .action-btns {{
      display: flex;
      gap: 10px;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: var(--radius-pill);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      text-decoration: none;
      font-family: inherit;
      transition: all 0.2s ease;
    }}
    .btn--primary {{
      background: var(--brand-gold);
      color: #ffffff;
      box-shadow: 0 4px 14px var(--brand-gold-glow);
    }}
    .btn--glass {{
      background: var(--surface-thick);
      color: var(--text);
      border-color: var(--hairline);
    }}
    .btn:hover {{
      transform: translateY(-1px);
    }}

    /* بطاقة بيانات الشركة المستهدفة */
    .company-hero {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--surface-thick);
      border: 1px solid var(--hairline);
      border-radius: var(--radius-md);
      padding: 22px 26px;
      margin-bottom: 24px;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .company-name {{
      font-family: var(--font-display);
      font-size: 24px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 6px;
    }}
    .company-url {{
      color: var(--brand-gold);
      text-decoration: none;
      font-size: 13px;
    }}
    .company-meta-row {{
      display: flex;
      gap: 10px;
      margin-bottom: 8px;
      flex-wrap: wrap;
    }}
    .score-dial {{
      background: rgba(186, 149, 85, 0.12);
      border: 1px solid rgba(186, 149, 85, 0.35);
      border-radius: var(--radius-md);
      padding: 14px 22px;
      text-align: center;
      min-width: 120px;
    }}
    .score-num {{
      font-size: 32px;
      font-weight: 900;
      color: var(--brand-gold);
      line-height: 1;
    }}
    .score-label {{
      font-size: 11px;
      color: var(--text-2);
      font-weight: 600;
      margin-top: 4px;
    }}

    /* الملخص التنفيذي */
    .exec-summary-box {{
      background: #fdfbf8;
      border: 1px solid var(--brand-cream);
      border-right: 4px solid var(--brand-gold);
      border-radius: var(--radius-sm);
      padding: 16px 20px;
      margin-bottom: 28px;
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }}
    .robot-thumb {{
      width: 50px;
      height: auto;
      flex-shrink: 0;
    }}
    .exec-p {{
      font-size: 14.5px;
      line-height: 1.8;
      color: var(--text);
    }}

    /* العناوين */
    .section-title {{
      font-family: var(--font-display);
      font-size: 19px;
      font-weight: 700;
      color: var(--brand-gold);
      margin-bottom: 16px;
      border-bottom: 1px solid var(--hairline);
      padding-bottom: 6px;
    }}

    /* مصفوفة المقارنة */
    .table-container {{
      overflow-x: auto;
      margin-bottom: 30px;
      border: 1px solid var(--hairline-soft);
      border-radius: var(--radius-md);
      background: #ffffff;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13.5px;
      text-align: right;
    }}
    th {{
      background: var(--surface-thick);
      color: var(--text);
      font-weight: 700;
      padding: 12px 14px;
      border-bottom: 1px solid var(--brand-sand);
    }}
    td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--hairline-soft);
      vertical-align: top;
    }}
    tr:nth-child(even) {{
      background: #fdfbf8;
    }}
    .dim-name {{
      font-weight: 700;
      color: var(--brand-gold);
      background: var(--surface-thick);
      white-space: nowrap;
    }}
    .dim-target {{
      font-weight: 700;
      color: var(--text);
      background: rgba(186, 149, 85, 0.05);
    }}
    .dim-verdict {{
      color: var(--text-2);
      font-size: 12.5px;
    }}

    /* شبكة المنافسين */
    .competitors-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
      margin-bottom: 32px;
    }}
    .competitor-card {{
      background: #fdfbf8;
      border: 1px solid var(--hairline-soft);
      border-radius: var(--radius-md);
      padding: 18px;
      transition: transform 0.2s;
    }}
    .competitor-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--brand-cream);
      padding-bottom: 10px;
    }}
    .competitor-num {{
      font-size: 11.5px;
      color: var(--brand-gold);
      font-weight: 700;
    }}
    .competitor-name {{
      font-size: 16px;
      font-weight: 700;
      color: var(--text);
    }}
    .competitor-link {{
      font-size: 12px;
      color: var(--brand-gold);
      text-decoration: none;
    }}
    .score-badge {{
      background: rgba(186, 149, 85, 0.12);
      border: 1px solid rgba(186, 149, 85, 0.3);
      border-radius: var(--radius-sm);
      padding: 4px 10px;
      text-align: center;
    }}
    .score-val {{
      font-size: 16px;
      font-weight: 900;
      color: var(--brand-gold);
      line-height: 1;
    }}
    .score-lbl {{
      font-size: 9.5px;
      color: var(--text-2);
    }}

    .field-group {{
      margin-bottom: 10px;
    }}
    .field-label {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--text-2);
      display: block;
      margin-bottom: 2px;
    }}
    .field-val {{
      font-size: 13px;
      color: var(--text);
    }}
    .italic-msg {{
      font-style: italic;
      color: var(--text-2);
    }}
    .badges-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 9px;
      border-radius: var(--radius-pill);
      font-size: 11.5px;
      font-weight: 600;
    }}
    .badge--gold {{
      background: rgba(186, 149, 85, 0.15);
      color: var(--brand-gold);
      border: 1px solid rgba(186, 149, 85, 0.35);
    }}
    .badge--sand {{
      background: rgba(211, 198, 180, 0.25);
      color: var(--brand-ink);
      border: 1px solid rgba(211, 198, 180, 0.5);
    }}
    .badge--red {{
      background: rgba(176, 52, 44, 0.12);
      color: #b0342c;
      border: 1px solid rgba(176, 52, 44, 0.3);
    }}

    .sw-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px dashed var(--brand-cream);
    }}
    .sw-box {{
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      font-size: 11.5px;
    }}
    .sw-box--green {{
      background: rgba(35, 116, 74, 0.08);
      border: 1px solid rgba(35, 116, 74, 0.2);
    }}
    .sw-box--green .sw-title {{
      color: #23744a;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .sw-box--red {{
      background: rgba(176, 52, 44, 0.08);
      border: 1px solid rgba(176, 52, 44, 0.2);
    }}
    .sw-box--red .sw-title {{
      color: #b0342c;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .sw-box ul {{
      padding-right: 14px;
      color: var(--text);
    }}

    /* شبكة SWOT */
    .swot-container {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
      margin-bottom: 30px;
    }}
    .swot-card {{
      background: #fdfbf8;
      border: 1px solid var(--hairline-soft);
      border-radius: var(--radius-md);
      padding: 16px;
    }}
    .swot-card--s {{ border-top: 4px solid #23744a; }}
    .swot-card--w {{ border-top: 4px solid #b0342c; }}
    .swot-card--o {{ border-top: 4px solid var(--brand-gold); }}
    .swot-card--t {{ border-top: 4px solid var(--brand-clay); }}
    .swot-card-title {{
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .swot-card ul {{
      padding-right: 18px;
      font-size: 13px;
      color: var(--text);
    }}

    /* الفجوات والتوصيات */
    .gaps-container, .recs-container {{
      display: grid;
      gap: 12px;
      margin-bottom: 30px;
    }}
    .gap-card, .rec-card {{
      background: #fdfbf8;
      border: 1px solid var(--hairline-soft);
      border-radius: var(--radius-md);
      padding: 14px 18px;
    }}
    .gap-header, .rec-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
      flex-wrap: wrap;
    }}
    .gap-title, .rec-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--text);
      flex: 1;
    }}
    .gap-desc, .rec-impact {{
      font-size: 13px;
      color: var(--text-2);
      margin-bottom: 8px;
    }}
    .gap-action-box, .rec-steps {{
      background: #faf7f2;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      font-size: 12.5px;
      color: var(--text);
    }}
    .rec-num {{
      width: 22px;
      height: 22px;
      background: var(--brand-gold);
      color: #ffffff;
      border-radius: 50%;
      text-align: center;
      line-height: 22px;
      font-size: 12px;
      font-weight: 700;
    }}
    .rec-steps ol {{
      padding-right: 20px;
      margin-top: 4px;
    }}

    /* استجابة الشاشات (Responsive) */
    @media (max-width: 768px) {{
      .report-paper {{
        padding: 16px 12px 24px;
      }}
      .company-hero {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .score-dial {{
        width: 100%;
      }}
      .swot-container {{
        grid-template-columns: 1fr;
      }}
      .competitors-grid {{
        grid-template-columns: 1fr;
      }}
      .sw-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    /* أنماط الطباعة الرسمية */
    @media print {{
      body {{
        padding: 0;
        background: #ffffff;
      }}
      .top-actions-bar {{
        display: none !important;
      }}
      .report-paper {{
        border: none;
        box-shadow: none;
        padding: 0;
      }}
    }}
  </style>
</head>
<body>
  <img src="{watermark_b64}" alt="" class="watermark-bg" aria-hidden="true">

  <div class="container">
    <!-- شريط الإجراءات والتحميل العلوي -->
    <div class="top-actions-bar">
      <div class="doc-status-badge">
        <span class="pulse-dot"></span>
        <span>تقرير معتمد لمنظومة أساس</span>
      </div>
      <div class="action-btns">
        <button class="btn btn--glass" onclick="window.print()">طباعة التقرير</button>
        <a class="btn btn--primary" href="/api/reports/{report.id}/pdf">تحميل كـ PDF رسمي</a>
      </div>
    </div>

    <!-- ورقة التقرير الرسمية بهوية أساس -->
    <div class="report-paper">
      
      <!-- 1. الترويسة الرسمية المعتمدة لأساس بالمقاس والنسبة الصحيحة -->
      <div class="official-header-banner">
        <img src="{header_b64}" alt="ترويسة أساس الرسمية">
      </div>

      <!-- 2. بيانات الشركة محل التحليل والتقييم -->
      <div class="company-hero">
        <div class="company-info">
          <div class="company-meta-row">
            <span class="badge badge--gold">{html.escape(target.industry)}</span>
            <span class="badge badge--sand">{html.escape(target.geographic_scope)}</span>
            <span class="badge badge--sand">تاريخ التقرير: {html.escape(report.created_at)}</span>
          </div>
          <h1 class="company-name">{html.escape(target.company_name)}</h1>
          {f'<a href="{html.escape(target.website_url)}" target="_blank" rel="noreferrer" class="company-url">{html.escape(target.website_url)} ↗</a>' if target.website_url else ''}
          <p style="font-size: 13.5px; color: var(--text-2); margin-top: 6px;">"{html.escape(target.marketing_message)}"</p>
        </div>
        <div class="score-dial">
          <div class="score-num">{report.overall_score}</div>
          <div class="score-label">التقييم التنافسي العام</div>
          <div style="font-size: 10px; color: var(--text-3);">من 10 نقاط</div>
        </div>
      </div>

      <!-- 3. الملخص التنفيذي الاستراتيجي -->
      <div class="section-title">الملخص التنفيذي الاستراتيجي (Executive Summary)</div>
      <div class="exec-summary-box">
        <img src="{robot_consultant}" alt="مستشار أساس" class="robot-thumb">
        <p class="exec-p">{html.escape(report.executive_summary)}</p>
      </div>

      <!-- 4. التحليل الرباعي SWOT -->
      <div class="section-title">التحليل الرباعي التنافسي (SWOT Analysis)</div>
      <div class="swot-container">
        <div class="swot-card swot-card--s">
          <div class="swot-card-title" style="color: #23744a;">نقاط القوة (Strengths)</div>
          <ul>{swot_s}</ul>
        </div>
        <div class="swot-card swot-card--w">
          <div class="swot-card-title" style="color: #b0342c;">نقاط الضعف (Weaknesses)</div>
          <ul>{swot_w}</ul>
        </div>
        <div class="swot-card swot-card--o">
          <div class="swot-card-title" style="color: var(--brand-gold);">الفرص الواعدة (Opportunities)</div>
          <ul>{swot_o}</ul>
        </div>
        <div class="swot-card swot-card--t">
          <div class="swot-card-title" style="color: var(--brand-clay);">التهديدات المحتملة (Threats)</div>
          <ul>{swot_t}</ul>
        </div>
      </div>

      <!-- 5. مصفوفة المقارنة المباشرة -->
      <div class="section-title">مصفوفة المقارنة التنافسية (8 محاور جوهرية)</div>
      <div class="table-container">
        <table>
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
            {''.join(table_rows_html)}
          </tbody>
        </table>
      </div>

      <!-- 6. المنافسون الفعليون في السوق -->
      <div class="section-title">تحليل المنافسين الميدانيين في السوق المستهدف</div>
      <div class="competitors-grid">
        {''.join(competitors_html)}
      </div>

      <!-- 7. الفجوات التنافسية -->
      <div class="section-title">الفجوات التسويقية والخدمية المرصودة (Market Gap Analysis)</div>
      <div class="gaps-container">
        {''.join(gaps_html)}
      </div>

      <!-- 8. التوصيات التنفيذية -->
      <div class="section-title">خارطة التوصيات الاستراتيجية (Actionable Roadmap)</div>
      <div class="recs-container">
        {''.join(recommendations_html)}
      </div>

      <!-- 9. التذييل الرسمي المعتمد لأساس بالمقاس والنسبة الصحيحة -->
      <div class="official-footer-banner">
        <img src="{footer_b64}" alt="تذييل أساس الرسمي">
        <div class="footer-note">
          تم استخراج وتحليل بيانات هذا التقرير التنافسي آلياً بواسطة طاقم وكلاء الذكاء الاصطناعي التابع لمنظومة أساس. كافة البيانات خاضعة لمعايير الحوكمة والسرية.
        </div>
      </div>

    </div>
  </div>
</body>
</html>"""
