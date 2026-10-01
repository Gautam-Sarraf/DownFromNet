import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { UrlInputForm } from './components/UrlInputForm';
import { MediaPreviewCard } from './components/MediaPreviewCard';
import { MultiMediaGrid } from './components/MultiMediaGrid';
import { DownloadHistoryDrawer } from './components/DownloadHistoryDrawer';
import { FeaturesSection } from './components/FeaturesSection';
import { LegalNotice } from './components/LegalNotice';
import { Toast } from './components/Toast';
import { DownloadProgressModal } from './components/DownloadProgressModal';
import { useMediaAnalyzer } from './hooks/useMediaAnalyzer';
import { useDownloadManager } from './hooks/useDownloadManager';
import { getPlatformFromPath, PlatformConfig, PLATFORMS_MAP } from './config/platforms';

export function App() {
  const [currentPath, setCurrentPath] = useState<string>(() => window.location.pathname);
  const platform = getPlatformFromPath(currentPath);

  const {
    url,
    setUrl,
    isAnalyzing,
    result,
    error,
    analyze,
    clear
  } = useMediaAnalyzer();

  const [notification, setNotification] = useState<{ message: string; type: 'error' | 'success' | 'info' } | null>(null);

  const {
    activeJob,
    isDownloading,
    isModalOpen,
    history,
    startDownload,
    startBatchDownload,
    cancelActiveJob,
    closeModal,
    fetchHistory
  } = useDownloadManager({
    onError: (errorMessage) => {
      setNotification({
        message: errorMessage,
        type: 'error'
      });
    }
  });

  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);

  // Sync document title and meta description on route / platform change
  useEffect(() => {
    document.title = platform.metaTitle;
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.setAttribute('name', 'description');
      document.head.appendChild(metaDesc);
    }
    metaDesc.setAttribute('content', platform.metaDescription);
  }, [platform]);

  // Handle browser back / forward navigation
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleSelectPlatform = useCallback((slug: string) => {
    const targetPath = slug ? `/${slug}` : '/';
    window.history.pushState(null, '', targetPath);
    setCurrentPath(targetPath);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

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
      setNotification({
        message: err.response?.data?.detail || 'Failed to start download.',
        type: 'error'
      });
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
      setNotification({
        message: err.response?.data?.detail || 'Failed to start batch ZIP archive.',
        type: 'error'
      });
    }
  };

  return (
    <div className="min-h-screen bg-surface-canvas text-slate-900 flex flex-col selection:bg-slate-900 selection:text-white relative">
      {/* Top Navbar */}
      <Navbar
        onOpenHistory={() => setIsHistoryDrawerOpen(true)}
        historyCount={history.length}
        activePlatformId={platform.id}
        onSelectPlatform={handleSelectPlatform}
      />

      {/* Main Content Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-10 space-y-12 relative z-10">
        {/* Hero & URL Input Form with dedicated SEO H1 Tag & Platform Switcher */}
        <UrlInputForm
          url={url}
          setUrl={setUrl}
          isAnalyzing={isAnalyzing}
          onAnalyze={analyze}
          onClear={clear}
          platform={platform}
          onSelectPlatform={handleSelectPlatform}
        />

        {/* Toast Notifications (Errors, Success & Browser Download Status) */}
        {error ? (
          <Toast
            message={error}
            type="error"
            onDismiss={() => {}}
          />
        ) : notification ? (
          <Toast
            message={notification.message}
            type={notification.type}
            onDismiss={() => setNotification(null)}
          />
        ) : null}

        {/* Media Analysis Result Area */}
        {result && (
          <div className="space-y-6 pt-2">
            {result.is_multi && result.items.length > 1 ? (
              <MultiMediaGrid
                analysis={result}
                isDownloading={isDownloading}
                onDownloadSingle={(p) => handleDownloadSingle(p)}
                onDownloadBatch={handleDownloadBatch}
              />
            ) : (
              <MediaPreviewCard
                analysis={result}
                isDownloading={isDownloading}
                onDownload={handleDownloadSingle}
              />
            )}
          </div>
        )}

        {/* Dedicated SEO Features, Step Guide, FAQs, and Cross-Platform Linking */}
        <FeaturesSection 
          platform={platform} 
          onSelectPlatform={handleSelectPlatform} 
        />

        {/* Legal & Compliance Notice */}
        <LegalNotice />
      </main>

      {/* Minimal Footer */}
      <footer className="w-full border-t border-slate-200 py-8 bg-white/70 backdrop-blur-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-xs text-slate-500 space-y-3">
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-semibold text-slate-600">
            <button onClick={() => handleSelectPlatform('youtube-downloader')} className="hover:text-slate-900 cursor-pointer">YouTube Downloader</button>
            <button onClick={() => handleSelectPlatform('instagram-downloader')} className="hover:text-slate-900 cursor-pointer">Instagram Downloader</button>
            <button onClick={() => handleSelectPlatform('facebook-downloader')} className="hover:text-slate-900 cursor-pointer">Facebook Downloader</button>
            <button onClick={() => handleSelectPlatform('tiktok-downloader')} className="hover:text-slate-900 cursor-pointer">TikTok Downloader</button>
            <button onClick={() => handleSelectPlatform('twitter-downloader')} className="hover:text-slate-900 cursor-pointer">Twitter / X Downloader</button>
            <button onClick={() => handleSelectPlatform('reddit-downloader')} className="hover:text-slate-900 cursor-pointer">Reddit Downloader</button>
          </div>
          <p className="font-medium text-slate-700">© {new Date().getFullYear()} DownFromNet — High-Speed Universal Video Downloader.</p>
          <p>Powered by FastAPI, AsyncIO, FFmpeg & React.</p>
        </div>
      </footer>

      {/* Download History Drawer */}
      <DownloadHistoryDrawer
        isOpen={isHistoryDrawerOpen}
        onClose={() => setIsHistoryDrawerOpen(false)}
        history={history}
        onRefresh={fetchHistory}
      />

      {/* Download Progress & Realtime Metrics Modal */}
      <DownloadProgressModal
        isOpen={isModalOpen}
        job={activeJob}
        onClose={closeModal}
        onCancel={cancelActiveJob}
      />
    </div>
  );
}
