import requests
from bs4 import BeautifulSoup
import re

from .song import Song

class TekstowoSong(Song):

    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup()
        self.lyrics = self._fetch_lyrics()
        self.artist, self.title = self._fetch_artist_title()

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return '{} {}'.format(self.artist, self.title)

    def _get_soup(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def _fetch_lyrics(self):
        text_tag = self.soup.find('div', class_='song-text')
        if not text_tag:
            return None
        text = ' '.join(text_tag.find_all(text=True, recursive=False))
        text = re.sub(r'^\s*(.*?)\s*$', r'\1', text, flags=re.DOTALL)
        return text

    def _fetch_artist_title(self):
        belka_tag = self.soup.select_one('div.belka.short')
        name = belka_tag.strong.get_text()
        match = re.match(r'^(.*?) - (.*?)$', name)
        return match.group(1), match.group(2)
