import asyncio
from pyrogram import Client, filters, enums
import requests
from urllib.parse import urlparse
import aiohttp
from aiohttp import TCPConnector, ClientTimeout
import time
from moviepy.editor import VideoFileClip
import os

# Replace YOUR_API_KEY and YOUR_BOT_TOKEN with your actual API key and bot token
api_id = ""
api_hash = ""
bot_token = ""

# Real-debrid
api_key = "I3FKSFPTCAVWHNPUSEPVMJPSZBWRTMRZ7HVLH5ILDSRIC35DKA6A"
endpoint = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/x-www-form-urlencoded"
}

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def update_progress_message(progress_message, current, total):
    progress_percent = current * 100 / total
    progress_bar = "█" * int(progress_percent / 5) + " " * (20 - int(progress_percent / 5))
    current_size = convert_size(current)
    total_size = convert_size(total)
    try:
        await progress_message.edit_text(f"[{progress_bar}] {progress_percent:.1f}% ({current_size}/{total_size})")
    except Exception as e:
        pass

def convert_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < (1024 ** 2):
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < (1024 ** 3):
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

import time

async def download_file(url, client, chat_id):
    progress_message = await client.send_message(chat_id, "Descargando...")
    connector = TCPConnector(limit_per_host=10)
    timeout = ClientTimeout(total=1800)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()

            total_size = response.headers.get('Content-Length')
            if total_size:
                total_size = int(total_size)
            else:
                total_size = None

            filename = url.split("/")[-1]
            downloaded_size = 0
            chunk_size = 10240
            update_threshold = total_size / 100 if total_size else 512 * 1024
            
            last_update_time = time.time()
            min_update_interval = 2 

            with open(filename, "wb") as file:
                async for chunk in response.content.iter_chunked(chunk_size):
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    current_time = time.time()
                    if (downloaded_size % update_threshold < chunk_size) and (current_time - last_update_time >= min_update_interval):
                        await update_progress_message(progress_message, downloaded_size, total_size)
                        last_update_time = current_time
            await progress_message.delete()
            return filename
        
async def progress_callback(current, total, progress_message, last_update_time):
    current_time = time.time()
    if current_time - last_update_time[0] < 2:
        return

    progress_percent = current * 100 / total
    progress_bar = "█" * int(progress_percent / 5) + " " * (20 - int(progress_percent / 5))
    current_size = convert_size(current)
    total_size = convert_size(total)
    try:
        await progress_message.edit_text(f"Subiendo... [{progress_bar}] {progress_percent:.1f}% ({current_size}/{total_size})")
        last_update_time[0] = current_time
    except Exception as e:
        print(f"Error updating upload progress: {str(e)}")


async def progress_callback(current, total, progress_message, last_update_time):
    current_time = time.time()
    if current_time - last_update_time[0] < 2:
        return

    progress_percent = current * 100 / total
    progress_bar = "█" * int(progress_percent / 5) + " " * (20 - int(progress_percent / 5))
    current_size = convert_size(current)
    total_size = convert_size(total)
    try:
        await progress_message.edit_text(f"Subiendo... [{progress_bar}] {progress_percent:.1f}% ({current_size}/{total_size})")
        last_update_time[0] = current_time
    except Exception as e:
        print(f"Error updating upload progress: {str(e)}")

async def upload_file(file_path, client, message, filename, host):
    progress_message = await message.reply_text("Iniciando la subida del archivo...")
    last_update_time = [time.time()]

    with open(file_path, 'rb') as f:
        try:
            if file_path.endswith('.mp4'):
                clip = VideoFileClip(file_path)
                width, height = clip.size
                await client.send_video(
                    message.chat.id, f, caption=f"**Archivo:** {filename}\n**Host:** {host}",
                    width=width, height=height,
                    progress=progress_callback, progress_args=(progress_message, last_update_time)
                )
            else:
                await client.send_document(
                    message.chat.id, f, caption=f"**Archivo:** {filename}\n**Host:** {host}",
                    progress=progress_callback, progress_args=(progress_message, last_update_time)
                )
        finally:
            os.remove(file_path)
            await progress_message.delete()

def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_premium_link(url):
    response = requests.post(endpoint, headers=headers, data={"link": url})
    if response.status_code == 200 and 'error' not in response.json():
        data = response.json()
        return {
            'filename': data['filename'],
            'host': data['host'],
            'download': data['download']
        }
    else:
        return None

@app.on_message(filters.private & filters.text)
async def handle_unrestrict(client, message):
    link = message.text.split()[0]
    if is_url(link):
        pLink = get_premium_link(link)
        if pLink:
            file_path = await download_file(pLink['download'], client, message.chat.id)
            await upload_file(file_path, client, message, pLink['filename'], pLink['host'])
        else:
            await message.reply_text('Enlace inválido ♿️', parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply_text('Por favor proporciona un enlace válido.', parse_mode=enums.ParseMode.MARKDOWN)

async def main():
    await app.start()
    print("Bot started!")
    await asyncio.Future() 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
