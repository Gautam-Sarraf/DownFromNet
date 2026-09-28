# DownFromNet — Universal Media Downloader

A production-grade, modular, high-performance web application to extract, preview, convert, and download publicly accessible media (videos, audio streams, image galleries, and webpage resources) across the internet.

---

## Key Features

- **Multi-Source Extraction Pipeline**:
  - Direct Media Extractor (MP4, MP3, WebM, MOV, JPG, PNG, WebP, GIF, WAV, etc.)
  - Social & Streaming Video Extractor (YouTube, Vimeo, Reddit, Twitter/X, TikTok, Soundcloud, Twitch clips, etc.)
  - Generic Webpage Extractor (OpenGraph, Twitter cards, JSON-LD schema, HTML5 `<video>`, `<audio>`, and high-res `<img>` galleries)
- **Modular Extractor Interface**: Standardized `MediaResult` normalized models for seamless expansion.
- **FFmpeg Transcoding Engine**: High-performance audio extraction (MP3, M4A, WAV), video conversions (MP4, WebM), and image conversions without unnecessary re-encoding.
- **Batch Multi-Media ZIP Packaging**: Select multiple detected media assets and package them into an organized ZIP archive.
- **Production Security & SSRF Protection**:
  - DNS resolution validation blocking loopback, private IPv4/IPv6 networks (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`, `fc00::/7`, `fe80::/10`).
  - Strict scheme whitelist (`http`/`https`).
  - Path traversal and shell injection protection.
  - Safe subprocess invocations.
- **Asynchronous Task Manager**: Real-time progress tracking with percentage calculation and background queueing.
- **Automatic TTL Storage Cleanup**: Background daemon clears temp media older than `FILE_RETENTION_MINUTES` (30 min default).
- **Modern SaaS User Interface**: Built with React, TypeScript, Tailwind CSS, Lucide icons, dark theme, interactive video/audio preview player, clipboard auto-paste, drag-and-drop link dropzone, and download history.

---

## Project Architecture

```
downFronmNet/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint & lifespan
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings & env management
│   │   │   ├── security.py      # SSRF validation & filename sanitization
│   │   │   ├── rate_limit.py    # Sliding window IP rate limiter
│   │   │   └── errors.py        # User-friendly error exceptions
│   │   ├── schemas/
│   │   │   ├── media.py         # Media metadata schemas
│   │   │   └── download.py      # Job status and batch schemas
│   │   ├── extractors/
│   │   │   ├── base.py          # BaseExtractor abstract interface
│   │   │   ├── direct.py        # Direct file extractor
│   │   │   ├── ytdlp_extractor.py # Streaming/video platform extractor
│   │   │   ├── generic_html.py  # OpenGraph/HTML5/Gallery parser
│   │   │   └── registry.py      # Extractor registry & cascading fallback
│   │   ├── services/
│   │   │   ├── analyzer.py      # URL analysis orchestrator
│   │   │   ├── downloader.py    # Async download manager & progress tracking
│   │   │   ├── converter.py     # FFmpeg transcoding service
│   │   │   ├── archiver.py      # ZIP bundle archiver
│   │   │   └── cleanup.py       # Background storage TTL cleanup daemon
│   │   ├── api/
│   │   │   ├── router.py        # Aggregated API routes
│   │   │   └── routes/
│   │   │       ├── health.py    # Health and system capabilities
│   │   │       ├── analyze.py   # URL inspection endpoint
│   │   │       └── download.py  # Single/batch download endpoints
│   │   └── utils/
│   │       ├── mime.py          # MIME types & format helpers
│   │       └── text.py          # Text cleanup & domain parser
│   ├── tests/                   # Security, extractor, & API test suites
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, UrlInput, PreviewCard, MultiGrid, ProgressModal, History
│   │   ├── hooks/               # useMediaAnalyzer, useDownloadManager
│   │   ├── services/api.ts      # Axios API client
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── index.css
│   ├── Dockerfile
│   └── package.json
│
├── nginx/
│   └── default.conf             # Reverse proxy config
├── docker-compose.yml
└── README.md
```

---

## Quick Start (Local Development)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run test suite
PYTHONPATH=. pytest -v

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

Backend will be live at `http://localhost:8000` (API Docs: `http://localhost:8000/docs`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at `http://localhost:3000` with instant proxy to backend.

---

## Running with Docker Compose

```bash
docker compose up --build
```

- Web Application: `http://localhost:3000`
- API & Health: `http://localhost:8000/health`

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | System health and storage status |
| `GET` | `/api/system/info` | Supported formats and limits |
| `POST` | `/api/analyze` | Validate & extract media metadata from URL |
| `POST` | `/api/download` | Start asynchronous single download or conversion job |
| `POST` | `/api/download/batch` | Start batch download & package into ZIP |
| `GET` | `/api/download/{id}/status` | Check live job progress percentage and status |
| `GET` | `/api/download/file/{id}` | Download the completed file/ZIP |
| `DELETE` | `/api/download/{id}` | Cancel active download and purge temp file |
| `GET` | `/api/history` | List recent download tasks |

---

## Legal & Terms Compliance

This software is designed exclusively for downloading publicly accessible media that the user is authorized to access. It does not circumvent digital rights management (DRM), authentication gates, or paywalls.
