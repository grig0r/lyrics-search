from . import tekstowo
from . import genius

def create_song(url):
    domain = urlsplit(url).netloc
    if domain == 'www.tekstowo.pl':
        return tekstowo.TekstowoSong(url)
    elif domain == 'genius.com':
        return genius.GeniusSong(url)
    else:
        raise Exception('domain unknown')
