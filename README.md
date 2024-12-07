
 Video Uploader with API Integration
 
This project automates the process of monitoring a directory for new video files (.mp4), uploading them to a specified API, and cleaning up local files after successful uploads. The implementation uses Python's asynchronous capabilities for efficient and concurrent operations.

Features

Monitor a /videos directory for new .mp4 files.

Generate upload URLs via API.

Upload videos using pre-signed URLs.

Automatically create posts with video metadata.

Delete local files after successful upload.

Error handling for robust operation.

Concurrent uploads using asyncio.

Technologies Used

Python: Core programming language.

Libraries:

aiohttp: For asynchronous HTTP requests.

watchdog: To monitor the directory for file changes.

tqdm: For displaying progress bars during uploads.

How It Works

Directory Monitoring:

The /videos folder is monitored continuously for new .mp4 files.

API Integration:

The script requests a pre-signed URL from the API.
It uploads the video file using this URL.
It creates a post with video metadata.

Clean-Up:

After a successful upload, the .mp4 file is deleted from the local directory.

  
