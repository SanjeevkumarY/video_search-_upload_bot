import os
import asyncio
import hashlib
from aiohttp import ClientSession
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tqdm.asyncio import tqdm

# Constants
VIDEOS_DIR = "./videos"
FLIC_TOKEN = "<YOUR_TOKEN>"  # Replace with your actual token
BASE_URL = "https://api.socialverseapp.com"

# Utility: Calculate file hash
def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Async: Get upload URL
async def get_upload_url(session):
    url = f"{BASE_URL}/posts/generate-upload-url"
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()

# Async: Upload video to presigned URL
async def upload_video(session, file_path, presigned_url):
    headers = {"Content-Type": "video/mp4"}
    with open(file_path, "rb") as f:
        async with session.put(presigned_url, data=f, headers=headers) as response:
            response.raise_for_status()
            return True

# Async: Create a post
async def create_post(session, title, file_hash, category_id=1):
    url = f"{BASE_URL}/posts"
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    body = {
        "title": title,
        "hash": file_hash,
        "is_available_in_public_feed": False,
        "category_id": category_id
    }
    async with session.post(url, json=body, headers=headers) as response:
        response.raise_for_status()
        return await response.json()

# Handler for monitoring /videos directory
class VideoHandler(FileSystemEventHandler):
    def __init__(self, loop, session):
        self.loop = loop
        self.session = session

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".mp4"):
            return
        self.loop.create_task(self.process_new_video(event.src_path))

    async def process_new_video(self, file_path):
        try:
            print(f"Processing new video: {file_path}")
            file_hash = calculate_file_hash(file_path)
            upload_url_data = await get_upload_url(self.session)
            await upload_video(self.session, file_path, upload_url_data["url"])
            await create_post(
                self.session,
                title=os.path.basename(file_path),
                file_hash=file_hash,
                category_id=1
            )
            os.remove(file_path)
            print(f"Uploaded and deleted: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# Main function
async def main():
    async with ClientSession() as session:
        loop = asyncio.get_event_loop()
        event_handler = VideoHandler(loop, session)
        observer = Observer()
        observer.schedule(event_handler, VIDEOS_DIR, recursive=False)
        observer.start()

        print(f"Monitoring {VIDEOS_DIR} for new videos...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    # Ensure the directory exists
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    asyncio.run(main())
