import React from 'react';
import { X, History, Download, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { DownloadJobStatus } from '../types';

interface DownloadHistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: DownloadJobStatus[];
  onRefresh: () => void;
}

export const DownloadHistoryDrawer: React.FC<DownloadHistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onRefresh
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/30 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white border-l border-slate-200 p-6 flex flex-col justify-between shadow-2xl animate-in slide-in-from-right duration-300">
          {/* Header */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-slate-100 text-slate-700">
                  <History className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 font-display">Download History</h3>
                  <p className="text-xs text-slate-500">{history.length} session items</p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* History List */}
            <div className="space-y-3 overflow-y-auto max-h-[calc(100vh-180px)] pr-1">
              {history.length === 0 ? (
                <div className="text-center py-16 space-y-2 text-slate-400">
                  <Clock className="w-10 h-10 mx-auto stroke-1" />
                  <p className="text-sm">No downloads in this session yet.</p>
                </div>
              ) : (
                history.map((job) => {
                  const isSuccess = job.status === 'completed';
                  return (
                    <div
                      key={job.job_id}
                      className="p-3.5 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-slate-300 space-y-2 transition-all"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="space-y-0.5 overflow-hidden">
                          <p className="text-xs font-semibold text-slate-900 truncate" title={job.filename || 'media_item'}>
                            {job.filename || 'Media Download'}
                          </p>
                          <div className="flex items-center gap-2 text-[10px] text-slate-500">
                            <span>{new Date(job.created_at).toLocaleTimeString()}</span>
                            {job.filesize_formatted && <span>• {job.filesize_formatted}</span>}
                          </div>
                        </div>

                        {isSuccess ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-500 shrink-0" />
                        )}
                      </div>

                      {/* Download Link if completed */}
                      {isSuccess && job.download_url && (
                        <div className="pt-1 flex justify-end">
                          <a
                            href={job.download_url}
                            download={job.filename || 'download'}
                            className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-bold text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors shadow-2xs"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>Save Again</span>
                          </a>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Footer note */}
          <div className="pt-4 border-t border-slate-100 text-center">
            <p className="text-[11px] text-slate-400">
              Temporary server files are automatically cleaned up after 30 minutes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
