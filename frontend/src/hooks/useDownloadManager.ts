import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';
import { DownloadJobStatus } from '../types';

export interface UseDownloadManagerOptions {
  onCompleted?: (job: DownloadJobStatus) => void;
  onError?: (error: string) => void;
}

export function useDownloadManager(options?: UseDownloadManagerOptions) {
  const [activeJob, setActiveJob] = useState<DownloadJobStatus | null>(null);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [history, setHistory] = useState<DownloadJobStatus[]>([]);
  const pollTimerRef = useRef<any>(null);
  const optionsRef = useRef(options);
  optionsRef.current = options;

  const fetchHistory = useCallback(async () => {
    try {
      const data = await api.getHistory();
      setHistory(data);
    } catch (e) {
      console.error('Failed to fetch history', e);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const pollJobStatus = useCallback(async (jobId: string) => {
    try {
      const status = await api.getDownloadStatus(jobId);
      setActiveJob(status);

      if (status.status === 'completed') {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
        setIsDownloading(false);
        fetchHistory();

        // Auto trigger browser native download (Chrome / Opera / Edge / etc.)
        if (status.download_url) {
          const downloadUrl = status.download_url.startsWith('http')
            ? status.download_url
            : `${status.download_url}`;
          
          const a = document.createElement('a');
          a.href = downloadUrl;
          a.download = status.filename || 'download';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }

        // Notify parent callback
        if (optionsRef.current?.onCompleted) {
          optionsRef.current.onCompleted(status);
        }
      } else if (status.status === 'failed' || status.status === 'cancelled') {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
        setIsDownloading(false);
        fetchHistory();

        if (status.status === 'failed' && optionsRef.current?.onError) {
          optionsRef.current.onError(status.error || status.message || 'Media preparation failed.');
        }
      }
    } catch (err: any) {
      console.error('Polling error', err);
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
      setIsDownloading(false);
      if (optionsRef.current?.onError) {
        optionsRef.current.onError(err.response?.data?.detail || 'Lost connection to download server.');
      }
    }
  }, [fetchHistory]);

  const startDownload = useCallback(async (params: {
    url: string;
    media_item_id?: string;
    format_id?: string;
    target_format?: string;
    quality?: string;
    direct_url?: string;
    custom_filename?: string;
  }) => {
    try {
      setIsDownloading(true);
      const initialJob = await api.startDownload(params);
      setActiveJob(initialJob);
      setIsModalOpen(true);

      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      pollTimerRef.current = setInterval(() => {
        pollJobStatus(initialJob.job_id);
      }, 700);

      return initialJob;
    } catch (err: any) {
      setIsDownloading(false);
      if (optionsRef.current?.onError) {
        optionsRef.current.onError(err.response?.data?.detail || 'Failed to start download.');
      }
      throw err;
    }
  }, [pollJobStatus]);

  const startBatchDownload = useCallback(async (params: {
    url: string;
    item_ids: string[];
    archive_name?: string;
    target_format?: string;
  }) => {
    try {
      setIsDownloading(true);
      const initialJob = await api.startBatchDownload(params);
      setActiveJob(initialJob);
      setIsModalOpen(true);

      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      pollTimerRef.current = setInterval(() => {
        pollJobStatus(initialJob.job_id);
      }, 800);

      return initialJob;
    } catch (err: any) {
      setIsDownloading(false);
      throw err;
    }
  }, [pollJobStatus]);

  const cancelActiveJob = useCallback(async () => {
    if (activeJob) {
      try {
        await api.cancelDownload(activeJob.job_id);
      } catch (e) {}
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
      setIsDownloading(false);
      setActiveJob(prev => prev ? { ...prev, status: 'cancelled', message: 'Cancelled by user' } : null);
    }
  }, [activeJob]);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  return {
    activeJob,
    isDownloading,
    isModalOpen,
    history,
    startDownload,
    startBatchDownload,
    cancelActiveJob,
    closeModal,
    fetchHistory
  };
}
