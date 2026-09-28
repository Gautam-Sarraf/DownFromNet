export function formatBytes(bytes?: number | null): string {
  if (bytes === undefined || bytes === null || bytes < 0) return 'Unknown size';
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatDuration(seconds?: number | null): string {
  if (!seconds || seconds <= 0) return '';
  const total = Math.floor(seconds);
  const hrs = Math.floor(total / 3600);
  const mins = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

export function isValidHttpUrl(string: string): boolean {
  try {
    const url = new URL(string.trim().startsWith('http') ? string.trim() : `https://${string.trim()}`);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch (_) {
    return false;
  }
}

export function getSourceBadgeColor(source: string): string {
  const s = source.toLowerCase();
  if (s.includes('youtube') || s.includes('youtu')) return 'bg-red-500/20 text-red-400 border-red-500/30';
  if (s.includes('vimeo')) return 'bg-sky-500/20 text-sky-400 border-sky-500/30';
  if (s.includes('reddit')) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
  if (s.includes('twitter') || s.includes('x')) return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
  if (s.includes('tiktok')) return 'bg-pink-500/20 text-pink-400 border-pink-500/30';
  if (s.includes('instagram')) return 'bg-fuchsia-500/20 text-fuchsia-400 border-fuchsia-500/30';
  if (s.includes('direct')) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
}
