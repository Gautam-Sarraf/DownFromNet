from typing import Optional, Any, Callable
from app.core.config import settings
from app.core.cookies import get_cookie_file_path


class YouTubeExtractorConfig:
    """
    Centralized configuration engine for YouTube extraction and media acquisition.
    Encapsulates yt-dlp options, EJS JavaScript runtimes, PO-tokens, format selectors, and timeouts.
    """
    DEFAULT_SOCKET_TIMEOUT = 12
    DOWNLOAD_SOCKET_TIMEOUT = 30

    @classmethod
    def get_js_runtimes(cls) -> dict[str, Any]:
        """Returns JavaScript runtime configuration for solving YouTube n-sig challenges."""
        return {"node": {}}

    @classmethod
    def get_extractor_args(
        cls,
        po_token: Optional[str] = None,
        player_clients: Optional[list[str]] = None,
        has_cookies: bool = False
    ) -> dict[str, Any]:
        """
        Builds yt-dlp extractor arguments for YouTube.
        """
        yt_args: dict[str, Any] = {}

        if player_clients:
            yt_args["player_client"] = player_clients

        # Proof of Origin (PO-Token)
        token = po_token or settings.YOUTUBE_PO_TOKEN
        if token and token.strip():
            yt_args["po_token"] = [
                f"web.gvs+{token.strip()}",
                f"web.player+{token.strip()}"
            ]

        return {"youtube": yt_args} if yt_args else {}

    @classmethod
    def build_format_selector(
        cls,
        format_id: Optional[str] = None,
        target_format: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Builds intelligent format selector string and container merge format.
        Distinguishes audio-only vs. video+audio vs. specific video streams.
        Returns: (format_selector_string, merge_container_format)
        """
        target_fmt = (target_format or "").lower().lstrip(".")
        merge_format = "mp4"

        # 1. Audio-only target formats (MP3, M4A, WAV)
        if target_fmt in ["mp3", "m4a", "wav", "aac", "flac"]:
            if format_id and format_id not in ["best", "direct"]:
                return f"{format_id}/bestaudio/best", "mp3" if target_fmt == "mp3" else target_fmt
            return "bestaudio/best", "mp3" if target_fmt == "mp3" else target_fmt

        # 2. Specific video stream selected
        if format_id and format_id not in ["best", "direct"]:
            selector = f"{format_id}+bestaudio[ext=m4a]/{format_id}+bestaudio/bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+{format_id}/{format_id}/best"
            if target_fmt in ["webm", "mkv", "mp4"]:
                merge_format = target_fmt
            return selector, merge_format

        # 3. Best overall video + audio stream
        if target_fmt in ["webm", "mkv", "mp4"]:
            merge_format = target_fmt

        selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        return selector, merge_format

    @classmethod
    def build_analyze_opts(
        cls,
        proxy: Optional[str] = None,
        cookie_file: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Builds options for metadata inspection without downloading media files.
        """
        c_file = cookie_file or get_cookie_file_path()
        has_cookies = bool(c_file)
        sock_timeout = timeout or cls.DEFAULT_SOCKET_TIMEOUT

        opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
            "user_agent": settings.USER_AGENT,
            "socket_timeout": sock_timeout,
            "ignoreerrors": False,
            "no_color": True,
            "format": "bestvideo+bestaudio/best/bv*+ba/b",
            "js_runtimes": cls.get_js_runtimes(),
        }

        if c_file:
            opts["cookiefile"] = c_file

        ext_args = cls.get_extractor_args(has_cookies=has_cookies)
        if ext_args:
            opts["extractor_args"] = ext_args

        if proxy:
            opts["proxy"] = proxy

        return opts

    @classmethod
    def build_download_opts(
        cls,
        output_template: str,
        format_id: Optional[str] = None,
        target_format: Optional[str] = None,
        proxy: Optional[str] = None,
        cookie_file: Optional[str] = None,
        progress_hook: Optional[Callable[[dict], None]] = None,
        timeout: Optional[int] = None
    ) -> tuple[dict[str, Any], str]:
        """
        Builds options for media acquisition and transcoding.
        Returns: (ydl_opts_dict, final_target_format)
        """
        c_file = cookie_file or get_cookie_file_path()
        has_cookies = bool(c_file)
        sock_timeout = timeout or cls.DOWNLOAD_SOCKET_TIMEOUT

        fmt_selector, merge_format = cls.build_format_selector(
            format_id=format_id,
            target_format=target_format
        )

        postprocessors: list[dict[str, Any]] = []
        target_fmt = (target_format or "").lower().lstrip(".")

        if target_fmt in ["mp3", "m4a", "wav"]:
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": target_fmt,
                "preferredquality": "192",
            })

        opts: dict[str, Any] = {
            "format": fmt_selector,
            "outtmpl": output_template,
            "merge_output_format": merge_format,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "user_agent": settings.USER_AGENT,
            "socket_timeout": sock_timeout,
            "concurrent_fragment_downloads": 8,
            "http_chunk_size": 10485760,
            "retries": 10,
            "fragment_retries": 10,
            "max_filesize": settings.MAX_FILE_SIZE_BYTES,
            "postprocessors": postprocessors,
            "js_runtimes": cls.get_js_runtimes(),
        }

        if progress_hook:
            opts["progress_hooks"] = [progress_hook]

        if c_file:
            opts["cookiefile"] = c_file

        ext_args = cls.get_extractor_args(has_cookies=has_cookies)
        if ext_args:
            opts["extractor_args"] = ext_args

        if proxy:
            opts["proxy"] = proxy

        return opts, target_fmt or merge_format
