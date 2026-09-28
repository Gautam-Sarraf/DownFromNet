import React, { useEffect, useState } from 'react';
import { DownloadCloud, History, Globe, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  onOpenHistory: () => void;
  historyCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenHistory, historyCount }) => {
  const [isServerHealthy, setIsServerHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(() => setIsServerHealthy(true))
      .catch(() => setIsServerHealthy(false));
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/80 backdrop-blur-md transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-sm">
            <Globe className="w-5 h-5 text-white stroke-[2.2]" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold font-display tracking-tight text-slate-900">
              DownFromNet
            </span>
            <span className="hidden sm:inline-block text-[11px] font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full border border-slate-200">
              Clean Utility
            </span>
          </div>
        </div>

        {/* Center / Navigation Links (Apple/Arc clean style) */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <a href="#downloader" className="hover:text-slate-900 transition-colors">Downloader</a>
          <a href="#platforms" className="hover:text-slate-900 transition-colors">Platforms</a>
          <a href="#how-to-use" className="hover:text-slate-900 transition-colors">How It Works</a>
          <a href="#features" className="hover:text-slate-900 transition-colors">Features</a>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {/* Server Status Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-xs text-slate-600">
            <span className={`w-2 h-2 rounded-full ${isServerHealthy === true ? 'bg-emerald-500' : isServerHealthy === false ? 'bg-rose-500' : 'bg-amber-400 animate-ping'}`} />
            <span className="font-medium">{isServerHealthy ? 'Engine Online' : 'Connecting...'}</span>
          </div>

          {/* History Button */}
          <button
            onClick={onOpenHistory}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-all shadow-xs hover:border-slate-300 active:scale-95"
            title="View Download History"
          >
            <History className="w-3.5 h-3.5 text-slate-500" />
            <span>History</span>
            {historyCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] font-bold bg-slate-900 text-white rounded-full">
                {historyCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
