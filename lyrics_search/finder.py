import re
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor as Pool
from collections import deque
from functools import partial
from itertools import chain, islice

from lyrics_search.loader import maybe_load, DummyModule
ddgclient = maybe_load('ddgclient')
gclient = maybe_load('gclient')

from .string_utils import string_contained_percentage
from .song_utils import create_song

def uniq_attr(iterable, attr):
    """return iterable without repeated element attributes"""
    used_attrs = deque()
    for i in iterable:
        current_attr = getattr(i, attr)
        if current_attr not in used_attrs:
            yield i
            used_attrs.append(current_attr)

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
            self._add_backend(gclient)
        if self.duckduckgo:
            self._add_backend(ddgclient)

    def _add_backend(self, engine):
        if isinstance(engine, DummyModule):
            engine._raise()
        else:
            self.backends.append(engine)

    def sort_by_fitting(self, songs, title):
        sorted_songs = sorted(
            songs,
            key=lambda s: string_contained_percentage(s.name, title),
            reverse=True
            )
        return sorted_songs

    def _is_website_result(self, result, domain, url_regex):
        url = result.url
        if not re.match(domain, urlsplit(url).netloc):
            return False
        elif not url_regex.search(url):
            return False
        else:
            return True

    def _find_all_engine_results(self, engine, title, website, filtering_func):
        search = engine.Search('{} {}'.format(title, website))
        results = filter(filtering_func, search.results(self.max_results))
        return islice(results, self.max_songs)

    def _find_all_website_results(self, title, website, filtering_func):
        get_engine_results = partial(self._find_all_engine_results,
            title=title, website=website, filtering_func=filtering_func)
        with Pool() as pool:
            results = uniq_attr(chain.from_iterable(pool.map(
                get_engine_results,
                self.backends
                )), 'url')
        return results

    def _is_genius_result(self, result):
        return self._is_website_result(
            result=result, domain='genius.com', url_regex=re.compile('-lyrics$')
            )

    def _find_all_genius_results(self, title):
        return self._find_all_website_results(
            title=title,
            website='genius',
            filtering_func=self._is_genius_result,
            )

    def _is_tekstowo_result(self, result):
        return self._is_website_result(
            result=result,
            domain='www.tekstowo.pl',
            url_regex=re.compile('tekstowo.pl/piosenka,'),
            )

    def _find_all_tekstowo_results(self, title):
        return self._find_all_website_results(
            title=title,
            website='tekstowo',
            filtering_func=self._is_tekstowo_result,
            )

    def _results_to_songs(self, results):
        urls = map(lambda r: r.url, results)
        with Pool() as pool:
            songs = pool.map(create_song, urls)
        return songs

    def find_all(self, title, genius=True, tekstowo=True):
        """Find all songs found with given title. Returns list of *Song objects"""
        result_funcs = \
            ([self._find_all_genius_results] if genius else []) + \
            ([self._find_all_tekstowo_results] if tekstowo else [])
        with Pool() as pool:
            results = chain.from_iterable(pool.map(
                lambda func: func(title),
                result_funcs
                ))
        songs = filter(
            lambda s: s.lyrics is not None,
            self._results_to_songs(results)
            )
        return list(songs)

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
