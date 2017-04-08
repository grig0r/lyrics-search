class Song(object):

    def __init__(self, url, title, artist, lyrics):
        self.url = url
        self.title = title
        self.artist = artist
        self.lyrics = lyrics

    @property
    def name(self):
        return '{} {}'.format(self.artist, self.title)

    def __repr__(self):
        return '<{} ({})>'.format(self.__class__.__name__, self.url)

    def __eq__(self, other):
        if isinstance(other, Song):
            return (self.url, self.title, self.artist, self.lyrics) == \
                (other.url, other.title, other.artist, other.lyrics)
        else:
            return False

    def __hash__(self):
        return hash((Song, self.url, self.title, self.artist, self.lyrics))
