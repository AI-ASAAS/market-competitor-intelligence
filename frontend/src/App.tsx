import { useState, useEffect } from 'react';
import './asaas-ui/styles/index.css';
import './App.css';
import { Ambient, AssistantWidget, type AssistantMessage } from './asaas-ui';
import { Header } from './components/Header';
import { NewAnalysisForm } from './components/NewAnalysisForm';
import { ReportView } from './components/ReportView';
import { ReportsHistory } from './components/ReportsHistory';
import { SettingsModal } from './components/SettingsModal';
import type { CompetitiveReport } from './types';
import { fetchReports, fetchReportById } from './api';

const DEFAULT_KEY = '';
const DEFAULT_TAVILY_KEY = '';
const DEFAULT_MODEL = 'nvidia/nemotron-3.5-lightning:free';

export function App() {
  const [activeTab, setActiveTab] = useState<'new' | 'report' | 'history'>('new');
  const [activeReport, setActiveReport] = useState<CompetitiveReport | null>(null);
  
  // مفاتيح الـ API ونموذج الذكاء الاصطناعي
  const [tavilyApiKey, setTavilyApiKey] = useState<string>(() => localStorage.getItem('asaas_tavily_key') || DEFAULT_TAVILY_KEY);
  const [llmApiKey, setLlmApiKey] = useState<string>(() => localStorage.getItem('asaas_llm_key') || DEFAULT_KEY);
  const [selectedModel, setSelectedModel] = useState<string>(() => localStorage.getItem('asaas_selected_model') || DEFAULT_MODEL);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // عند التحميل الأولي، فحص أحدث تقرير لعرضه
  useEffect(() => {
    fetchReports()
      .then((reports) => {
        if (reports.length > 0) {
          fetchReportById(reports[0].id).then((rep) => {
            setActiveReport(rep);
          }).catch(() => {});
        }
      })
      .catch(() => {});
  }, []);

  const handleReportGenerated = (report: CompetitiveReport) => {
    setActiveReport(report);
    setActiveTab('report');
  };

  const handleSelectReport = (report: CompetitiveReport) => {
    setActiveReport(report);
    setActiveTab('report');
  };

  // المساعد الذكي
  const askAssistant = async (messages: AssistantMessage[]) => {
    const lastUserMsg = messages[messages.length - 1]?.content || '';
    
    if (!activeReport) {
      return {
        reply: 'أهلاً بك! يمكنك بدء فحص موقعك أو نصوص شركتك أولاً عبر تبويب "تحليل جديد"، وسأقوم بعدها بالإجابة عن كافة استفساراتك بخصوص المنافسين والفجوات والتوصيات.',
      };
    }

    const target = activeReport.target_analysis;
    const comps = activeReport.competitors;
    const compNames = comps.map((c) => c.name).join('، ');

    const lower = lastUserMsg.toLowerCase();
    let reply = '';

    if (lower.includes('فجو') || lower.includes('gap')) {
      const topGap = activeReport.gap_analysis[0];
      reply = `أبرز فجوة تنافسية تم رصدها هي «${topGap.title}» في محور (${topGap.category}) بأثر ${topGap.impact_level}.\n\nالوصف: ${topGap.description}\n\nالإجراء الموصى به: ${topGap.action_to_close}`;
    } else if (lower.includes('سعر') || lower.includes('اسعار') || lower.includes('باق')) {
      reply = `بناءً على نتائج المقارنة:\n- نموذج تسعير شركتك: ${target.pricing?.[0]?.price || 'مرن / عند الطلب'}\n- المنافسون: ${comps.map((c) => `${c.name} (${c.pricing_summary})`).join(' · ')}\n\nتوصية الوكيل: عرض باقات واضحة ومحددة يمنحك أفضلية مباشرة لأن المنافسين يفرضون التواصل المسبق.`;
    } else if (lower.includes('منافس') || lower.includes('مين')) {
      reply = `أبرز 3 منافسين تم رصدهم في ${target.geographic_scope} هم:\n1. ${comps[0]?.name || ''} (قوة التواجد: ${comps[0]?.online_presence_score}/10)\n2. ${comps[1]?.name || ''} (قوة التواجد: ${comps[1]?.online_presence_score}/10)\n3. ${comps[2]?.name || ''} (قوة التواجد: ${comps[2]?.online_presence_score}/10)\n\nيمكنك استعراض جدول المقارنة التفصيلي كاملاً في تبويب "التقرير التنافسي".`;
    } else if (lower.includes('توصي') || lower.includes('نصيح') || lower.includes('خطوة')) {
      const topRec = activeReport.recommendations[0];
      reply = `أهم توصية استراتيجية ذات أولوية عاجلة:\n«${topRec.title}»\n\nالأثر المتوقع: ${topRec.impact}\nخطوات التنفيذ:\n${topRec.action_steps.map((s, i) => `${i + 1}. ${s}`).join('\n')}`;
    } else {
      reply = `أنا هنا لمساعدتك في استكشاف تفاصيل تقرير «${target.company_name}» التنافسي أمام المنافسين (${compNames}).\nالتقييم التنافسي لشركتك هو ${activeReport.overall_score}/10. اسألني عن الفجوات، الأسعار، أو التوصيات وسأجيبك فوراً.`;
    }

    return { reply };
  };

  return (
    <div className="app-container">
      {/* خلفية أساس الانسيابية */}
      <Ambient />

      {/* الرأس النظيف بالهوية البصرية */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasActiveReport={!!activeReport}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* المحتوى الرئيسي */}
      <main className="main-content">
        {activeTab === 'new' && (
          <NewAnalysisForm
            onReportGenerated={handleReportGenerated}
            tavilyApiKey={tavilyApiKey}
            llmApiKey={llmApiKey}
            selectedModel={selectedModel}
          />
        )}

        {activeTab === 'report' && activeReport && (
          <ReportView
            report={activeReport}
            onNewAnalysis={() => setActiveTab('new')}
          />
        )}

        {activeTab === 'history' && (
          <ReportsHistory
            onSelectReport={handleSelectReport}
            onNewAnalysis={() => setActiveTab('new')}
          />
        )}
      </main>

      {/* التذييل */}
      <footer className="app-footer">
        <p>
          مهندس تحليل الأعمال والمنافسين · منظومة أساس للذكاء الاصطناعي (ASAAS AI) © {new Date().getFullYear()}
        </p>
      </footer>

      {/* المساعد الذكي العائم */}
      <AssistantWidget
        user={{ id: 'current-user', displayName: 'مهندس الأعمال' }}
        title="مساعد الذكاء التنافسي"
        subtitle="اسأل الروبوت عن منافسيك وفجوات السوق"
        intro="مرحباً بك! أنا روبوت أساس لتحليل المنافسين. اسألني عن أي نقطة في التقرير أو كيفية التفوق على منافسيك."
        disclaimer="يجيب المساعد من واقع بيانات التقرير التنافسي."
        suggestions={[
          'ما هي أكبر فجوة تسويقية تم رصدها؟',
          'كيف أتفوق على المنافسين في الأسعار؟',
          'من هم أبرز 3 منافسين في السوق؟',
          'ما هي التوصية الأكثر إلحاحاً الآن؟',
        ]}
        ask={askAssistant}
      />

      {/* نافذة الإعدادات ومفاتيح الـ API */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        tavilyApiKey={tavilyApiKey}
        setTavilyApiKey={setTavilyApiKey}
        llmApiKey={llmApiKey}
        setLlmApiKey={setLlmApiKey}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />
    </div>
  );
}

export default App;
