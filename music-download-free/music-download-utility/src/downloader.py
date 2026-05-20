"""
Core downloader module for music-download-utility.
Handles fetching audio from various sources and saving to disk.
"""

import os
import logging
from typing import Optional
import requests
import youtube_dl

logger = logging.getLogger(__name__)


class MusicDownloader:
    """
    A class to download music from YouTube and other supported platforms.
    Supports MP3 extraction with metadata tagging.
    """

    def __init__(self, output_dir: str = "./downloads"):
        """
        Initialize the downloader with an output directory.

        Args:
            output_dir: Directory to save downloaded files.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def download_from_youtube(self, url: str, format: str = "mp3") -> Optional[str]:
        """
        Download audio from a YouTube video.

        Args:
            url: YouTube video URL.
            format: Desired audio format (mp3, m4a, etc.).

        Returns:
            Path to the downloaded file, or None if failed.
        """
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": "192",
            }],
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                # Adjust extension after post-processing
                base, _ = os.path.splitext(filename)
                final_path = f"{base}.{format}"
                logger.info(f"Downloaded: {final_path}")
                return final_path
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

    def download_from_direct_url(self, url: str, filename: str) -> Optional[str]:
        """
        Download a music file directly from a URL.

        Args:
            url: Direct link to an audio file.
            filename: Name to save the file as.

        Returns:
            Path to the downloaded file, or None if failed.
        """
        save_path = os.path.join(self.output_dir, filename)
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"Failed to download from {url}: {e}")
            return None

    def list_downloads(self) -> list:
        """
        List all downloaded files in the output directory.

        Returns:
            List of filenames.
        """
        return [f for f in os.listdir(self.output_dir) if os.path.isfile(os.path.join(self.output_dir, f))]
