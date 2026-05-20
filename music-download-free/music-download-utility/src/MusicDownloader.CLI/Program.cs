using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using MusicDownloader.Core;

namespace MusicDownloader.CLI
{
    /// <summary>
    /// Command-line interface for the music download utility.
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("Music Download Utility - Free Music Downloader");
            Console.WriteLine("----------------------------------------------");

            if (args.Length < 2)
            {
                Console.WriteLine("Usage: music-download-utility <download-directory> <url1> [url2] ... [urlN]");
                Console.WriteLine("Example: music-download-utility ./downloads https://example.com/song.mp3");
                return;
            }

            string downloadDir = args[0];
            var urls = new List<(string url, string fileName)>();

            for (int i = 1; i < args.Length; i++)
            {
                string url = args[i];
                // Extract file name from URL or generate a default one
                string fileName = ExtractFileNameFromUrl(url);
                urls.Add((url, fileName));
            }

            var downloader = new MusicDownloader.Core.MusicDownloader(downloadDir);

            try
            {
                var downloadedFiles = await downloader.DownloadMultipleAsync(urls);
                Console.WriteLine($"\nSuccessfully downloaded {downloadedFiles.Count} file(s):");
                foreach (var file in downloadedFiles)
                {
                    Console.WriteLine($"  - {file}");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"An error occurred: {ex.Message}");
            }
            finally
            {
                downloader.Dispose();
            }
        }

        /// <summary>
        /// Extracts a file name from a URL. Falls back to a timestamp-based name if extraction fails.
        /// </summary>
        /// <param name="url">The URL to extract from.</param>
        /// <returns>A valid file name with extension.</returns>
        private static string ExtractFileNameFromUrl(string url)
        {
            try
            {
                var uri = new Uri(url);
                var segments = uri.Segments;
                var lastSegment = segments[^1];

                // Decode URL-encoded characters and validate file name
                var decoded = Uri.UnescapeDataString(lastSegment);
                if (!string.IsNullOrWhiteSpace(decoded) && decoded.Contains('.'))
                {
                    // Remove query parameters if any
                    var cleanName = decoded.Split('?')[0];
                    return cleanName;
                }
            }
            catch
            {
                // Fall through to default
            }

            // Default: generate a name with timestamp
            return $"download_{DateTime.UtcNow:yyyyMMddHHmmssfff}.mp3";
        }
    }
}
