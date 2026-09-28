export type MediaType = 'video' | 'audio' | 'image' | 'document' | 'other';

export interface MediaFormat {
  format_id: string;
  format: string;
  quality: string;
  resolution?: string | null;
  filesize_bytes?: number | null;
  filesize?: string | null;
  has_video: boolean;
  has_audio: boolean;
  download_url?: string | null;
  note?: string | null;
}

export interface MediaItem {
  id: string;
  title: string;
  media_type: MediaType;
  thumbnail?: string | null;
  duration?: number | null;
  duration_formatted?: string | null;
  source_url: string;
  direct_url?: string | null;
  formats: MediaFormat[];
  width?: number | null;
  height?: number | null;
  original_filename?: string | null;
}

export interface MediaAnalysisResponse {
  success: boolean;
  url: string;
  source: string;
  extractor_name: string;
  title: string;
  thumbnail?: string | null;
  duration?: number | null;
  duration_formatted?: string | null;
  media_type: MediaType;
  is_multi: boolean;
  items_count: number;
  items: MediaItem[];
  formats: MediaFormat[];
  notice?: string | null;
}

export type DownloadStatus = 'pending' | 'downloading' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface DownloadJobStatus {
  job_id: string;
  status: DownloadStatus;
  progress: number;
  message: string;
  filename?: string | null;
  filesize_bytes?: number | null;
  filesize_formatted?: string | null;
  download_url?: string | null;
  error?: string | null;
  created_at: string;
  expires_at?: string | null;
  is_archive: boolean;
}

export interface SystemInfo {
  name: string;
  version: string;
  ffmpeg_available: boolean;
  max_file_size_mb: number;
  file_retention_minutes: number;
  supported_video_formats: string[];
  supported_audio_formats: string[];
  supported_image_formats: string[];
}
