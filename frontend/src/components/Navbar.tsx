import React, { useEffect, useState } from 'react';
import { DownloadCloud, History, Globe, Youtube, Facebook, Instagram, Music, Cloud, Bot, Sparkles, ChevronDown } from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  onOpenHistory: () => void;
  historyCount: number;
  activePlatformId: string;
  onSelectPlatform: (slug: string) => void;
}

const NAV_PLATFORMS = [
  { id: 'youtube', slug: 'youtube-downloader', label: 'YouTube' },
  { id: 'instagram', slug: 'instagram-downloader', label: 'Instagram' },
  { id: 'facebook', slug: 'facebook-downloader', label: 'Facebook' },
  { id: 'tiktok', slug: 'tiktok-downloader', label: 'TikTok' },
  { id: 'twitter', slug: 'twitter-downloader', label: 'Twitter/X' },
  { id: 'reddit', slug: 'reddit-downloader', label: 'Reddit' },
];

export const Navbar: React.FC<NavbarProps> = ({ 
  onOpenHistory, 
  historyCount,
  activePlatformId,
  onSelectPlatform
}) => {
  const [isServerHealthy, setIsServerHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(() => setIsServerHealthy(true))
      .catch(() => setIsServerHealthy(false));
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/85 backdrop-blur-md transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <button
          onClick={() => onSelectPlatform('')}
          className="flex items-center gap-3 text-left focus:outline-hidden cursor-pointer group"
          aria-label="DownFromNet Home"
        >
          <div className="h-9 w-9 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
            <Globe className="w-5 h-5 text-white stroke-[2.2]" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold font-display tracking-tight text-slate-900">
              DownFromNet
            </span>
            <span className="hidden sm:inline-block text-[11px] font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full border border-slate-200">
              Free Utility
            </span>
          </div>
        </button>

        {/* Center / Navigation Links for Dedicated Platform Pages (SEO Link Architecture) */}
        <nav aria-label="Main platform navigation" className="hidden lg:flex items-center gap-1 text-xs font-semibold text-slate-600">
          <button
            onClick={() => onSelectPlatform('')}
            className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
              activePlatformId === 'home'
                ? 'bg-slate-100 text-slate-900 font-bold'
                : 'hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            All Platforms
          </button>

          {NAV_PLATFORMS.map((item) => {
            const isActive = activePlatformId === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectPlatform(item.slug)}
                className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-slate-100 text-slate-900 font-bold'
                    : 'hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {/* Server Status Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-xs text-slate-600" aria-label="Engine status">
            <span className={`w-2 h-2 rounded-full ${isServerHealthy === true ? 'bg-emerald-500' : isServerHealthy === false ? 'bg-rose-500' : 'bg-amber-400 animate-ping'}`} />
            <span className="font-medium">{isServerHealthy ? 'Engine Online' : 'Connecting...'}</span>
          </div>

          {/* History Button */}
          <button
            onClick={onOpenHistory}
            aria-label={`View download history, ${historyCount} items saved`}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-all shadow-2xs hover:border-slate-300 active:scale-95 cursor-pointer"
            title="View Download History"
          >
            <History className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
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
