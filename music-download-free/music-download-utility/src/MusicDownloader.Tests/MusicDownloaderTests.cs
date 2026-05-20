using System;
using System.IO;
using System.Threading.Tasks;
using MusicDownloader.Core;
using Xunit;

namespace MusicDownloader.Tests
{
    /// <summary>
    /// Unit tests for the MusicDownloader class.
    /// </summary>
    public class MusicDownloaderTests : IDisposable
    {
        private readonly string _testDirectory;
        private readonly MusicDownloader.Core.MusicDownloader _downloader;

        public MusicDownloaderTests()
        {
            // Create a temporary directory for test downloads
            _testDirectory = Path.Combine(Path.GetTempPath(), "MusicDownloaderTests_" + Guid.NewGuid().ToString());
            Directory.CreateDirectory(_testDirectory);
            _downloader = new MusicDownloader.Core.MusicDownloader(_testDirectory);
        }

        [Fact]
        public async Task DownloadMusicAsync_ValidUrl_ReturnsFilePath()
        {
            // Arrange
            // Using a known free music sample (public domain)
            string url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3";
            string fileName = "test_song.mp3";

            // Act
            var result = await _downloader.DownloadMusicAsync(url, fileName);

            // Assert
            Assert.NotNull(result);
            Assert.True(File.Exists(result));
            Assert.EndsWith(fileName, result);
        }

        [Fact]
        public async Task DownloadMusicAsync_InvalidUrl_ThrowsException()
        {
            // Arrange
            string url = "https://invalid.example.com/nonexistent.mp3";
            string fileName = "nonexistent.mp3";

            // Act & Assert
            await Assert.ThrowsAsync<HttpRequestException>(() => _downloader.DownloadMusicAsync(url, fileName));
        }

        [Fact]
        public async Task DownloadMultipleAsync_ValidUrls_ReturnsAllPaths()
        {
            // Arrange
            var urls = new System.Collections.Generic.List<(string, string)>
            {
                ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "song1.mp3"),
                ("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", "song2.mp3")
            };

            // Act
            var results = await _downloader.DownloadMultipleAsync(urls);

            // Assert
            Assert.Equal(2, results.Count);
            foreach (var file in results)
            {
                Assert.True(File.Exists(file));
            }
        }

        [Fact]
        public void Constructor_CreatesDirectoryIfNotExists()
        {
            // Arrange
            string newDir = Path.Combine(Path.GetTempPath(), "MusicDownloaderTests_NewDir_" + Guid.NewGuid().ToString());

            // Act
            var downloader = new MusicDownloader.Core.MusicDownloader(newDir);

            // Assert
            Assert.True(Directory.Exists(newDir));

            // Cleanup
            downloader.Dispose();
            Directory.Delete(newDir);
        }

        public void Dispose()
        {
            _downloader?.Dispose();
            if (Directory.Exists(_testDirectory))
            {
                try
                {
                    Directory.Delete(_testDirectory, true);
                }
                catch
                {
                    // Ignore cleanup errors
                }
            }
        }
    }
}
