import telebot
import requests
import urllib.request
from html.parser import HTMLParser
from lxml import html
from requests_html import HTMLSession
import os
import pandas as pd
from io import StringIO
from urllib.parse import urlparse
import json
import time

# Replace YOUR_API_KEY and YOUR_BOT_TOKEN with your actual API key and bot token
api_key = ""
bot_token = ""

endpoint = "https://api.real-debrid.com/rest/1.0/unrestrict/link"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/x-www-form-urlencoded"
}

bot = telebot.TeleBot(bot_token)

def fetch_proxy_list():
    response = requests.get("https://mtpro.xyz/api/?type=socks")
    proxy_list = json.loads(response.text)
    return proxy_list

def select_proxy(proxy_list):
    current_time = int(time.time())
    proxy_index = current_time // (8 * 60 * 60) % len(proxy_list)
    return proxy_list[proxy_index]

@bot.message_handler()
def handle_unrestrict(message):
    proxy_list = fetch_proxy_list()
    proxy = select_proxy(proxy_list)
    
    link = message.text.split()[0]
    if(link.startswith('https://controlc.com')):
        links = get_links(url=link)

        for l in links:
            pLink = get_premium_link(l, proxy)

            if(isinstance(pLink, int) == False):
                filename = pLink['filename']
                host = pLink['host']
                unrestricted_link = pLink['download']

                # Download the file
                file_path = download_file(unrestricted_link, proxy)
                
                # Upload the downloaded file to Telegram
                with open(file_path, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=f"*Archivo:* {filename}\n*Host:* {host}", parse_mode='Markdown')
                
                # Remove the downloaded file
                os.remove(file_path)
            else:
                bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')

    elif is_url(link):
        pLink = get_premium_link(link, proxy)
        if(isinstance(pLink, int) == False):
            filename = pLink['filename']
            host = pLink['host']
            unrestricted_link = pLink['download']
            
            # Download the file
            file_path = download_file(unrestricted_link, proxy)
                
            # Upload the downloaded file to Telegram
            with open(file_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption=f"*Archivo:* {filename}\n*Host:* {host}", parse_mode='Markdown')
            
            # Remove the downloaded file
            os.remove(file_path)
        else:
            bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')

def get_premium_link(url, proxy):
    # Replace mirror hosts with "turbobit.net"
    for mirror_host in ['turbobif.com', 'turbobit.com', 'turb.to', 'turb.pw', 'turb.cc', 'turbo.to', 'turbo.pw', 'turbo.cc', 'turbobit.net', 'trbbt.net']:
        url = url.replace(mirror_host, 'turbobit.net')

    response = requests.post(endpoint, headers=headers, data={"link": url}, proxies=proxy)

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

def download_file(url, proxy=None):
    response = requests.get(url, proxies=proxy)
    filename = url.split("/")[-1]
    with open(filename, "wb") as file:
        file.write(response.content)
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
        
# Start the bot
bot.polling()
