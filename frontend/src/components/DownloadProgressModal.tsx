import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Download, 
  X, 
  FileCheck, 
  AlertTriangle,
  Film,
  Sparkles,
  Copy,
  Check,
  ArrowDown
} from 'lucide-react';
import { DownloadJobStatus } from '../types';

interface DownloadProgressModalProps {
  isOpen: boolean;
  job: DownloadJobStatus | null;
  onClose: () => void;
  onCancel: () => void;
}

export const DownloadProgressModal: React.FC<DownloadProgressModalProps> = ({
  isOpen,
  job,
  onClose,
  onCancel
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !job) return null;

  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isCancelled = job.status === 'cancelled';
  const isDownloading = job.status === 'downloading' || job.status === 'pending';
  const isProcessing = job.status === 'processing';
  const isInProgress = isDownloading || isProcessing;

  const progressPercent = Math.min(100, Math.max(0, Math.round(job.progress || 0)));

  const handleCopyLink = () => {
    if (job.download_url) {
      const fullUrl = job.download_url.startsWith('http')
        ? job.download_url
        : `${window.location.origin}${job.download_url}`;
      navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleTriggerDownload = () => {
    if (job.download_url) {
      const a = document.createElement('a');
      a.href = job.download_url;
      a.download = job.filename || 'download';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/65 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-lg bg-white rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-200/80 space-y-6 animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
        aria-labelledby="download-modal-title"
      >
        {/* Top Close Button for Completed / Failed states */}
        {!isInProgress && (
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Header with Status Icon & Title */}
        <div className="flex items-center gap-4">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 border transition-all ${
            isCompleted 
              ? 'bg-emerald-50 border-emerald-200 text-emerald-600 shadow-sm shadow-emerald-100' 
              : isFailed 
              ? 'bg-rose-50 border-rose-200 text-rose-600' 
              : isCancelled 
              ? 'bg-amber-50 border-amber-200 text-amber-600' 
              : 'bg-blue-50 border-blue-200 text-blue-600 shadow-sm shadow-blue-100'
          }`}>
            {isCompleted && <CheckCircle2 className="w-8 h-8 animate-in zoom-in-50" />}
            {isFailed && <XCircle className="w-8 h-8 animate-in zoom-in-50" />}
            {isCancelled && <AlertTriangle className="w-8 h-8" />}
            {isInProgress && <Loader2 className="w-8 h-8 animate-spin" />}
          </div>

          <div className="space-y-1 overflow-hidden pr-6">
            <div className="flex items-center gap-2">
              <h3 id="download-modal-title" className="text-xl font-bold text-slate-900 font-display">
                {isCompleted 
                  ? 'Download Ready!' 
                  : isProcessing 
                  ? 'Merging Media...' 
                  : isDownloading 
                  ? 'Downloading Media...' 
                  : isCancelled 
                  ? 'Download Cancelled' 
                  : 'Download Error'}
              </h3>
              {isInProgress && (
                <span className="flex h-2.5 w-2.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-600"></span>
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 truncate" title={job.filename || 'media_download'}>
              {job.filename || 'Preparing high-speed stream acquisition...'}
            </p>
          </div>
        </div>

        {/* Progress Bar & Real-time Metrics (During In-Progress or Completed) */}
        <div className="space-y-3 bg-slate-50/80 p-4 sm:p-5 rounded-2xl border border-slate-100">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-slate-700 truncate pr-2 flex items-center gap-1.5">
              {isInProgress && <ArrowDown className="w-3.5 h-3.5 text-blue-600 animate-bounce" />}
              {job.message || 'Extracting media streams...'}
            </span>
            <span className="text-slate-900 font-mono text-sm font-bold shrink-0">
              {progressPercent}%
            </span>
          </div>

          {/* Animated Progress Track */}
          <div className="w-full h-3.5 bg-slate-200/70 rounded-full overflow-hidden p-0.5 relative">
            <div
              className={`h-full rounded-full transition-all duration-300 ease-out relative overflow-hidden ${
                isCompleted
                  ? 'bg-emerald-500'
                  : isFailed
                  ? 'bg-rose-500'
                  : isCancelled
                  ? 'bg-amber-500'
                  : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500'
              }`}
              style={{ width: `${Math.max(4, progressPercent)}%` }}
            >
              {isInProgress && (
                <div className="absolute inset-0 bg-white/20 animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent w-full" />
              )}
            </div>
          </div>

          {/* Subtitle helper */}
          {isInProgress && (
            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-0.5">
              <span>{isProcessing ? 'Merging streams with FFmpeg...' : 'Multi-threaded stream fetch'}</span>
              <span>Keep this tab open</span>
            </div>
          )}
        </div>

        {/* Success Card */}
        {isCompleted && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200/80 flex items-center justify-between gap-3 text-xs text-emerald-900">
              <div className="flex items-center gap-2.5 overflow-hidden">
                <FileCheck className="w-5 h-5 text-emerald-600 shrink-0" />
                <div className="overflow-hidden">
                  <p className="font-bold text-slate-900 truncate" title={job.filename || ''}>
                    {job.filename}
                  </p>
                  <p className="text-[11px] text-emerald-700">Ready to save to your device</p>
                </div>
              </div>
              {job.filesize_formatted && (
                <span className="px-2.5 py-1 rounded-lg bg-emerald-100/80 font-mono font-bold text-emerald-800 text-xs shrink-0">
                  {job.filesize_formatted}
                </span>
              )}
            </div>

            {/* Save Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-2.5">
              <button
                onClick={handleTriggerDownload}
                className="w-full sm:flex-1 flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl font-bold text-sm bg-slate-900 hover:bg-black text-white shadow-md hover:shadow-lg transition-all active:scale-[0.99] cursor-pointer"
              >
                <Download className="w-4 h-4 stroke-[2.5]" />
                <span>Save File to Device</span>
              </button>

              <button
                onClick={handleCopyLink}
                className="w-full sm:w-auto flex items-center justify-center gap-1.5 py-3.5 px-4 rounded-xl font-semibold text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors"
                title="Copy Direct Link"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-600" />
                    <span className="text-emerald-700">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    <span>Copy Link</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Failed Error Message */}
        {isFailed && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-800 space-y-1">
            <p className="font-bold flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>Acquisition Error</span>
            </p>
            <p className="text-slate-600 leading-relaxed">
              {job.error || 'The remote media server rejected the stream request. Please try another quality or check the link.'}
            </p>
          </div>
        )}

        {/* In-Progress Cancel Action or Footer */}
        {isInProgress && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <span className="text-xs text-slate-400">Processing in background</span>
            <button
              onClick={onCancel}
              className="px-4 py-2 text-xs font-semibold text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-xl transition-all"
            >
              Cancel Download
            </button>
          </div>
        )}

        {/* Close Button on Complete/Failed */}
        {!isInProgress && (
          <div className="flex justify-end pt-1">
            <button
              onClick={onClose}
              className="px-5 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
