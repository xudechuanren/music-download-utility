"""
Metadata tagging module for music-download-utility.
Uses mutagen to edit ID3 tags on downloaded audio files.
"""

import os
import logging
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

logger = logging.getLogger(__name__)


class MetadataEditor:
    """
    A class to edit metadata (ID3 tags) for MP3 files.
    """

    def __init__(self):
        """Initialize the metadata editor."""
        pass

    def set_basic_tags(self, filepath: str, title: Optional[str] = None,
                       artist: Optional[str] = None, album: Optional[str] = None) -> bool:
        """
        Set basic ID3 tags (title, artist, album) on an MP3 file.

        Args:
            filepath: Path to the MP3 file.
            title: Song title.
            artist: Artist name.
            album: Album name.

        Returns:
            True if successful, False otherwise.
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False

        try:
            audio = EasyID3(filepath)
        except Exception:
            # File might not have ID3 tags yet; add them
            audio = EasyID3()
            audio.save(filepath)
            audio = EasyID3(filepath)

        if title:
            audio["title"] = title
        if artist:
            audio["artist"] = artist
        if album:
            audio["album"] = album

        audio.save()
        logger.info(f"Updated tags for {filepath}")
        return True

    def add_cover_art(self, filepath: str, image_path: str) -> bool:
        """
        Add cover art image to an MP3 file.

        Args:
            filepath: Path to the MP3 file.
            image_path: Path to the image file (JPEG or PNG).

        Returns:
            True if successful, False otherwise.
        """
        if not os.path.exists(filepath) or not os.path.exists(image_path):
            logger.error("File or image not found")
            return False

        try:
            audio = MP3(filepath, ID3=ID3)
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime="image/jpeg",
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=open(image_path, "rb").read()
                )
            )
            audio.save()
            logger.info(f"Added cover art to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to add cover art: {e}")
            return False

    def get_tags(self, filepath: str) -> dict:
        """
        Retrieve current ID3 tags from an MP3 file.

        Args:
            filepath: Path to the MP3 file.

        Returns:
            Dictionary of tags.
        """
        tags = {}
        try:
            audio = EasyID3(filepath)
            for key in audio.keys():
                tags[key] = audio[key]
        except Exception as e:
            logger.error(f"Failed to read tags: {e}")
        return tags
