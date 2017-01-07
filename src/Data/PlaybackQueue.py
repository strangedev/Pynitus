import threading
from typing import NewType, List

from src.Data.Track.Track import Track

PlaybackQueueType = NewType('PlaybackQueue', object)


class PlaybackQueue(object):

    def __init__(self, on_finished_callback=None, on_stopped_callback=None):
        self.onFinishedCallback = on_finished_callback
        self.onStoppedCallback = on_stopped_callback
        self.queue = []
        self.played = []
        self.playing = False
        self.current_track = None
        self.playback_semaphore = threading.BoundedSemaphore(1)

    def startPlaying(self):
        print("Start! I am playing: ", self.playing)
        self.playNext()

    def stopPlaying(self, add_to_queue: bool=False) -> None:
        print("Stopping! I am playing: ", self.playing)
        if self.playing:
            try:
                if self.current_track.playbackHandlerInstance:
                    self.current_track.stop()
                self.playback_semaphore.acquire()
                self.playing = False
                self.playback_semaphore.release()
            except Exception as e:
                print(e)

            if add_to_queue:
                self.playback_semaphore.acquire()
                self.queue.insert(0, self.current_track)
                self.playback_semaphore.release()

    def playNext(self) -> None:
        print("Next! I am playing: ", self.playing)
        if self.playing and self.current_track:
            self.stopPlaying()

        self.playback_semaphore.acquire()
        if len(self.queue) == 0:
            self.playback_semaphore.release()
            return
        self.played.append(self.current_track)
        self.current_track = self.queue.pop(0)
        self.current_track.play(self)
        self.playing = True
        self.playback_semaphore.release()

    def playPrevious(self) -> None:
        if self.playing:
            self.stopPlaying()

        self.playback_semaphore.acquire()
        self.queue.insert(0, self.current_track)
        self.current_track = self.played.pop(-1)
        self.current_track.play(self)
        self.playing = True
        self.playback_semaphore.release()

    def addToQueue(self, track: Track) -> None:
        self.playback_semaphore.acquire()
        self.queue.append(track)
        self.playback_semaphore.release()

    def getQueued(self) -> List[Track]:
        return self.queue

    def getQueueLength(self) -> int:
        return len(self.queue)

    def removeFromQueueByIndex(self, i) -> None:
        self.playback_semaphore.acquire()
        del self.queue[i]
        self.playback_semaphore.release()

    def removeFromQueueByTrack(self, track: Track) -> None:
        self.playback_semaphore.acquire()
        self.queue.remove(track)
        self.playback_semaphore.release()

    def onFinished(self) -> None:
        if self.onFinishedCallback:
            self.onFinishedCallback()

        if self.playing:
            self.playNext()

    def onStopped(self) -> None:
        if self.onStoppedCallback:
            self.onStoppedCallback()