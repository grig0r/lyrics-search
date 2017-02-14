import re
from urllib.parse import urlsplit

from . import tekstowo
from . import genius
from .string_utils import string_contained_percentage
from .song_utils import create_song

class Finder(object):
    """Class for finding song lyrics on the web."""

    def __init__(self, google=True, duckduckgo=True, max_results=10, max_songs=3):
        """Arguments:
        duckduckgo -- enable ddg search engine
        google -- enable google search engine
        max_results -- max amount of results fetched per search engine
        max_songs -- max amount of songs fetched per search engine
        """
        self.google = google
        self.duckduckgo = duckduckgo
        self.max_results = max_results
        self.max_songs = max_songs
        self.backends = []
        if self.google:
            import gclient
            self.backends.append(gclient)
        if self.duckduckgo:
            import ddgclient
            self.backends.append(ddgclient)

    def filter_by_domain(self, results, domain):
        return [r for r in results
            if re.match(domain, urlsplit(r.url).netloc)]

    def filter_duplicates(self, results):
        out = []
        for result in results:
            if result.url not in (r.url for r in out):
                out.append(result)
        return out

    def sort_by_fitting(self, songs, title):
        sorted_songs = sorted(
            songs,
            key=lambda s: string_contained_percentage(s.name, title),
            reverse=True
            )
        return sorted_songs

    def _find_all(self, title, website, domain, url_regex):
        all_results = []
        for engine in self.backends:
            search = engine.Search(title + ' ' + website)
            engine_results = self.filter_by_domain(search.results(self.max_results), domain)
            engine_results = [r for r in engine_results
                if re.search(url_regex, r.url)]
            all_results.extend(engine_results[:self.max_songs])
        all_results = self.filter_duplicates(all_results)
        songs = [create_song(r.url) for r in all_results]
        return songs

    def find_all_genius(self, title):
        songs = self._find_all(
            title=title,
            website='genius',
            domain=r'genius.com',
            url_regex=r'-lyrics$',
            )
        return self.sort_by_fitting(songs, title)

    def find_all_tekstowo(self, title):
        songs = self._find_all(
            title=title,
            website='tekstowo',
            domain=r'www.tekstowo.pl',
            url_regex=r'tekstowo.pl/piosenka,',
            )
        return self.sort_by_fitting(songs, title)

    def find_all(self, title, genius=True, tekstowo=True):
        """Find all songs found with given title. Returns list of *Song objects"""
        songs = []
        if genius:
            songs.extend(self.find_all_genius(title))
        if tekstowo:
            songs.extend(self.find_all_tekstowo(title))
        return self.sort_by_fitting(songs, title)

    def find(self, title, genius=True, tekstowo=True):
        """Find best fitting song for the title. Returns adequate *Song object depending on the website"""
        songs = self.find_all(title, genius, tekstowo)
        sorted_songs = self.sort_by_fitting(songs, title)
        if sorted_songs:
            return sorted_songs[0]
        else:
            return None

    def find_genius(self, title):
        return self.find(title, tekstowo=False, genius=True)

    def find_tekstowo(self, title):
        return self.find(title, tekstowo=True, genius=False)
