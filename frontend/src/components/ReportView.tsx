import React, { useState } from 'react';
import { Card, Button, Icon } from '../asaas-ui';
import type { CompetitiveReport } from '../types';
import { getHtmlExportUrl, getPdfExportUrl } from '../api';

interface ReportViewProps {
  report: CompetitiveReport;
  onNewAnalysis: () => void;
}

export const ReportView: React.FC<ReportViewProps> = ({ report, onNewAnalysis }) => {
  const [activeSubTab, setActiveSubTab] = useState<'matrix' | 'swot' | 'gaps' | 'recs' | 'competitors' | 'target'>('matrix');

  const target = report.target_analysis;
  const c1 = report.competitors[0];
  const c2 = report.competitors[1];
  const c3 = report.competitors[2];

  const handlePrint = () => {
    window.print();
  };

  const openHtmlReport = () => {
    window.open(getHtmlExportUrl(report.id), '_blank');
  };

  const downloadPdf = () => {
    window.open(getPdfExportUrl(report.id), '_blank');
  };

  return (
    <div className="report-view-container">
      {/* خلفية العلامة المائية الرسمية لأساس */}
      <img
        src="/report_assets/image1.png"
        alt=""
        className="report-bg-watermark"
        aria-hidden="true"
      />

      {/* الترويسة الرسمية المعتمدة لقالب ورقة تقارير أساس بالمقاس الصحيح */}
      <div className="report-official-header-banner">
        <img
          src="/report_assets/image2.png"
          alt="ترويسة أساس الرسمية"
          className="report-banner-img"
        />
      </div>

      {/* البطاقة الرئيسية للتقرير والتصدير */}
      <div className="report-hero-card glass thick">
        <div className="report-hero-right">
          <div className="company-badge-row">
            <span className="badge badge--gold">{target.industry}</span>
            <span className="badge badge--sand">{target.geographic_scope}</span>
            <span className="report-date">تاريخ الإعداد: {report.created_at}</span>
          </div>
          <h2 className="company-title">
            {target.company_name}
            {target.website_url && (
              <a
                href={target.website_url}
                target="_blank"
                rel="noreferrer"
                className="site-link"
              >
                {target.website_url} ↗
              </a>
            )}
          </h2>
          <p className="marketing-quote">"{target.marketing_message}"</p>
        </div>

        <div className="report-hero-left">
          <div className="score-dial-box">
            <div className="score-number">{report.overall_score}</div>
            <div className="score-title">التقييم التنافسي العام</div>
            <div className="score-stars">من 10 نقاط</div>
          </div>

          <div className="report-quick-actions">
            <Button
              size="sm"
              variant="primary"
              icon="download"
              label="تحميل تقرير PDF الرسمي"
              onClick={downloadPdf}
            />
            <Button
              size="sm"
              variant="glass"
              icon="external"
              label="عرض التقرير بهوية أساس (HTML)"
              onClick={openHtmlReport}
            />
            <Button
              size="sm"
              variant="ghost"
              icon="printer"
              label="طباعة التقرير"
              onClick={handlePrint}
            />
          </div>
        </div>
      </div>

      {/* الملخص التنفيذي الاستراتيجي مع روبوت أساس الاستشاري */}
      <div className="exec-summary-card glass">
        <div className="card-head-row">
          <div className="head-title-group">
            <h3>الملخص التنفيذي الاستراتيجي (Executive Summary)</h3>
          </div>
          <span className="robot-mood-pill">
            <span className="pulse-dot" />
            اعتماد منظومة وكلاء أساس
          </span>
        </div>
        <div className="exec-summary-inner">
          <img
            src="/robot/08_ثقة.png"
            alt="مستشار أساس الذكي"
            className="exec-robot-avatar"
          />
          <div className="exec-text-wrap">
            <p className="exec-text">{report.executive_summary}</p>
          </div>
        </div>
      </div>

      {/* شريط التنقل النظيف بين أقسام التقرير بهوية وأيقونات أساس */}
      <div className="sub-tabs-bar glass">
        <button
          className={`sub-tab-btn ${activeSubTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('matrix')}
        >
          <Icon name="grid" className="sub-tab-svg" />
          <span>مصفوفة المقارنة التنافسية</span>
        </button>
        <button
          className={`sub-tab-btn ${activeSubTab === 'competitors' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('competitors')}
        >
          <Icon name="users" className="sub-tab-svg" />
          <span>ملفات المنافسين الـ 3</span>
        </button>
        <button
          className={`sub-tab-btn ${activeSubTab === 'swot' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('swot')}
        >
          <Icon name="briefcase" className="sub-tab-svg" />
          <span>التحليل الرباعي (SWOT)</span>
        </button>
        <button
          className={`sub-tab-btn ${activeSubTab === 'gaps' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('gaps')}
        >
          <Icon name="alert" className="sub-tab-svg" />
          <span>الفجوات التنافسية ({report.gap_analysis.length})</span>
        </button>
        <button
          className={`sub-tab-btn ${activeSubTab === 'recs' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('recs')}
        >
          <Icon name="trend" className="sub-tab-svg" />
          <span>التوصيات الاستراتيجية ({report.recommendations.length})</span>
        </button>
        <button
          className={`sub-tab-btn ${activeSubTab === 'target' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('target')}
        >
          <Icon name="search" className="sub-tab-svg" />
          <span>فحص الموقع الأصلي</span>
        </button>
      </div>

      {/* المحتوى بحسب القسم المختار */}
      <div className="sub-tab-content">
        {/* 1. جدول المقارنة التنافسي المباشر */}
        {activeSubTab === 'matrix' && (
          <Card className="section-card">
            <div className="section-header-info">
              <h3>مصفوفة المقارنة التنافسية المباشرة (Competitive Matrix)</h3>
              <p>مقارنة استراتيجية شاملة عبر 8 محاور جوهرية مع الحكم والفرصة المتاحة في السوق.</p>
              <div className="matrix-hint">💡 يمكنك سحب الجدول أفقياً للاطلاع على كامل مقارنات المنافسين والأحكام الاستراتيجية</div>
            </div>

            <div className="matrix-table-wrap">
              <table className="matrix-table">
                <thead>
                  <tr>
                    <th>المحور المقارن</th>
                    <th className="th-target">{target.company_name} (موقعك)</th>
                    <th>{c1?.name || 'المنافس الأول'}</th>
                    <th>{c2?.name || 'المنافس الثاني'}</th>
                    <th>{c3?.name || 'المنافس الثالث'}</th>
                    <th className="th-verdict">الحكم الاستراتيجي</th>
                  </tr>
                </thead>
                <tbody>
                  {report.comparison_table.dimensions.map((row, idx) => (
                    <tr key={idx}>
                      <td className="td-dimension">{row.dimension}</td>
                      <td className="td-target">{row.target_company}</td>
                      <td className="td-comp">{row.competitor_1}</td>
                      <td className="td-comp">{row.competitor_2}</td>
                      <td className="td-comp">{row.competitor_3}</td>
                      <td className="td-verdict">
                        <span className="verdict-tag">الحكم:</span> {row.strategic_verdict}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* 2. تفاصيل المنافسين الـ 3 */}
        {activeSubTab === 'competitors' && (
          <div className="competitors-cards-grid">
            {report.competitors.map((comp, idx) => (
              <Card key={idx} className="comp-full-card">
                <div className="comp-card-head">
                  <div className="comp-meta">
                    <span className="comp-rank">المنافس #{idx + 1}</span>
                    <h3 className="comp-name">{comp.name}</h3>
                    <a href={comp.website} target="_blank" rel="noreferrer" className="comp-url">
                      {comp.website} ↗
                    </a>
                  </div>
                  <div className="comp-score-box">
                    <div className="c-score">{comp.online_presence_score}</div>
                    <div className="c-lbl">التواجد الرقمي</div>
                  </div>
                </div>

                <div className="comp-card-body">
                  <div className="comp-prop">
                    <span className="p-label">الموقع في السوق:</span>
                    <span className="p-val">{comp.market_position}</span>
                  </div>

                  <div className="comp-prop">
                    <span className="p-label">الرسالة التسويقية:</span>
                    <span className="p-val italic">"{comp.marketing_message}"</span>
                  </div>

                  <div className="comp-prop">
                    <span className="p-label">الخدمات الرئيسية:</span>
                    <div className="comp-badges">
                      {comp.services.map((s, sIdx) => (
                        <span key={sIdx} className="badge badge--sand">{s}</span>
                      ))}
                    </div>
                  </div>

                  <div className="comp-prop">
                    <span className="p-label">نموذج التسعير:</span>
                    <span className="p-val gold">{comp.pricing_summary}</span>
                  </div>

                  <div className="comp-sw-row">
                    <div className="comp-sw-box green">
                      <div className="sw-title">نقاط القوة:</div>
                      <ul>
                        {comp.strengths.map((st, stIdx) => (
                          <li key={stIdx}>{st}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="comp-sw-box red">
                      <div className="sw-title">نقاط الضعف:</div>
                      <ul>
                        {comp.weaknesses.map((wk, wkIdx) => (
                          <li key={wkIdx}>{wk}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* 3. مصفوفة SWOT الرباعية */}
        {activeSubTab === 'swot' && (
          <Card className="section-card">
            <div className="section-header-info">
              <h3>التحليل الرباعي التنافسي (SWOT Analysis)</h3>
              <p>تحليل العوامل الداخلية للشركة والعوامل الخارجية في السوق الإقليمي.</p>
            </div>

            <div className="swot-matrix-grid">
              {/* نقاط القوة */}
              <div className="swot-card swot--s">
                <div className="swot-title">نقاط القوة (Strengths)</div>
                <ul className="swot-items-list">
                  {report.swot.strengths.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* نقاط الضعف */}
              <div className="swot-card swot--w">
                <div className="swot-title">نقاط الضعف (Weaknesses)</div>
                <ul className="swot-items-list">
                  {report.swot.weaknesses.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* الفرص السوقية */}
              <div className="swot-card swot--o">
                <div className="swot-title">الفرص السوقية (Opportunities)</div>
                <ul className="swot-items-list">
                  {report.swot.opportunities.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              {/* التهديدات التنافسية */}
              <div className="swot-card swot--t">
                <div className="swot-title">التهديدات التنافسية (Threats)</div>
                <ul className="swot-items-list">
                  {report.swot.threats.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        )}

        {/* 4. تحليل الفجوات التنافسية */}
        {activeSubTab === 'gaps' && (
          <div className="gaps-container">
            <div className="section-header-info">
              <h3>الفجوات التنافسية المستخرجة (Gap Analysis)</h3>
              <p>الفجوات الخدمية والتسويقية والسعرية التي تشكل فرص استحواذ ونمو فوري.</p>
            </div>

            <div className="gaps-cards-grid">
              {report.gap_analysis.map((gap, idx) => {
                const impactClass =
                  gap.impact_level === 'عالي'
                    ? 'badge--red'
                    : gap.impact_level === 'متوسط'
                    ? 'badge--gold'
                    : 'badge--sand';

                return (
                  <Card key={idx} className="gap-item-card">
                    <div className="gap-head-row">
                      <span className="badge badge--sand">{gap.category}</span>
                      <span className={`badge ${impactClass}`}>الأثر: {gap.impact_level}</span>
                    </div>

                    <h4 className="gap-item-title">{gap.title}</h4>
                    <p className="gap-item-desc">{gap.description}</p>

                    <div className="gap-action-box">
                      <div className="action-tag">الإجراء المطلوب لسد الفجوة:</div>
                      <div className="action-content">{gap.action_to_close}</div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* 5. التوصيات الاستراتيجية */}
        {activeSubTab === 'recs' && (
          <div className="recs-container">
            <div className="section-header-info">
              <h3>خارطة التوصيات الاستراتيجية وخطة العمل</h3>
              <p>إجراءات عملية مرتبة حسب الأولوية والأثر على الحصة السوقية والإيرادات.</p>
            </div>

            <div className="recs-cards-list">
              {report.recommendations.map((rec, idx) => {
                const prioBorder =
                  rec.priority === 'عاجل'
                    ? 'prio-border-urgent'
                    : rec.priority === 'مهم'
                    ? 'prio-border-important'
                    : 'prio-border-normal';

                return (
                  <Card key={idx} className={`rec-item-card ${prioBorder}`}>
                    <div className="rec-top-row">
                      <div className="rec-prio-badge">
                        أولوية: {rec.priority}
                      </div>
                      <div className="rec-effort-badge">
                        الجهد المطلوب: <strong>{rec.effort}</strong>
                      </div>
                    </div>

                    <h4 className="rec-item-heading">{idx + 1}. {rec.title}</h4>
                    
                    <div className="rec-impact-banner">
                      <strong>الأثر المتوقع:</strong> {rec.impact}
                    </div>

                    <div className="rec-steps-section">
                      <div className="steps-heading">خطوات التنفيذ الموصى بها:</div>
                      <ol className="steps-ordered-list">
                        {rec.action_steps.map((st, stIdx) => (
                          <li key={stIdx}>{st}</li>
                        ))}
                      </ol>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* 6. فحص الموقع الأصلي */}
        {activeSubTab === 'target' && (
          <Card className="section-card">
            <div className="section-header-info">
              <h3>بيانات الموقع المستهدف (مخرجات الوكيل الأول)</h3>
              <p>ما استخلصه الوكيل الذكي من نصوص وعروض وصفحات الموقع بدقة.</p>
            </div>

            <div className="target-profile-grid">
              <div className="profile-block">
                <h4 className="block-title">الخدمات والحلول المستخرجة</h4>
                <div className="services-details-list">
                  {target.services.map((s, idx) => (
                    <div key={idx} className="service-detail-item">
                      <div className="s-name">{s.name}</div>
                      <div className="s-desc">{s.description}</div>
                      {s.features.length > 0 && (
                        <div className="s-feats">
                          الميزات: {s.features.join(' · ')}
                        </div>
                      )}
                      {s.pricing_hint && (
                        <div className="s-price">السعر: {s.pricing_hint}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="profile-block">
                <h4 className="block-title">الجمهور المستهدف ونقاط التميز</h4>
                <div className="audience-box">
                  <strong>توصيف الجمهور:</strong> {target.target_audience}
                </div>

                <div className="usps-box">
                  <strong>نقاط البيع الفريدة:</strong>
                  <ul>
                    {target.unique_selling_points.map((usp, idx) => (
                      <li key={idx}>{usp}</li>
                    ))}
                  </ul>
                </div>

                {target.pricing && target.pricing.length > 0 && (
                  <div className="pricing-box">
                    <strong>الباقات ونماذج التسعير:</strong>
                    {target.pricing.map((p, idx) => (
                      <div key={idx} className="plan-chip">
                        <span className="p-title">{p.plan_name}:</span>
                        <span className="p-cost">{p.price}</span>
                        <span className="p-cycle">({p.billing_cycle})</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* التذييل الرسمي المعتمد لقالب ورقة تقارير أساس بالمقاس الصحيح */}
      <div className="report-official-footer-banner">
        <img
          src="/report_assets/image3.png"
          alt="تذييل أساس الرسمي"
          className="report-banner-img"
        />
        <div className="report-footer-note">
          تم استخراج وتحليل بيانات هذا التقرير التنافسي آلياً بواسطة طاقم وكلاء الذكاء الاصطناعي لمنظومة أساس. كافة البيانات محفوظة ومحمية.
        </div>
      </div>

      {/* زر بدء تحليل موقع آخر في الأسفل */}
      <div className="report-bottom-cta">
        <Button
          variant="primary"
          size="md"
          label="تحليل موقع أو شركة أخرى"
          onClick={onNewAnalysis}
        />
      </div>
    </div>
  );
};
