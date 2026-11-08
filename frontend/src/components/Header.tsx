import React from 'react';
import { Button, useTheme, Icon } from '../asaas-ui';

interface HeaderProps {
  activeTab: 'new' | 'report' | 'history';
  setActiveTab: (tab: 'new' | 'report' | 'history') => void;
  hasActiveReport: boolean;
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  hasActiveReport,
  onOpenSettings,
}) => {
  const [theme, toggleTheme] = useTheme();

  return (
    <header className="app-header-unified">
      <div className="header-container">
        
        {/* 1. الشعار الرسمي والهوية البصرية لأساس */}
        <div className="brand-section" onClick={() => setActiveTab('new')} role="button" tabIndex={0}>
          <div className="brand__mark" aria-label="شعار أساس الرسمي" />
          <div className="brand-meta">
            <div className="brand-headline">
              <span className="brand-title-main">مهندس تحليل الأعمال والمنافسين</span>
              <span className="brand-badge-version">ذكاء اصطناعي</span>
            </div>
            <div className="brand-tagline">
              Market & Competitor Intelligence Specialist · أساس ASAAS
            </div>
          </div>
        </div>

        {/* 2. شريط التبويبات الانسيابي (Harmonious Liquid Navigation) */}
        <nav className="unified-nav-pill" aria-label="شريط التنقل الرئيسي">
          <button
            type="button"
            className={`unified-tab-btn ${activeTab === 'new' ? 'active' : ''}`}
            onClick={() => setActiveTab('new')}
          >
            <Icon name="sparkle" className="unified-tab-icon" />
            <span className="tab-label">تحليل جديد</span>
          </button>

          {hasActiveReport && (
            <button
              type="button"
              className={`unified-tab-btn ${activeTab === 'report' ? 'active' : ''}`}
              onClick={() => setActiveTab('report')}
            >
              <span className="report-ready-dot" title="التقرير مكتمل" />
              <Icon name="trend" className="unified-tab-icon" />
              <span className="tab-label">التقرير التنافسي</span>
            </button>
          )}

          <button
            type="button"
            className={`unified-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <Icon name="clock" className="unified-tab-icon" />
            <span className="tab-label">سجل التقارير</span>
          </button>
        </nav>

        {/* 3. أدوات التحكم وفاحص الاتصال بالمحركات */}
        <div className="unified-actions">
          <button
            type="button"
            className="engine-status-pill"
            onClick={onOpenSettings}
            title="فحص وإعداد مفاتيح Tavily وOpenRouter"
          >
            <span className="engine-pulse-dot" />
            <span className="engine-status-text">المحركات نشطة</span>
            <span className="engine-chip">Tavily + AI</span>
            <Icon name="settings" className="engine-gear-icon" />
          </button>

          <Button
            size="sm"
            variant="ghost"
            icon={theme === 'dark' ? 'sun' : 'moon'}
            iconOnly
            label={theme === 'dark' ? 'التبديل إلى الوضع النهاري' : 'التبديل إلى الوضع الليلي'}
            onClick={toggleTheme}
            className="theme-toggle-btn"
          />
        </div>

      </div>
    </header>
  );
};
