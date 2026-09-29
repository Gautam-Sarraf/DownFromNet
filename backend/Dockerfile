# Pull static ffmpeg binaries (fast, reliable, zero debian dependency bloat)
FROM mwader/static-ffmpeg:7.1 AS ffmpeg-source

# Python 3.11 lightweight runtime
FROM python:3.11-slim

# Copy static FFmpeg binaries
COPY --from=ffmpeg-source /ffmpeg /usr/local/bin/
COPY --from=ffmpeg-source /ffprobe /usr/local/bin/

# Install basic network utilities and Node.js (needed by yt-dlp for JS challenge solving)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U yt-dlp

COPY . .

ENV PORT=8000
ENV TEMP_STORAGE_DIR=/tmp/universal_media_downloader

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
