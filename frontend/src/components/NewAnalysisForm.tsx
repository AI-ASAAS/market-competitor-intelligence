import React, { useState } from 'react';
import { Card, Button, TextInput, TextArea, Select, Icon } from '../asaas-ui';
import type { CompetitiveReport } from '../types';
import { analyzeByUrl, analyzeByText } from '../api';

interface NewAnalysisFormProps {
  onReportGenerated: (report: CompetitiveReport) => void;
  tavilyApiKey: string;
  llmApiKey: string;
  selectedModel: string;
}

const REGION_OPTIONS = [
  { value: 'السوق العربي بشكل عام', label: 'السوق العربي بشكل عام' },
  { value: 'المملكة العربية السعودية والخليج', label: 'المملكة العربية السعودية والخليج العربي' },
  { value: 'مصر وشمال أفريقيا', label: 'مصر ودول شمال أفريقيا' },
  { value: 'اليمن والمنطقة الجنوبية', label: 'اليمن والمنطقة الجنوبية' },
  { value: 'السوق العالمي (International)', label: 'السوق العالمي (International)' },
];

export const NewAnalysisForm: React.FC<NewAnalysisFormProps> = ({
  onReportGenerated,
  tavilyApiKey,
  llmApiKey,
  selectedModel,
}) => {
  const [mode, setMode] = useState<'url' | 'text'>('url');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [geographicScope, setGeographicScope] = useState('السوق العربي بشكل عام');
  const [extraContext, setExtraContext] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    { title: 'سحب محتوى الموقع', desc: 'استخراج العناوين والنصوص والبيانات الوصفية' },
    { title: 'الوكيل الأول: تحليل المحتوى', desc: 'تحديد الخدمات والجمهور والرسالة التسويقية والأسعار' },
    { title: 'الوكيل الثاني: استكشاف المنافسين', desc: 'مسح الويب وسحب بيانات 3 منافسين مباشرين' },
    { title: 'الوكيل الثالث: المقارنة وSWOT والفجوات', desc: 'مقارنة 8 محاور واستخراج الفجوات التنافسية والتوصيات' },
    { title: 'صياغة التقرير التنافسي', desc: 'توليد المخرجات النهائية وجداول التحليل الاستراتيجي' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setCurrentStep(1);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 2200);

    try {
      let report: CompetitiveReport;
      if (mode === 'url') {
        if (!url.trim()) throw new Error('يرجى إدخال رابط الموقع المراد تحليله');
        report = await analyzeByUrl({
          url: url.trim(),
          geographic_scope: geographicScope,
          extra_context: extraContext.trim() || undefined,
          tavily_api_key: tavilyApiKey || undefined,
          llm_api_key: llmApiKey || undefined,
          selected_model: selectedModel || undefined,
        });
      } else {
        if (!text.trim() || text.trim().length < 20) {
          throw new Error('يرجى إدخال نص كافٍ عن الموقع والخدمات (20 حرفاً على الأقل)');
        }
        report = await analyzeByText({
          content: text.trim(),
          company_name: companyName.trim() || undefined,
          geographic_scope: geographicScope,
          tavily_api_key: tavilyApiKey || undefined,
          llm_api_key: llmApiKey || undefined,
          selected_model: selectedModel || undefined,
        });
      }

      setCurrentStep(5);
      clearInterval(stepInterval);
      setTimeout(() => {
        onReportGenerated(report);
      }, 500);
    } catch (err: any) {
      clearInterval(stepInterval);
      setError(err.message || 'حدث خطأ أثناء إجراء التحليل التنافسي');
      setLoading(false);
    }
  };

  const loadSampleData = () => {
    setMode('text');
    setCompanyName('منصة أساس للذكاء الرقمي');
    setText(`نحن منصة أساس (ASAAS AI) — منظومة عربية متخصصة في تمكين الشركات ورواد الأعمال من بناء ونشر وكلاء الذكاء الاصطناعي وأتمتة العمليات التجارية.
نقدم:
1. بناء الوكلاء الذكيين المخصصين لخدمة العملاء وأبحاث السوق.
2. منصة تحليل البيانات والتكامل مع قواعد البيانات السحابية وبوابات الدفع.
3. استشارات التحول الرقمي وتدريب فرق العمل على أدوات الذكاء التوليدي.
باقات الأسعار:
- باقة المبتكرين: 499 ر.س شهرياً تشمل بناء حتى 3 وكلاء ذكيين.
- باقة الشركات: 1,899 ر.س شهرياً مع وكلاء غير محدودين وتكامل API ودعم فني مخصص.
رسالتنا: جعل الذكاء الاصطناعي في متناول كل شركة عربية لرفع الإنتاجية بمقدار 5 أضعاف.`);
    setGeographicScope('السوق العربي بشكل عام');
  };

  return (
    <div className="new-analysis-wrapper">
      {/* قسم الترحيب بالهوية البصرية النظيفة */}
      <div className="hero-section glass">
        <div className="hero-text">
          <div className="hero-badge">
            منظومة الذكاء التنافسي المعتمدة · أساس AI
          </div>
          <h2 className="hero-heading">
            تحليل الموقع والمنافسين <span className="gold-gradient">واستخراج الفجوات التنافسية</span>
          </h2>
          <p className="hero-desc">
            أدخل رابط أي موقع أو نصوص خدماته، ليقوم طاقم الوكلاء الذكيين بفحص العرض القيمي والأسعار، واستكشاف أبرز 3 منافسين في الويب، مع إعداد مصفوفة مقارنة شاملة وتحليل SWOT وخطة عمل تنفيذية.
          </p>
          <div className="hero-cta-row">
            <button
              type="button"
              className="sample-btn"
              onClick={loadSampleData}
            >
              <Icon name="sparkle" className="btn-icon-svg" />
              <span>تحميل نموذج بيانات استرشادي</span>
            </button>
          </div>
        </div>

        <div className="hero-robot">
          <img
            src="/robot/01_ترحيب.png"
            alt="روبوت أساس"
            className="robot-mascot-img"
          />
        </div>
      </div>

      {/* نموذج الإدخال الرئيسي */}
      <div className="form-card-container">
        <Card className="analysis-card">
          {/* محول النمط النظيف المتناسق بهوية أساس */}
          <div className="mode-toggle-wrap">
            <button
              type="button"
              className={`mode-btn ${mode === 'url' ? 'active' : ''}`}
              onClick={() => setMode('url')}
              disabled={loading}
            >
              <Icon name="search" className="btn-icon-svg" />
              <span>تحليل عبر رابط الموقع (URL)</span>
            </button>
            <button
              type="button"
              className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
              onClick={() => setMode('text')}
              disabled={loading}
            >
              <Icon name="edit" className="btn-icon-svg" />
              <span>تحليل عبر لصق نصوص المحتوى</span>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="analysis-form">
            {mode === 'url' ? (
              <div className="form-field-group">
                <label className="field-label">رابط الموقع الإلكتروني المستهدف</label>
                <TextInput
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={loading}
                />
                <span className="field-hint">
                  يقوم الوكيل بسحب النصوص والعناوين والخدمات وتحليلها آلياً.
                </span>
              </div>
            ) : (
              <>
                <div className="form-row">
                  <div className="form-field-group flex-1">
                    <label className="field-label">اسم الشركة أو الموقع (اختياري)</label>
                    <TextInput
                      placeholder="مثال: شركة نمو، منصة الأفق..."
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                </div>
                <div className="form-field-group">
                  <label className="field-label">نصوص المحتوى والخدمات</label>
                  <TextArea
                    rows={6}
                    placeholder="الصق نصوص الموقع، صفحات الخدمات، الأسعار، أو نبذة عن نشاط الشركة..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    disabled={loading}
                  />
                  <span className="field-hint">
                    تساعد التفاصيل الواضحة الوكلاء على بناء مقارنة تنافسية أكثر دقة وعمقاً.
                  </span>
                </div>
              </>
            )}

            <div className="form-row">
              <div className="form-field-group flex-1">
                <label className="field-label">النطاق الجغرافي للبحث التنافسي</label>
                <Select
                  value={geographicScope}
                  onChange={(e) => setGeographicScope(e.target.value)}
                  disabled={loading}
                >
                  {REGION_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </div>

              {mode === 'url' && (
                <div className="form-field-group flex-1">
                  <label className="field-label">ملاحظات توجيهية للوكيل (اختياري)</label>
                  <TextInput
                    placeholder="مثال: التركيز على باقات الاشتراك والشركات المنافسة..."
                    value={extraContext}
                    onChange={(e) => setExtraContext(e.target.value)}
                    disabled={loading}
                  />
                </div>
              )}
            </div>

            {error && (
              <div className="error-alert">
                <span>{error}</span>
              </div>
            )}

            {/* شريط تقدم الوكلاء النظيف والأنيق */}
            {loading && (
              <div className="stepper-box">
                <div className="stepper-title">
                  <span className="spinner-dot"></span> جاري معالجة التحليل عبر طاقم الوكلاء الذكيين...
                </div>
                <div className="steps-list">
                  {steps.map((st, idx) => {
                    const stepNum = idx + 1;
                    const isDone = currentStep > stepNum;
                    const isCurrent = currentStep === stepNum;
                    return (
                      <div
                        key={idx}
                        className={`step-item ${isDone ? 'done' : ''} ${isCurrent ? 'current' : ''}`}
                      >
                        <div className="step-circle">
                          {isDone ? '✓' : stepNum}
                        </div>
                        <div className="step-content">
                          <div className="step-h">{st.title}</div>
                          <div className="step-p">{st.desc}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="form-actions">
              <Button
                type="submit"
                variant="primary"
                size="md"
                icon="trend"
                label={loading ? 'جاري استخبارات المنافسين والتحليل…' : 'بدء التحليل والبحث التنافسي الذكي'}
                disabled={loading}
              />
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};
