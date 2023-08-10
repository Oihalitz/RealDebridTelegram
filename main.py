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


# Replace YOUR_API_KEY and YOUR_BOT_TOKEN with your actual API key and bot token
api_key = ""
bot_token = ""

endpoint = "https://api.real-debrid.com/rest/1.0/unrestrict/link"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/x-www-form-urlencoded"
}

bot = telebot.TeleBot(bot_token)
@bot.message_handler()
def handle_unrestrict(message):
    link = message.text.split()[0]
    if(link.startswith('https://controlc.com')):
        links = get_links(url=link)

        for l in links:
            pLink = get_premium_link(l)

            if(isinstance(pLink, int) == False):
                filename = pLink['filename']
                host = pLink['host']
                unrestricted_link = pLink['download']

                bot.send_message(message.chat.id, '*Archivo:* '+filename+'\n*Host:* '+host+'\n[Descargar]('+unrestricted_link+')', parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')

            
    elif is_url(link):
        pLink = get_premium_link(link)
        if(isinstance(pLink, int) == False):
            filename = pLink['filename']
            host = pLink['host']
            unrestricted_link = pLink['download']
            bot.send_message(message.chat.id, '*Archivo:* '+filename+'\n*Host:* '+host+'\n[Descargar]('+unrestricted_link+')', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')



    else:
        bot.send_message(message.chat.id, 'Enlace inválido ♿️', parse_mode='Markdown')

def get_premium_link(url):
    # Replace mirror hosts with "turbobit.net"
    for mirror_host in ['turbobif.com', 'turbobit.com', 'turb.to', 'turb.pw', 'turb.cc', 'turbo.to', 'turbo.pw', 'turbo.cc', 'turbobit.net', 'trbbt.net']:
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
