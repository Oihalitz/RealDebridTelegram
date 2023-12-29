import asyncio
from pyrogram import Client, filters, enums
from urllib.parse import urlparse
import requests
import aiohttp
import asyncio
import pandas as pd
import time
from io import StringIO
from moviepy.editor import VideoFileClip
import os

# Replace YOUR_API_KEY and YOUR_BOT_TOKEN with your actual API key and bot token
api_id = ""  
api_hash = "" 
bot_token = ""

#Real-debrid
api_key = ""
endpoint = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/x-www-form-urlencoded"
}

main_loop = asyncio.get_event_loop()
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.private & filters.text)
async def handle_unrestrict(client, message):
    link = message.text.split()[0]
    if link.startswith('https://controlc.com'):
        links = get_links(url=link)

        for l in links:
            pLink = get_premium_link(l)

            if not isinstance(pLink, int):
                await message.reply_text(f'**Archivo:** {pLink["filename"]}\n**Host:** {pLink["host"]}\n[Descargar]({pLink["download"]})', parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await message.reply_text('Enlace inválido ♿️', parse_mode=enums.ParseMode.MARKDOWN)

    elif is_url(link):
        pLink = get_premium_link(link)
        if not isinstance(pLink, int):
            filename = pLink['filename']
            host = pLink['host']
            unrestricted_link = pLink['download']
            
            file_path = await download_file(unrestricted_link, client=client, chat_id=message.chat.id)
            if not os.path.exists(file_path):
                await message.reply_text("Error al descargar el archivo.")
                return
            
            global last_update_time
            last_update_time = 0
            progress_message = await message.reply_text("Iniciando la subida del archivo...")

            if file_path.endswith('.mp4'):
                with open(file_path, 'rb') as f:
                    clip = VideoFileClip(file_path)
                    width, height = clip.size
                    await client.send_video(message.chat.id, f, caption=f"**Archivo:** {filename}\n**Host:** {host}",
                                            width=width, height=height,
                                            progress=lambda current, total: progress(current, total, progress_message),
                                            parse_mode=enums.ParseMode.MARKDOWN)
            else:
                with open(file_path, 'rb') as f:
                    await client.send_document(message.chat.id, f, caption=f"**Archivo:** {filename}\n**Host:** {host}",
                                            progress=lambda current, total: progress(current, total, progress_message),
                                            parse_mode=enums.ParseMode.MARKDOWN)

            os.remove(file_path)
            await progress_message.delete()
        else:
            await message.reply_text('Enlace inválido ♿️', parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply_text('Enlace inválido ♿️', parse_mode=enums.ParseMode.MARKDOWN)


#Some defs
last_update_time = 0

def progress(current, total, progress_message):
    global last_update_time
    current_time = time.time()

    if current_time - last_update_time >= 5:  # Actualizar cada 5 segundos
        last_update_time = current_time
        coroutine = update_progress_message(progress_message, current, total)
        asyncio.run_coroutine_threadsafe(coroutine, main_loop)

def convert_size(size_bytes):
    """Convierte el tamaño de un archivo de bytes a MB o GB."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < (1024 ** 2):
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < (1024 ** 3):
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"

async def update_progress_message(progress_message, current, total):
    progress_percent = current * 100 / total
    progress_bar = "█" * int(progress_percent / 5) + " " * (20 - int(progress_percent / 5))

    # Convertir el tamaño actual y total a una unidad más grande (MB o GB)
    current_size = convert_size(current)
    total_size = convert_size(total)

    try:
        await progress_message.edit_text(f"[{progress_bar}] {progress_percent:.1f}% ({current_size}/{total_size})")
    except Exception as e:
        pass



def get_premium_link(url):
    # Replace mirror hosts with "turbobit.net"
    for mirror_host in ['turbobyt.net', 'turbobif.com', 'turbobit.com', 'turb.to', 'turb.pw', 'turb.cc', 'turbo.to', 'turbo.pw', 'turbo.cc', 'turbobit.net', 'trbbt.net']:
        url = url.replace(mirror_host, 'turbobit.net')

    response = requests.post(endpoint, headers=headers, data={"link": url})

    print(response.json())
    try:
        if response.json()['error'] in ["hoster_unsupported","unavailable_file"]:
            return response.json()['error_code']
        else:
            pass
    except:
        pass
    if response.status_code in [404,503,16,24]:
        print('ERROR: ' + response.status_code)
        return response.status_code
    else:
        filename = response.json()['filename']
        host = response.json()['host']
        unrestricted_link = response.json()['download']

        return {
            'filename': filename,
            'host': host,
            'download': unrestricted_link
        }

async def download_file(url, proxy=None, client=None, chat_id=None):
    progress_message = await client.send_message(chat_id, "Descargando...")
    last_update_time = time.time()

    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=proxy) as response:
            if response.status != 200:
                response.raise_for_status()

            total_size = response.headers.get('Content-Length')
            if total_size:
                total_size = int(total_size)
            else:
                total_size = None

            filename = url.split("/")[-1]
            downloaded_size = 0
            with open(filename, "wb") as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    current_time = time.time()

                    # Actualizar cada 5 segundos
                    if current_time - last_update_time >= 5:
                        last_update_time = current_time
                        if total_size:
                            progress = downloaded_size / total_size * 100
                            progress_bar = "█" * int(progress / 5) + " " * (20 - int(progress / 5))
                            await progress_message.edit_text(f"Descargando... [{progress_bar}] {progress:.1f}%")
            progress_message.delete
            return filename

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False


def get_links(url):
    links = os.popen('python3 LinkParser.py '+url).read()

    links = pd.read_csv(StringIO(links), header=None).values.tolist()
    print(links)
    filtered_links = []
    for link in links:
        filtered_links.append(link[0])
    
    
    return filtered_links

async def main():
    await app.start()
    print("Bot started!")
    await asyncio.Future() 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())