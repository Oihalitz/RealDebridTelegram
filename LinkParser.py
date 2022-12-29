import urllib.request
from html.parser import HTMLParser
from lxml import html
from requests_html import HTMLSession
import sys
import pandas as pd

class LinkParser:
    def __init__(self,url):
        self.url = url
        self.fullscreen_url = ''
        self.raw_links = self.__get_links()
        self.links = self.__get_filtered_links()
    

    def __get_links(self):
        req = urllib.request.Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        cn = html.fromstring(response.read())

        sel = cn.xpath('//*[@id="pasteFrame"]')[0].get('src')
        self.fullscreen_url = sel

        session = HTMLSession()
        r = session.get(self.fullscreen_url)
        c = r.html.render()
        links = r.html.xpath('//*[@id="thepaste"]/text()')[0].split('\n')
        return links

    def __get_filtered_links(self):
        links = self.raw_links
        array_links = ['rapidgator.net']

        filtered_links = list(filter(lambda x: any(link in x for link in array_links), links))

        if filtered_links == []:
            array_links = ['katfile.com']
            filtered_links = list(filter(lambda x: any(link in x for link in array_links), links))

            array_links = ['katfile.com']

        return filtered_links

    def get_filtered_links(self):
        return self.links

    def get_raw_links(self):
        return self.raw_links    

linkparser = LinkParser(sys.argv[1])
links = linkparser.get_filtered_links()
for link in links:
    print(link)