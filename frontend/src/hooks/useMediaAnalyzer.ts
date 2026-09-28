import { useState, useCallback } from 'react';
import { api } from '../services/api';
import { MediaAnalysisResponse } from '../types';

export function useMediaAnalyzer() {
  const [url, setUrl] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<MediaAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (targetUrl?: string) => {
    const inputUrl = (targetUrl || url).trim();
    if (!inputUrl) {
      setError('Please paste or enter a URL first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.analyzeUrl(inputUrl);
      setResult(data);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to analyze URL. Please check the link and try again.';
      setError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  }, [url]);

  const clear = useCallback(() => {
    setUrl('');
    setResult(null);
    setError(null);
  }, []);

  return {
    url,
    setUrl,
    isAnalyzing,
    result,
    error,
    analyze,
    clear,
  };
}
