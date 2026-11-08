import React, { useState, useEffect } from 'react';
import { Modal, Button, TextInput, Select } from '../asaas-ui';
import { checkSystemStatus, testApiKeys, type TestKeysResult } from '../api';
import type { SystemStatus } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  tavilyApiKey: string;
  setTavilyApiKey: (key: string) => void;
  llmApiKey: string;
  setLlmApiKey: (key: string) => void;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
}

const SUGGESTED_MODELS = [
  { value: 'nvidia/nemotron-3.5-lightning:free', label: 'Nvidia Nemotron 3.5 Lightning (مجاني وسريع وفائق الذكاء — مستحسن)' },
  { value: 'google/gemini-2.5-flash', label: 'Google Gemini 2.5 Flash (سريع ودقيق)' },
  { value: 'anthropic/claude-3.5-sonnet', label: 'Anthropic Claude 3.5 Sonnet (أعلى عمق استراتيجي)' },
  { value: 'openai/gpt-4o-mini', label: 'OpenAI GPT-4o Mini (اقتصادي وسريع)' },
  { value: 'deepseek/deepseek-chat', label: 'DeepSeek V3 (قوي في العربية والأعمال)' },
  { value: 'meta-llama/llama-3.3-70b-instruct', label: 'Llama 3.3 70B (مفتوح المصدر ومتقدم)' },
];

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  tavilyApiKey,
  setTavilyApiKey,
  llmApiKey,
  setLlmApiKey,
  selectedModel,
  setSelectedModel,
}) => {
  const [tavilyInput, setTavilyInput] = useState(tavilyApiKey);
  const [llmInput, setLlmInput] = useState(llmApiKey);
  const [modelInput, setModelInput] = useState(selectedModel);
  const [serverStatus, setServerStatus] = useState<SystemStatus | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestKeysResult | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setTavilyInput(tavilyApiKey);
      setLlmInput(llmApiKey);
      setModelInput(selectedModel);
      setTestResult(null);
      setTestError(null);
      checkSystemStatus()
        .then(setServerStatus)
        .catch(() => {});
    }
  }, [isOpen, tavilyApiKey, llmApiKey, selectedModel]);

  const handleTestKeys = async () => {
    setTesting(true);
    setTestResult(null);
    setTestError(null);
    try {
      const result = await testApiKeys({
        llm_api_key: llmInput.trim() || undefined,
        selected_model: modelInput,
        tavily_api_key: tavilyInput.trim() || undefined,
      });
      setTestResult(result);
    } catch (err: any) {
      setTestError(err.message || 'فشل فحص الاتصال بالمفاتيح');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    setTavilyApiKey(tavilyInput.trim());
    setLlmApiKey(llmInput.trim());
    setSelectedModel(modelInput);
    localStorage.setItem('asaas_tavily_key', tavilyInput.trim());
    localStorage.setItem('asaas_llm_key', llmInput.trim());
    localStorage.setItem('asaas_selected_model', modelInput);
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 700);
  };

  const resetToDefaultKey = () => {
    setLlmInput('');
  };

  if (!isOpen) return null;

  return (
    <Modal open={isOpen} onClose={onClose} title="إعدادات مفاتيح الربط البرمجي (API)">
      <div className="settings-modal-body">
        <p className="settings-intro">
          يمكنك تخصيص أو تعديل مفاتيح الـ API واختيار النموذج اللغوي المفضل. يتم حفظ هذه الإعدادات محلياً في متصفحك.
        </p>

        {/* حالة الخدمة */}
        {serverStatus && (
          <div className="status-box glass">
            <div className="status-item">
              <span>أداة Tavily API:</span>
              <span className={`badge ${serverStatus.tavily_configured ? 'badge--gold' : 'badge--sand'}`}>
                {serverStatus.tavily_configured ? 'متصل' : 'محرك البحث الاستدلالي المدمج'}
              </span>
            </div>
            <div className="status-item">
              <span>النموذج اللغوي (LLM):</span>
              <span className="badge badge--gold">
                OpenRouter مفعّل
              </span>
            </div>
          </div>
        )}

        {/* اختيار النموذج */}
        <div className="settings-field">
          <label className="field-label">
            النموذج اللغوي المقترح للتحليل
          </label>
          <Select
            value={modelInput}
            onChange={(e) => setModelInput(e.target.value)}
          >
            {SUGGESTED_MODELS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </Select>
          <span className="field-hint">
            اختر النموذج الأنسب لك، أو اعتمد على النموذج الافتراضي الموصى به من أساس.
          </span>
        </div>

        {/* مفتاح OpenRouter */}
        <div className="settings-field">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="field-label">
              مفتاح OpenRouter API
            </label>
            <button
              type="button"
              className="text-btn"
              onClick={resetToDefaultKey}
              style={{ fontSize: '11px', color: 'var(--gold)', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              استعادة المفتاح الافتراضي
            </button>
          </div>
          <TextInput
            type="password"
            placeholder="sk-or-v1-..."
            value={llmInput}
            onChange={(e) => setLlmInput(e.target.value)}
          />
          <span className="field-hint">
            مفتاح OpenRouter معتمد وقابل للتعديل من قبل أي مستخدم في أي وقت.
          </span>
        </div>

        {/* مفتاح Tavily */}
        <div className="settings-field">
          <label className="field-label">
            مفتاح Tavily API (اختياري)
          </label>
          <TextInput
            type="password"
            placeholder="tvly-xxxxxxxxxxxxxxxxxxxx"
            value={tavilyInput}
            onChange={(e) => setTavilyInput(e.target.value)}
          />
          <span className="field-hint">
            للبحث الحي في الويب. في حال تركه فارغاً، يعتمد النظام على المحرك التنافسي المدمج.
          </span>
        </div>

        {/* نتيجة فحص الاتصال الحية */}
        {testResult && (
          <div className={`test-result-box ${testResult.llm_valid ? 'test-result--success' : 'test-result--error'}`}>
            <div className="test-header-line">
              <span className="test-title">نتيجة فحص الاتصال المباشر:</span>
              <span className={`badge ${testResult.llm_valid ? 'badge--gold' : 'badge--red'}`}>
                {testResult.llm_valid ? 'الاتصال نشط وسليم' : 'تعذر الاتصال'}
              </span>
            </div>
            <p className="test-detail-p">{testResult.llm_message}</p>
            {testResult.tavily_message && (
              <p className="test-detail-tavily">{testResult.tavily_message}</p>
            )}
          </div>
        )}

        {testError && (
          <div className="error-alert">
            <span>{testError}</span>
          </div>
        )}

        {savedSuccess && (
          <div className="success-banner">
            تم حفظ الإعدادات بنجاح
          </div>
        )}

        <div className="modal-actions-row">
          <Button variant="ghost" label="إلغاء" onClick={onClose} />
          <Button
            variant="glass"
            icon="check"
            label={testing ? 'جارٍ فحص الاتصال…' : 'فحص الاتصال بالمفاتيح'}
            onClick={handleTestKeys}
            disabled={testing}
          />
          <Button variant="primary" label="حفظ التغييرات" onClick={handleSave} />
        </div>
      </div>
    </Modal>
  );
};
