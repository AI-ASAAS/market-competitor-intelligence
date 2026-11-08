import React, { useEffect, useState } from 'react';
import { Card, Button } from '../asaas-ui';
import type { ReportSummaryItem, CompetitiveReport } from '../types';
import { fetchReports, fetchReportById, deleteReportById, getHtmlExportUrl, getPdfExportUrl } from '../api';

interface ReportsHistoryProps {
  onSelectReport: (report: CompetitiveReport) => void;
  onNewAnalysis: () => void;
}

export const ReportsHistory: React.FC<ReportsHistoryProps> = ({
  onSelectReport,
  onNewAnalysis,
}) => {
  const [reports, setReports] = useState<ReportSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchReports();
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'فشل في تحميل سجل التقارير');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpen = async (id: string) => {
    try {
      setLoading(true);
      const report = await fetchReportById(id);
      onSelectReport(report);
    } catch (err: any) {
      alert(err.message || 'فشل في فتح التقرير');
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`هل أنت متأكد من حذف تقرير «${name}» نهائياً؟`)) return;
    try {
      setDeletingId(id);
      await deleteReportById(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      alert(err.message || 'تعذر حذف التقرير');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="history-wrapper">
      <div className="history-header-row">
        <div>
          <h2 className="history-title">سجل التقارير التنافسية السابقة</h2>
          <p className="history-subtitle">
            جميع التحليلات التنافسية المحفوظة في قاعدة بيانات النظام — متاحة للعرض المباشر والتحميل بصيغتي PDF الرسمي و HTML الفاخر في أي وقت.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          label="تحليل جديد"
          onClick={onNewAnalysis}
        />
      </div>

      {loading && reports.length === 0 ? (
        <Card className="loading-card">
          <div className="loading-spinner"></div>
          <p>جاري استرجاع التقارير من قاعدة البيانات...</p>
        </Card>
      ) : error ? (
        <div className="error-alert">
          <span>{error}</span>
          <Button size="sm" variant="glass" label="إعادة المحاولة" onClick={loadData} />
        </div>
      ) : reports.length === 0 ? (
        <Card className="empty-history-card">
          <div className="empty-robot">
            <img src="/robot/03_تفكير.png" alt="لا توجد تقارير" className="empty-robot-img" />
          </div>
          <h3>لا توجد تقارير تنافسية محفوظة بعد</h3>
          <p>ابدأ الآن بتحليل موقعك أو لصق نصوص شركتك لاكتشاف المنافسين وبناء مصفوفة المقارنة التنافسية.</p>
          <Button
            variant="primary"
            size="md"
            label="ابدأ أول تحليل تنافسي"
            onClick={onNewAnalysis}
          />
        </Card>
      ) : (
        <div className="reports-grid">
          {reports.map((item) => (
            <Card key={item.id} className="history-item-card">
              <div className="h-card-top">
                <span className="badge badge--gold">{item.industry}</span>
                <span className="h-score">التقييم: {item.overall_score}/10</span>
              </div>

              <h3 className="h-company-name">{item.company_name}</h3>
              
              {item.url && (
                <div className="h-url">
                  <a href={item.url} target="_blank" rel="noreferrer">
                    {item.url} ↗
                  </a>
                </div>
              )}

              <div className="h-comps-preview">
                <span className="comps-label">المنافسون المكتشفون:</span>
                <div className="comps-tags">
                  {item.competitors_names.map((cName, idx) => (
                    <span key={idx} className="badge badge--sand">
                      {cName}
                    </span>
                  ))}
                </div>
              </div>

              <div className="h-date-row">
                <span>تاريخ الإعداد: {item.created_at}</span>
              </div>

              <div className="h-actions-row">
                <Button
                  size="sm"
                  variant="primary"
                  label="عرض التقرير"
                  onClick={() => handleOpen(item.id)}
                />
                <a
                  href={getPdfExportUrl(item.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-link btn-link--gold"
                >
                  PDF رسمي
                </a>
                <a
                  href={getHtmlExportUrl(item.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-link"
                >
                  عرض HTML ↗
                </a>
                <Button
                  size="sm"
                  variant="ghost"
                  icon="trash"
                  iconOnly={deletingId !== item.id}
                  label={deletingId === item.id ? 'حذف...' : 'حذف التقرير'}
                  onClick={() => handleDelete(item.id, item.company_name)}
                  disabled={deletingId === item.id}
                />
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
