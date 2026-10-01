import React, { useState, useRef, useEffect } from 'react';
import { 
  Search, 
  Clipboard, 
  X, 
  Loader2, 
  ArrowRight, 
  Globe,
  Youtube,
  Facebook,
  Instagram,
  Bot,
  Music,
  Cloud
} from 'lucide-react';
import { PlatformConfig, PLATFORMS_MAP } from '../config/platforms';
import { isValidHttpUrl } from '../utils/formatters';

interface UrlInputFormProps {
  url: string;
  setUrl: (url: string) => void;
  isAnalyzing: boolean;
  onAnalyze: (targetUrl?: string) => void;
  onClear: () => void;
  platform: PlatformConfig;
  onSelectPlatform: (slug: string) => void;
}

const PLATFORM_PILLS = [
  { id: 'home', slug: '', label: 'All Platforms', icon: Globe },
  { id: 'youtube', slug: 'youtube-downloader', label: 'YouTube', icon: Youtube },
  { id: 'instagram', slug: 'instagram-downloader', label: 'Instagram', icon: Instagram },
  { id: 'facebook', slug: 'facebook-downloader', label: 'Facebook', icon: Facebook },
  { id: 'tiktok', slug: 'tiktok-downloader', label: 'TikTok', icon: Music },
  { id: 'twitter', slug: 'twitter-downloader', label: 'Twitter / X', icon: Cloud },
  { id: 'reddit', slug: 'reddit-downloader', label: 'Reddit', icon: Bot },
];

export const UrlInputForm: React.FC<UrlInputFormProps> = ({
  url,
  setUrl,
  isAnalyzing,
  onAnalyze,
  onClear,
  platform,
  onSelectPlatform
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text.trim());
        if (isValidHttpUrl(text)) {
          onAnalyze(text.trim());
        }
      }
    } catch (err) {
      console.warn('Clipboard permission error');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyze();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedText = e.dataTransfer.getData('text/plain') || e.dataTransfer.getData('text/uri-list');
    if (droppedText) {
      setUrl(droppedText.trim());
      onAnalyze(droppedText.trim());
    }
  };

  const IconComponent = platform.icon;

  return (
    <div id="downloader" className="w-full max-w-4xl mx-auto text-center space-y-6 pt-2 sm:pt-6">
      {/* Platform Navigation Pills */}
      <div className="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 p-1.5 rounded-2xl bg-white/80 backdrop-blur-xs border border-slate-200/80 shadow-2xs max-w-fit mx-auto">
        {PLATFORM_PILLS.map((p) => {
          const isCurrent = (p.id === platform.id);
          const PillIcon = p.icon;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelectPlatform(p.slug)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer active:scale-95 ${
                isCurrent
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              <PillIcon className="w-3.5 h-3.5" />
              <span>{p.label}</span>
            </button>
          );
        })}
      </div>

      {/* Hero Badge, H1 Tag & Subtitle tailored for SEO */}
      <div className="space-y-4">
        <div className={`inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${platform.badgeBg} ${platform.badgeColor} border`}>
          <IconComponent className="w-3.5 h-3.5" />
          <span>{platform.badgeText}</span>
        </div>

        {/* SEO-Optimized H1 Tag */}
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 font-display max-w-3xl mx-auto leading-tight">
          {platform.h1}
        </h1>

        <p className="max-w-2xl mx-auto text-slate-500 text-sm sm:text-base leading-relaxed">
          {platform.subtitle}
        </p>
      </div>

      {/* Clean Minimalist Search / Input Pill */}
      <form
        role="search"
        aria-label={`${platform.name} search and download form`}
        onSubmit={handleSubmit}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`w-full max-w-3xl mx-auto transition-all duration-200 ${
          isDragOver ? 'scale-[1.01]' : ''
        }`}
      >
        <div className={`relative flex items-center bg-white rounded-2xl border p-2 shadow-apple transition-all ${
          isDragOver 
            ? 'border-blue-500 ring-4 ring-blue-100' 
            : 'border-slate-200 hover:border-slate-300 focus-within:border-blue-600 focus-within:ring-4 focus-within:ring-blue-100'
        }`}>
          <Search className="w-5 h-5 text-slate-400 ml-3 mr-3 shrink-0" aria-hidden="true" />
          
          <input
            ref={inputRef}
            id="media-url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={platform.placeholder}
            aria-label={`${platform.name} URL`}
            className="w-full bg-transparent text-slate-900 placeholder-slate-400 text-sm sm:text-base outline-none pr-2 font-normal"
            required
            disabled={isAnalyzing}
          />

          {/* Action Buttons inside Input Pill */}
          <div className="flex items-center gap-1.5 shrink-0">
            {url && (
              <button
                type="button"
                onClick={onClear}
                disabled={isAnalyzing}
                aria-label="Clear input URL"
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                title="Clear input"
              >
                <X className="w-4 h-4" aria-hidden="true" />
              </button>
            )}

            <button
              type="button"
              onClick={handlePaste}
              disabled={isAnalyzing}
              aria-label="Paste URL from clipboard"
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors active:scale-95 cursor-pointer"
              title="Paste from clipboard"
            >
              <Clipboard className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              <span>Paste</span>
            </button>

            <button
              type="submit"
              disabled={isAnalyzing || !url.trim()}
              aria-label={isAnalyzing ? "Analyzing video stream" : "Download media"}
              className="flex items-center gap-2 px-5 sm:px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-black text-white font-semibold text-sm shadow-xs transition-all disabled:opacity-40 disabled:pointer-events-none active:scale-95 cursor-pointer"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Download</span>
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Sample Quick Try Button */}
      {platform.sampleUrl && (
        <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
          <span className="text-slate-400">Want to test?</span>
          <button
            type="button"
            onClick={() => {
              setUrl(platform.sampleUrl);
              onAnalyze(platform.sampleUrl);
            }}
            disabled={isAnalyzing}
            className="text-blue-600 hover:text-blue-800 font-semibold underline underline-offset-2 hover:opacity-80 transition-opacity cursor-pointer"
          >
            Load sample {platform.shortName} link
          </button>
        </div>
      )}
    </div>
  );
};
