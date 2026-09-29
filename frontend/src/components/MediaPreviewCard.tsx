import React, { useState } from 'react';
import { 
  Download, 
  Film, 
  Music, 
  Image as ImageIcon, 
  FileText, 
  Check, 
  Clock, 
  Layers, 
  Sparkles,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import { MediaAnalysisResponse, MediaItem, MediaFormat } from '../types';
import { formatBytes, formatDuration, getSourceBadgeColor } from '../utils/formatters';

interface MediaPreviewCardProps {
  analysis: MediaAnalysisResponse;
  onDownload: (params: {
    url: string;
    media_item_id?: string;
    format_id?: string;
    target_format?: string;
    quality?: string;
    direct_url?: string;
    custom_filename?: string;
  }) => void;
}

export const MediaPreviewCard: React.FC<MediaPreviewCardProps> = ({
  analysis,
  onDownload
}) => {
  const item = analysis.items[0] || {
    id: 'item_0',
    title: analysis.title,
    media_type: analysis.media_type,
    thumbnail: analysis.thumbnail,
    duration: analysis.duration,
    duration_formatted: analysis.duration_formatted,
    source_url: analysis.url,
    formats: analysis.formats
  };

  const availableFormats = item.formats.length > 0 ? item.formats : analysis.formats;

  const [selectedFormatId, setSelectedFormatId] = useState<string>(
    availableFormats[0]?.format_id || 'best'
  );

  const [targetConversion, setTargetConversion] = useState<string>('original');

  const selectedFormatObj = availableFormats.find(f => f.format_id === selectedFormatId) || availableFormats[0];

  const handleDownloadClick = () => {
    const isPlatformExtractor = analysis.extractor_name === 'ytdlp';
    const directUrlToSend = (!isPlatformExtractor && (selectedFormatObj?.download_url || item.direct_url)) || undefined;

    onDownload({
      url: analysis.url,
      media_item_id: item.id,
      format_id: selectedFormatId,
      target_format: targetConversion !== 'original' ? targetConversion : undefined,
      quality: selectedFormatObj?.quality,
      direct_url: directUrlToSend,
      custom_filename: item.title
    });
  };

  const renderPreviewElement = () => {
    if (item.media_type === 'video' && item.direct_url) {
      return (
        <video
          src={item.direct_url}
          poster={item.thumbnail || undefined}
          controls
          className="w-full h-auto max-h-[360px] rounded-2xl object-contain bg-slate-900 shadow-xs"
        />
      );
    }
    if (item.media_type === 'audio' && item.direct_url) {
      return (
        <div className="w-full p-6 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col items-center justify-center gap-4">
          <div className="w-14 h-14 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
            <Music className="w-7 h-7" />
          </div>
          <audio src={item.direct_url} controls className="w-full max-w-md" />
        </div>
      );
    }
    if (item.thumbnail || item.media_type === 'image') {
      return (
        <div className="relative group overflow-hidden rounded-2xl bg-slate-100 border border-slate-200/80 max-h-[360px] flex items-center justify-center">
          <img
            src={item.thumbnail || item.direct_url || ''}
            alt={item.title}
            className="w-full h-auto max-h-[360px] object-contain transition-transform duration-300 group-hover:scale-[1.02]"
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
        </div>
      );
    }
    return (
      <div className="w-full h-48 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col items-center justify-center gap-2 text-slate-400">
        <Layers className="w-8 h-8 text-slate-400 stroke-1" />
        <span className="text-xs font-medium">Direct stream ready for download</span>
      </div>
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto card-clean rounded-3xl p-6 sm:p-8 shadow-apple border border-slate-200 bg-white animate-in fade-in slide-in-from-bottom-3 duration-300">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Left / Preview Area */}
        <div className="md:col-span-6 space-y-3">
          {renderPreviewElement()}
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span className="truncate max-w-[200px]" title={analysis.url}>
              {analysis.url}
            </span>
            <a
              href={analysis.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 font-medium text-slate-700 hover:text-blue-600 transition-colors"
            >
              <span>Visit Source</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        {/* Right / Configuration & Action */}
        <div className="md:col-span-6 space-y-5">
          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-100 text-slate-700 border border-slate-200 uppercase tracking-wide">
              {analysis.source}
            </span>
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-50 text-blue-700 border border-blue-100 uppercase">
              {item.media_type}
            </span>
            {item.duration_formatted && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs rounded-full bg-slate-50 text-slate-600 border border-slate-200">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>{item.duration_formatted}</span>
              </span>
            )}
          </div>

          {/* Title */}
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 font-display line-clamp-2" title={item.title}>
              {item.title}
            </h2>
          </div>

          {/* Format & Quality Selector */}
          <div className="space-y-4 pt-3 border-t border-slate-100">
            {/* Stream Quality Selector */}
            {availableFormats.length > 0 && (
              <div className="space-y-1.5">
                <label htmlFor="media-quality-select" className="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center justify-between">
                  <span>Resolution / Quality</span>
                  {selectedFormatObj?.filesize && (
                    <span className="text-slate-500 font-mono text-xs lowercase">
                      ~ {selectedFormatObj.filesize}
                    </span>
                  )}
                </label>
                <select
                  id="media-quality-select"
                  value={selectedFormatId}
                  onChange={(e) => setSelectedFormatId(e.target.value)}
                  aria-label="Select stream quality or resolution"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 text-sm focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none transition-all cursor-pointer font-medium"
                >
                  {availableFormats.map((fmt) => (
                    <option key={fmt.format_id} value={fmt.format_id}>
                      {fmt.quality} {fmt.resolution ? `(${fmt.resolution})` : ''} - {fmt.format.toUpperCase()} {fmt.filesize ? `[${fmt.filesize}]` : ''}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Target Conversion Format (FFmpeg) */}
            <div className="space-y-1.5">
              <label htmlFor="target-conversion-select" className="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-blue-600" aria-hidden="true" />
                <span>Format Conversion (FFmpeg)</span>
              </label>
              <select
                id="target-conversion-select"
                value={targetConversion}
                onChange={(e) => setTargetConversion(e.target.value)}
                aria-label="Select target conversion format"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 text-sm focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none transition-all cursor-pointer font-medium"
              >
                <option value="original">Original Format (Fastest - Direct Stream)</option>
                <optgroup label="Audio Extraction">
                  <option value="mp3">MP3 Audio (192 kbps)</option>
                  <option value="m4a">M4A / AAC Audio</option>
                  <option value="wav">WAV Lossless Audio</option>
                </optgroup>
                <optgroup label="Video Formats">
                  <option value="mp4">MP4 Video (H.264 Universal)</option>
                  <option value="webm">WebM Video (VP9 Modern)</option>
                </optgroup>
                {item.media_type === 'image' && (
                  <optgroup label="Image Formats">
                    <option value="png">PNG Image</option>
                    <option value="jpg">JPEG Image</option>
                    <option value="webp">WebP Image</option>
                  </optgroup>
                )}
              </select>
            </div>
          </div>

          {/* Download Action Button */}
          <div className="pt-2">
            <button
              onClick={handleDownloadClick}
              aria-label={`Download media: ${item.title}`}
              className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-base shadow-sm hover:shadow transition-all active:scale-[0.99] cursor-pointer"
            >
              <Download className="w-5 h-5 stroke-[2.2]" aria-hidden="true" />
              <span>Download Media</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
