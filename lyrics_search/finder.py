import re
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor as Pool
from collections import deque

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

    def _filter_by_domain(self, results, domain):
        return [r for r in results
            if re.match(domain, urlsplit(r.url).netloc)]

    def _filter_duplicates(self, results):
        out = deque()
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

    def _find_all_results(self, title, website, domain, url_regex, engine):
        search = engine.Search(title + ' ' + website)
        results = self._filter_by_domain(search.results(self.max_results), domain)
        results = [r for r in results
            if re.search(url_regex, r.url)]
        results = results[:self.max_songs]
        return results

    def _find_all_results_futures(self, title, website, domain, url_regex):
        futures = deque()
        with Pool() as pool:
            for engine in self.backends:
                futures.append(pool.submit(
                    self._find_all_results,
                    title=title,
                    website=website,
                    domain=domain,
                    url_regex=url_regex,
                    engine=engine
                    ))
        return futures

    def _find_all_genius_results_futures(self, title):
        futures = self._find_all_results_futures(
            title=title,
            website='genius',
            domain=r'genius.com',
            url_regex=r'-lyrics$',
            )
        return futures

    def _find_all_tekstowo_results_futures(self, title):
        futures = self._find_all_results_futures(
            title=title,
            website='tekstowo',
            domain=r'www.tekstowo.pl',
            url_regex=r'tekstowo.pl/piosenka,',
            )
        return futures

    def _results_to_songs(self, results):
        urls = (r.url for r in results)
        with Pool() as pool:
            songs = list(pool.map(create_song, urls))
        return songs

    def find_all(self, title, genius=True, tekstowo=True):
        """Find all songs found with given title. Returns list of *Song objects"""
        results_futures = deque()
        if genius:
            results_futures.extend(self._find_all_genius_results_futures(title))
        if tekstowo:
            results_futures.extend(self._find_all_tekstowo_results_futures(title))
        results = deque()
        for future in results_futures:
            results.extend(future.result())
        results = self._filter_duplicates(results)
        songs = self._results_to_songs(results)
        songs = list(filter(lambda s: s.lyrics, songs))
        return self.sort_by_fitting(songs, title)

    def find_all_genius(self, title):
        return self.find_all(title, genius=True, tekstowo=False)

    def find_all_tekstowo(self, title):
        return self.find_all(title, genius=False, tekstowo=True)

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
