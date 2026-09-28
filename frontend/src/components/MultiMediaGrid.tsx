import React, { useState } from 'react';
import { 
  Archive, 
  CheckSquare, 
  Square, 
  Download, 
  Image as ImageIcon, 
  Film, 
  Music, 
  Check,
  Sparkles
} from 'lucide-react';
import { MediaAnalysisResponse, MediaItem } from '../types';

interface MultiMediaGridProps {
  analysis: MediaAnalysisResponse;
  onDownloadSingle: (params: {
    url: string;
    media_item_id: string;
    direct_url?: string;
    custom_filename?: string;
  }) => void;
  onDownloadBatch: (params: {
    url: string;
    item_ids: string[];
    archive_name?: string;
  }) => void;
}

export const MultiMediaGrid: React.FC<MultiMediaGridProps> = ({
  analysis,
  onDownloadSingle,
  onDownloadBatch
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(
    analysis.items.map(item => item.id) // Default select all
  );

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    setSelectedIds(analysis.items.map(item => item.id));
  };

  const handleDeselectAll = () => {
    setSelectedIds([]);
  };

  const handleBatchDownloadSelected = () => {
    if (selectedIds.length === 0) return;
    onDownloadBatch({
      url: analysis.url,
      item_ids: selectedIds,
      archive_name: `${analysis.source}_bundle`
    });
  };

  const handleBatchDownloadAll = () => {
    onDownloadBatch({
      url: analysis.url,
      item_ids: analysis.items.map(i => i.id),
      archive_name: `${analysis.source}_all_media`
    });
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-3 duration-300">
      {/* Header bar */}
      <div className="card-clean rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-200 bg-white">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-blue-50 text-blue-700 border border-blue-100">
              Found {analysis.items_count} media files
            </span>
            <span className="text-sm font-bold text-slate-900">
              {analysis.title}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {selectedIds.length} of {analysis.items.length} items selected for download
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={selectedIds.length === analysis.items.length ? handleDeselectAll : handleSelectAll}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-700 transition-colors"
          >
            {selectedIds.length === analysis.items.length ? (
              <>
                <Square className="w-3.5 h-3.5" />
                <span>Deselect All</span>
              </>
            ) : (
              <>
                <CheckSquare className="w-3.5 h-3.5 text-blue-600" />
                <span>Select All</span>
              </>
            )}
          </button>

          <button
            onClick={handleBatchDownloadSelected}
            disabled={selectedIds.length === 0}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold bg-slate-900 hover:bg-black text-white rounded-xl shadow-xs transition-all disabled:opacity-40 disabled:pointer-events-none active:scale-95"
          >
            <Archive className="w-4 h-4" />
            <span>Download Selected ({selectedIds.length}) ZIP</span>
          </button>

          <button
            onClick={handleBatchDownloadAll}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200 rounded-xl transition-all active:scale-95"
          >
            <Download className="w-4 h-4" />
            <span>Download All ({analysis.items.length})</span>
          </button>
        </div>
      </div>

      {/* Media Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {analysis.items.map((item, idx) => {
          const isSelected = selectedIds.includes(item.id);
          const isImage = item.media_type === 'image';
          const isVideo = item.media_type === 'video';

          return (
            <div
              key={item.id || idx}
              onClick={() => toggleSelect(item.id)}
              className={`group relative rounded-xl overflow-hidden card-clean border transition-all cursor-pointer bg-white ${
                isSelected
                  ? 'border-blue-600 ring-2 ring-blue-500/20'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              {/* Media Thumbnail */}
              <div className="relative aspect-video bg-slate-100 overflow-hidden flex items-center justify-center">
                {item.thumbnail || item.direct_url ? (
                  <img
                    src={item.thumbnail || item.direct_url || ''}
                    alt={item.title}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center text-slate-400">
                    {isVideo ? <Film className="w-8 h-8" /> : isImage ? <ImageIcon className="w-8 h-8" /> : <Music className="w-8 h-8" />}
                  </div>
                )}

                {/* Selection Checkbox overlay */}
                <div className="absolute top-2 left-2 z-10">
                  <div className={`w-5 h-5 rounded flex items-center justify-center transition-all ${
                    isSelected ? 'bg-blue-600 text-white shadow-xs' : 'bg-white/90 border border-slate-300 text-transparent'
                  }`}>
                    <Check className="w-3.5 h-3.5 stroke-[3]" />
                  </div>
                </div>

                {/* Type badge */}
                <div className="absolute top-2 right-2">
                  <span className="px-1.5 py-0.5 text-[10px] font-bold bg-black/70 backdrop-blur-md rounded text-white uppercase">
                    {item.media_type}
                  </span>
                </div>
              </div>

              {/* Card Footer */}
              <div className="p-2.5 space-y-1 bg-white border-t border-slate-100">
                <p className="text-xs font-semibold text-slate-900 truncate" title={item.title}>
                  {item.title}
                </p>
                <div className="flex items-center justify-between pt-0.5">
                  <span className="text-[10px] text-slate-400 font-medium">
                    {item.width && item.height ? `${item.width}x${item.height}` : `#${idx + 1}`}
                  </span>
                  
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDownloadSingle({
                        url: analysis.url,
                        media_item_id: item.id,
                        direct_url: item.direct_url || undefined,
                        custom_filename: item.title
                      });
                    }}
                    className="p-1 rounded-md hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition-colors"
                    title="Download this item directly"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
