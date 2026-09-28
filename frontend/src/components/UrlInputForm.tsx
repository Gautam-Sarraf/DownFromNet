import React, { useState, useRef } from 'react';
import { Search, Clipboard, X, Loader2, ArrowRight, Play, Film, Image as ImageIcon, Music, Globe } from 'lucide-react';
import { isValidHttpUrl } from '../utils/formatters';

interface UrlInputFormProps {
  url: string;
  setUrl: (url: string) => void;
  isAnalyzing: boolean;
  onAnalyze: (targetUrl?: string) => void;
  onClear: () => void;
}

const SUPPORTED_PLATFORMS = [
  {
    name: 'YouTube',
    color: 'text-red-600',
    dotColor: 'bg-red-500',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
  },
  {
    name: 'Facebook',
    color: 'text-blue-600',
    dotColor: 'bg-blue-600',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
  },
  {
    name: 'Instagram',
    color: 'text-pink-600',
    dotColor: 'bg-pink-500',
    sampleUrl: 'https://images-assets.nasa.gov/image/PIA12348/PIA12348~orig.jpg',
  },
  {
    name: 'TikTok',
    color: 'text-slate-900',
    dotColor: 'bg-slate-900',
    sampleUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
  },
  {
    name: 'Twitter / X',
    color: 'text-slate-800',
    dotColor: 'bg-slate-800',
    sampleUrl: 'https://commons.wikimedia.org/wiki/File:Apollo_11_launch_clip.ogv',
  },
  {
    name: 'Reddit',
    color: 'text-orange-600',
    dotColor: 'bg-orange-500',
    sampleUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
  }
];

export const UrlInputForm: React.FC<UrlInputFormProps> = ({
  url,
  setUrl,
  isAnalyzing,
  onAnalyze,
  onClear
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

  return (
    <div id="downloader" className="w-full max-w-3xl mx-auto text-center space-y-6 pt-4 sm:pt-8">
      {/* Utility Tag & Hero Titles (Apple + Arc minimal style) */}
      <div className="space-y-3.5">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold">
          <Globe className="w-3.5 h-3.5 text-blue-600" />
          <span>Internet Utility — Clean & Minimal</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 font-display">
          Download any video <br className="hidden sm:inline" />
          <span className="text-slate-900">in high quality.</span>
        </h1>

        <p className="max-w-xl mx-auto text-slate-500 text-sm sm:text-base leading-relaxed">
          The cleanest way to save your favorite content from the web and social platforms. Instant analysis, no ads, high-speed.
        </p>
      </div>

      {/* Clean Minimalist Search / Input Pill */}
      <form
        onSubmit={handleSubmit}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`w-full transition-all duration-200 ${
          isDragOver ? 'scale-[1.01]' : ''
        }`}
      >
        <div className={`relative flex items-center bg-white rounded-2xl border p-2 shadow-apple transition-all ${
          isDragOver 
            ? 'border-blue-500 ring-4 ring-blue-100' 
            : 'border-slate-200 hover:border-slate-300 focus-within:border-blue-600 focus-within:ring-4 focus-within:ring-blue-100'
        }`}>
          <Search className="w-5 h-5 text-slate-400 ml-3 mr-3 shrink-0" />
          
          <input
            ref={inputRef}
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste your link here..."
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
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                title="Clear input"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            <button
              type="button"
              onClick={handlePaste}
              disabled={isAnalyzing}
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors active:scale-95"
              title="Paste from clipboard"
            >
              <Clipboard className="w-3.5 h-3.5 text-slate-500" />
              <span>Paste</span>
            </button>

            <button
              type="submit"
              disabled={isAnalyzing || !url.trim()}
              className="flex items-center gap-2 px-5 sm:px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-black text-white font-semibold text-sm shadow-xs transition-all disabled:opacity-40 disabled:pointer-events-none active:scale-95"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>Download</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Platform Chips Bar (as seen in Mockup 1) */}
      <div className="flex flex-wrap items-center justify-center gap-2 pt-1 text-xs text-slate-500">
        <span className="font-medium mr-1 text-slate-400">Supported:</span>
        {SUPPORTED_PLATFORMS.map((platform, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setUrl(platform.sampleUrl);
              onAnalyze(platform.sampleUrl);
            }}
            disabled={isAnalyzing}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white hover:bg-slate-50 border border-slate-200/80 hover:border-slate-300 text-slate-700 font-medium text-xs shadow-2xs transition-all active:scale-95 cursor-pointer"
            title={`Try ${platform.name}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${platform.dotColor}`} />
            <span>{platform.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
