import React from 'react';
import { AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

interface ToastProps {
  message: string | null;
  type?: 'error' | 'success' | 'info';
  onDismiss: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'error', onDismiss }) => {
  if (!message) return null;

  const styles = {
    error: 'bg-rose-50 border-rose-200 text-rose-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconColors = {
    error: 'text-rose-600',
    success: 'text-emerald-600',
    info: 'text-blue-600'
  };

  const Icon = type === 'error' ? AlertTriangle : type === 'success' ? CheckCircle : Info;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 animate-in fade-in slide-in-from-top-2 duration-200">
      <div className={`p-4 rounded-2xl border shadow-soft flex items-start gap-3 justify-between ${styles[type]}`}>
        <div className="flex items-start gap-3">
          <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${iconColors[type]}`} />
          <div className="text-xs sm:text-sm font-medium leading-relaxed">
            {message}
          </div>
        </div>
        <button
          onClick={onDismiss}
          className="p-1 rounded-lg hover:bg-black/5 transition-colors shrink-0 text-slate-500"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
