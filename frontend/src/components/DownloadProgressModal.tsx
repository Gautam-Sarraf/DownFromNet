import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Download, 
  X, 
  FileCheck, 
  AlertTriangle 
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
  if (!isOpen || !job) return null;

  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isCancelled = job.status === 'cancelled';
  const isProcessing = job.status === 'processing' || job.status === 'downloading' || job.status === 'pending';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md card-clean bg-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-200 space-y-6">
        {/* Close button if finished */}
        {(isCompleted || isFailed || isCancelled) && (
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Header with status icon */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 bg-slate-50 border border-slate-200">
            {isCompleted && <CheckCircle2 className="w-7 h-7 text-emerald-600 animate-in zoom-in-50" />}
            {isFailed && <XCircle className="w-7 h-7 text-rose-600 animate-in zoom-in-50" />}
            {isCancelled && <AlertTriangle className="w-7 h-7 text-amber-500" />}
            {isProcessing && <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />}
          </div>

          <div className="space-y-0.5 overflow-hidden">
            <h3 className="text-lg font-bold text-slate-900 font-display">
              {isCompleted ? 'Download Ready' : isFailed ? 'Download Failed' : isCancelled ? 'Download Cancelled' : 'Processing Media...'}
            </h3>
            <p className="text-xs text-slate-500 truncate" title={job.filename || 'media_item'}>
              {job.filename || 'Analyzing and streaming bits...'}
            </p>
          </div>
        </div>

        {/* Progress Bar & Status Text */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-medium">
            <span className="text-slate-600 flex items-center gap-1.5">
              {job.message}
            </span>
            <span className="text-slate-900 font-bold font-mono">
              {Math.round(job.progress)}%
            </span>
          </div>

          <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden p-0.5 border border-slate-200">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isCompleted
                  ? 'bg-emerald-500'
                  : isFailed
                  ? 'bg-rose-500'
                  : 'bg-slate-900'
              }`}
              style={{ width: `${Math.max(6, job.progress)}%` }}
            />
          </div>
        </div>

        {/* File info box */}
        {isCompleted && (
          <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200/80 flex items-center justify-between text-xs text-emerald-800">
            <div className="flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="truncate max-w-[200px] font-medium">{job.filename}</span>
            </div>
            {job.filesize_formatted && (
              <span className="font-bold text-emerald-700">{job.filesize_formatted}</span>
            )}
          </div>
        )}

        {isFailed && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-xs text-rose-700 font-medium">
            <p>{job.error || 'The download could not be completed. Please check the URL or try another format.'}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2.5 pt-2">
          {isProcessing && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
            >
              Cancel
            </button>
          )}

          {isCompleted && (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
              >
                Close
              </button>
              {job.download_url && (
                <a
                  href={job.download_url}
                  download={job.filename || 'download'}
                  className="flex items-center gap-2 px-5 py-2 text-xs font-bold text-white bg-slate-900 hover:bg-black rounded-xl shadow-xs transition-all active:scale-95"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Again</span>
                </a>
              )}
            </>
          )}

          {(isFailed || isCancelled) && (
            <button
              onClick={onClose}
              className="px-5 py-2 text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
