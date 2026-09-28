import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { UrlInputForm } from './components/UrlInputForm';
import { MediaPreviewCard } from './components/MediaPreviewCard';
import { MultiMediaGrid } from './components/MultiMediaGrid';
import { DownloadProgressModal } from './components/DownloadProgressModal';
import { DownloadHistoryDrawer } from './components/DownloadHistoryDrawer';
import { FeaturesSection } from './components/FeaturesSection';
import { LegalNotice } from './components/LegalNotice';
import { Toast } from './components/Toast';
import { useMediaAnalyzer } from './hooks/useMediaAnalyzer';
import { useDownloadManager } from './hooks/useDownloadManager';

export function App() {
  const {
    url,
    setUrl,
    isAnalyzing,
    result,
    error,
    analyze,
    clear
  } = useMediaAnalyzer();

  const {
    activeJob,
    isModalOpen,
    history,
    startDownload,
    startBatchDownload,
    cancelActiveJob,
    closeModal,
    fetchHistory
  } = useDownloadManager();

  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleDownloadSingle = async (params: {
    url: string;
    media_item_id?: string;
    format_id?: string;
    target_format?: string;
    quality?: string;
    direct_url?: string;
    custom_filename?: string;
  }) => {
    try {
      await startDownload(params);
    } catch (err: any) {
      setToastMessage(err.response?.data?.detail || 'Failed to start download.');
    }
  };

  const handleDownloadBatch = async (params: {
    url: string;
    item_ids: string[];
    archive_name?: string;
    target_format?: string;
  }) => {
    try {
      await startBatchDownload(params);
    } catch (err: any) {
      setToastMessage(err.response?.data?.detail || 'Failed to start batch ZIP archive.');
    }
  };

  const handleSampleSelect = (sampleUrl: string) => {
    setUrl(sampleUrl);
    analyze(sampleUrl);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-surface-canvas text-slate-900 flex flex-col selection:bg-slate-900 selection:text-white relative">
      {/* Top Navbar */}
      <Navbar
        onOpenHistory={() => setIsHistoryDrawerOpen(true)}
        historyCount={history.length}
      />

      {/* Main Content Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-12 relative z-10">
        {/* Hero & URL Input Form */}
        <UrlInputForm
          url={url}
          setUrl={setUrl}
          isAnalyzing={isAnalyzing}
          onAnalyze={analyze}
          onClear={clear}
        />

        {/* Error Toast Notification */}
        <Toast
          message={error || toastMessage}
          type="error"
          onDismiss={() => setToastMessage(null)}
        />

        {/* Media Analysis Result Area */}
        {result && (
          <div className="space-y-6 pt-2">
            {result.is_multi && result.items.length > 1 ? (
              <MultiMediaGrid
                analysis={result}
                onDownloadSingle={(p) => handleDownloadSingle(p)}
                onDownloadBatch={handleDownloadBatch}
              />
            ) : (
              <MediaPreviewCard
                analysis={result}
                onDownload={handleDownloadSingle}
              />
            )}
          </div>
        )}

        {/* Platforms, How It Works & Value Props (All matching reference mockups) */}
        <FeaturesSection onSelectSample={handleSampleSelect} />

        {/* Legal & Compliance Notice */}
        <LegalNotice />
      </main>

      {/* Minimal Footer */}
      <footer className="w-full border-t border-slate-200 py-8 bg-white/70 backdrop-blur-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-xs text-slate-500 space-y-1.5">
          <p className="font-medium text-slate-700">© {new Date().getFullYear()} DownFromNet — Clean & Minimal Internet Utility.</p>
          <p>Powered by FastAPI, AsyncIO, FFmpeg & React.</p>
        </div>
      </footer>

      {/* Download Progress Modal */}
      <DownloadProgressModal
        isOpen={isModalOpen}
        job={activeJob}
        onClose={closeModal}
        onCancel={cancelActiveJob}
      />

      {/* Download History Drawer */}
      <DownloadHistoryDrawer
        isOpen={isHistoryDrawerOpen}
        onClose={() => setIsHistoryDrawerOpen(false)}
        history={history}
        onRefresh={fetchHistory}
      />
    </div>
  );
}
