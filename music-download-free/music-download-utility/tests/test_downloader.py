"""
Unit tests for the MusicDownloader class.
Uses pytest and mock objects to avoid actual network calls.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.downloader import MusicDownloader


@pytest.fixture
def downloader(tmpdir):
    """Fixture providing a MusicDownloader instance with temp directory."""
    return MusicDownloader(output_dir=str(tmpdir))


def test_init_creates_directory(tmpdir):
    """Test that initialization creates the output directory."""
    output_dir = str(tmpdir.join("custom_downloads"))
    downloader = MusicDownloader(output_dir=output_dir)
    assert os.path.exists(output_dir)
    assert os.path.isdir(output_dir)


def test_download_from_youtube_success(downloader):
    """Test successful YouTube download with mocked youtube_dl."""
    mock_return_path = os.path.join(downloader.output_dir, "test_song.mp3")
    with patch("src.downloader.youtube_dl.YoutubeDL") as mock_ydl:
        mock_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {"title": "test_song"}
        mock_instance.prepare_filename.return_value = mock_return_path

        # Simulate file creation by postprocessor
        with open(mock_return_path, "w") as f:
            f.write("dummy audio")

        result = downloader.download_from_youtube("https://youtube.com/watch?v=test")
        assert result == mock_return_path
        mock_instance.extract_info.assert_called_once()


def test_download_from_youtube_failure(downloader):
    """Test YouTube download failure handling."""
    with patch("src.downloader.youtube_dl.YoutubeDL") as mock_ydl:
        mock_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.side_effect = Exception("Network error")

        result = downloader.download_from_youtube("https://youtube.com/watch?v=bad")
        assert result is None


def test_download_from_direct_url_success(downloader):
    """Test direct URL download with mocked requests."""
    with patch("src.downloader.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"audio data chunk"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = downloader.download_from_direct_url("https://example.com/song.mp3", "song.mp3")
        expected_path = os.path.join(downloader.output_dir, "song.mp3")
        assert result == expected_path
        assert os.path.exists(expected_path)
        with open(expected_path, "rb") as f:
            assert f.read() == b"audio data chunk"


def test_download_from_direct_url_failure(downloader):
    """Test direct URL download failure."""
    with patch("src.downloader.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        result = downloader.download_from_direct_url("https://example.com/bad.mp3", "bad.mp3")
        assert result is None


def test_list_downloads_empty(downloader):
    """Test listing downloads when directory is empty."""
    assert downloader.list_downloads() == []


def test_list_downloads_with_files(downloader):
    """Test listing downloads with existing files."""
    # Create some dummy files
    open(os.path.join(downloader.output_dir, "song1.mp3"), "w").close()
    open(os.path.join(downloader.output_dir, "song2.mp3"), "w").close()
    files = downloader.list_downloads()
    assert len(files) == 2
    assert "song1.mp3" in files
    assert "song2.mp3" in files
