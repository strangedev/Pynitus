from typing import Dict

import cherrypy

from src.Data.Tagging import TagSupport
from src.Server import ServerUtils
from src.Server.Components.HtmlBuilder import HtmlBuilder
from src.Data.Tagging.TagSupport import TagValue


class UnimportedViews(object):

    def __init__(self, management):
        self.__management = management

    @staticmethod
    def tagInfoToTuples(tag_info: Dict[str, TagValue]):
        tuples = []

        for internal_name, value in tag_info.items():

            required = internal_name in TagSupport.REQUIRED_TAGS
            display_name = TagSupport.getDisplayNameByInternalName(internal_name)

            if TagSupport.isListType(internal_name):
                display_name += " (separated by commas)"
                if value is not None:
                    value = "".join(value)

            tuples.append((display_name, internal_name, value, required))

        return sorted(tuples)

    # TODO: session activity
    @cherrypy.expose
    def index(self):
        self.__management.session_handler.activity(ServerUtils.getClientIp())

        tracks = self.__management.database.getUnimported()

        for track in tracks:

            number_required = len(TagSupport.REQUIRED_TAGS)
            number_complete = number_required

            for internal_name in TagSupport.REQUIRED_TAGS:
                value = track.tag_info[internal_name]
                if value is None or value == []:
                    number_complete -= 1

            track.completeness = "{}/{}".format(number_complete, number_required)

        return HtmlBuilder.render(
            "unimported.html",
            ServerUtils.getClientIp(),
            tracks=tracks
        )

    @cherrypy.expose
    def edit(self, location: str=""):
        edited_track = self.__management.database.getByLocation(location)  # TODO: implement

        if edited_track is None:
            return ":("

        if ServerUtils.existsForCurrentSession(self.__management, "edited_track"):
            edited_track = ServerUtils.getForCurrentSession(self.__management, "edited_track")

        ServerUtils.setForCurrentSession(self.__management, "edited_track", edited_track)

        return HtmlBuilder.render(
            "edit.html",
            ServerUtils.getClientIp(),
            track=edited_track,
            location=edited_track.location,
            tag_info_tuples=UnimportedViews.tagInfoToTuples(edited_track.tag_info)
        )

    @cherrypy.expose
    def verify(self, location="", **tag_info: Dict[str, str]):
        edited_track = ServerUtils.getForCurrentSession(self.__management, "edited_track")
        edited_track.tag_info = tag_info

        for internal_name in TagSupport.REQUIRED_TAGS:
            value = edited_track.tag_info[internal_name]
            if value is None or value == []:
                return self.edit(location)

        ServerUtils.removeForCurrentSession(self.__management, "edited_track")
        self.__management.database.updateTrack(edited_track)
        self.__management.database.importTrack(edited_track)

        return "Success"
        #return DetailViews.track(edited_track.location)