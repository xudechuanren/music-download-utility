using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace MusicDownloader.Core
{
    /// <summary>
    /// Provides functionality to download music files from free music sources.
    /// </summary>
    public class MusicDownloader
    {
        private readonly HttpClient _httpClient;
        private readonly string _downloadDirectory;

        /// <summary>
        /// Initializes a new instance of the <see cref="MusicDownloader"/> class.
        /// </summary>
        /// <param name="downloadDirectory">Directory where downloaded files will be saved.</param>
        public MusicDownloader(string downloadDirectory)
        {
            _httpClient = new HttpClient();
            _downloadDirectory = downloadDirectory;

            if (!Directory.Exists(_downloadDirectory))
            {
                Directory.CreateDirectory(_downloadDirectory);
            }
        }

        /// <summary>
        /// Downloads a music file from the specified URL and saves it to the download directory.
        /// </summary>
        /// <param name="url">The direct URL to the music file (e.g., .mp3, .wav).</param>
        /// <param name="fileName">The desired file name (including extension).</param>
        /// <returns>The full path to the downloaded file.</returns>
        public async Task<string> DownloadMusicAsync(string url, string fileName)
        {
            if (string.IsNullOrWhiteSpace(url))
                throw new ArgumentException("URL cannot be empty.", nameof(url));
            if (string.IsNullOrWhiteSpace(fileName))
                throw new ArgumentException("File name cannot be empty.", nameof(fileName));

            var filePath = Path.Combine(_downloadDirectory, fileName);

            try
            {
                var response = await _httpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();

                using (var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    await response.Content.CopyToAsync(fileStream);
                }

                Console.WriteLine($"Downloaded: {fileName} to {filePath}");
                return filePath;
            }
            catch (HttpRequestException ex)
            {
                Console.Error.WriteLine($"HTTP error downloading {url}: {ex.Message}");
                throw;
            }
            catch (IOException ex)
            {
                Console.Error.WriteLine($"File I/O error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Downloads multiple music files concurrently.
        /// </summary>
        /// <param name="urls">A list of tuples containing URL and desired file name.</param>
        /// <returns>A list of paths to the downloaded files.</returns>
        public async Task<List<string>> DownloadMultipleAsync(List<(string url, string fileName)> urls)
        {
            var tasks = urls.Select(item => DownloadMusicAsync(item.url, item.fileName));
            var results = await Task.WhenAll(tasks);
            return results.ToList();
        }

        /// <summary>
        /// Disposes the HTTP client resources.
        /// </summary>
        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
