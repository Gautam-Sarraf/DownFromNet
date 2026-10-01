import axios from 'axios';
import { MediaAnalysisResponse, DownloadJobStatus, SystemInfo } from '../types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

apiClient.interceptors.response.use((response) => {
  if (typeof response.data === 'string' && (response.data.trim().startsWith('<!doctype html') || response.data.trim().startsWith('<!DOCTYPE html') || response.data.trim().startsWith('<html'))) {
    throw new Error('API endpoint returned HTML instead of API data. Ensure VITE_API_URL points to your backend URL (e.g. https://downfromnet-backend.onrender.com/api).');
  }
  return response;
});

export const api = {
  // Analyze URL
  async analyzeUrl(url: string): Promise<MediaAnalysisResponse> {
    const response = await apiClient.post<MediaAnalysisResponse>('/analyze', { url });
    return response.data;
  },

  // Get Direct Streaming Download URL
  getStreamDownloadUrl(params: {
    url: string;
    format_id?: string;
    target_format?: string;
    custom_filename?: string;
    direct_url?: string;
  }): string {
    const base = import.meta.env.VITE_API_URL || '/api';
    const query = new URLSearchParams({
      url: params.url,
      ...(params.format_id ? { format_id: params.format_id } : {}),
      ...(params.target_format ? { target_format: params.target_format } : {}),
      ...(params.custom_filename ? { custom_filename: params.custom_filename } : {}),
      ...(params.direct_url ? { direct_url: params.direct_url } : {}),
    });
    return `${base}/download/stream?${query.toString()}`;
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
