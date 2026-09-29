import axios from 'axios';
import { MediaAnalysisResponse, DownloadJobStatus, SystemInfo } from '../types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const api = {
  // Analyze URL
  async analyzeUrl(url: string): Promise<MediaAnalysisResponse> {
    const response = await apiClient.post<MediaAnalysisResponse>('/analyze', { url });
    return response.data;
  },

  // Initiate single download
  async startDownload(params: {
    url: string;
    media_item_id?: string;
    format_id?: string;
    target_format?: string;
    quality?: string;
    direct_url?: string;
    custom_filename?: string;
  }): Promise<DownloadJobStatus> {
    const response = await apiClient.post<DownloadJobStatus>('/download', params);
    return response.data;
  },

  // Initiate batch ZIP download
  async startBatchDownload(params: {
    url: string;
    item_ids: string[];
    archive_name?: string;
    target_format?: string;
  }): Promise<DownloadJobStatus> {
    const response = await apiClient.post<DownloadJobStatus>('/download/batch', params);
    return response.data;
  },

  // Check download status
  async getDownloadStatus(jobId: string): Promise<DownloadJobStatus> {
    const response = await apiClient.get<DownloadJobStatus>(`/download/${jobId}/status`);
    return response.data;
  },

  // Cancel/delete download job
  async cancelDownload(jobId: string): Promise<void> {
    await apiClient.delete(`/download/${jobId}`);
  },

  // Get download history
  async getHistory(): Promise<DownloadJobStatus[]> {
    const response = await apiClient.get<DownloadJobStatus[]>('/history');
    return response.data;
  },

  // System info & health
  async getSystemInfo(): Promise<SystemInfo> {
    const response = await apiClient.get<SystemInfo>('/system/info');
    return response.data;
  },

  async getHealth(): Promise<{ status: string; ffmpeg_available: boolean }> {
    const response = await apiClient.get('/health');
    return response.data;
  }
};
