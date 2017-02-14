import requests
from bs4 import BeautifulSoup

from .song import Song

class GeniusSong(Song):

    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup()
        self.lyrics = self._fetch_lyrics()
        self.title = self._fetch_title()
        self.artist = self._fetch_artist()

    @property
    def name(self):
        return '{} {}'.format(self.artist, self.title)

    def _get_soup(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def _fetch_lyrics(self):
        lyrics_tag = self.soup.lyrics
        text = lyrics_tag.p.get_text()
        return text

    def _fetch_title(self):
        title = self.soup.find(class_='song_header-primary_info-title').get_text()
        return title

    def _fetch_artist(self):
        info_tag = self.soup.find('div', class_='song_header-primary_info')
        artist = info_tag.find(class_='song_header-primary_info-primary_artist').get_text()
        return artist
