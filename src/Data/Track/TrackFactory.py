from src.Data.Tagging import TagSupport
from src.Data.Track.Track import Track
from src.Data.Foundation.UniqueFactory import UniqueFactory
from src.Database.IDatabaseAdapter import IDatabaseAdapter


class TrackFactory(UniqueFactory):

    track_types = dict({})

    @classmethod
    def register(cls, track_type, constructor):
        cls.track_types[track_type] = constructor

    def __init__(self, database: IDatabaseAdapter):
        super(TrackFactory, self).__init__(Track, "title", "artist", "album")

        self.db = database

    def getTrack(self, **kwargs):

        self.setConstructor(TrackFactory.track_types[kwargs["type"]])

        track = self.new(
            title=kwargs["title"],
            artist=kwargs["artist"],
            album=kwargs["album"]
        )

        for key in set(kwargs) - {"type", "title", "artist", "album"}:
            setattr(track, key, kwargs[key])

        track.__metadata_load_hook = self.loadMetadata

        return track

    def loadMetadata(self, track):

        meta_data = self.db.getMetainformation(track.title, track.artist, track.album)

        for key in TagSupport.TAGLIB_INTERNAL_NAMES.values():
            setattr(track, key, None)

        for key in meta_data:
            setattr(track, key, meta_data[key])

        return track