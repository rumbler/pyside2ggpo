# -*- coding: utf-8 -*-
import abc
import os
import sys
from subprocess import Popen

from ggpo.common.util import findFba
from ggpo.common.runtime import *
from ggpo.common.settings import Settings


class Backend(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @staticmethod
    def wavfile():
        filename = Settings.value(Settings.CUSTOM_CHALLENGE_SOUND_LOCATION)
        if filename and os.path.isfile(filename):
            return filename
        fba = findFba()
        if fba:
            filename = os.path.join(os.path.dirname(fba), "assets", "sf2-challenge.wav")
            if os.path.isfile(filename):
                return filename
        filename = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "assets", "sf2-challenge.wav")
        if filename and os.path.isfile(filename):
            return filename

    @staticmethod
    def notifyfile():
        fba = findFba()
        if fba:
            filename = os.path.join(os.path.dirname(fba), "assets", "notify.wav")
            if os.path.isfile(filename):
                return filename
        filename = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "assets", "notify.wav")
        if filename and os.path.isfile(filename):
            return filename

    @abc.abstractmethod
    def play(self):
        pass

    @abc.abstractmethod
    def notify(self):
        pass



class NullBackend(Backend):
    def play(self):
        pass
    def notify(self):
        pass


class WinSoundBackend(Backend):
    def __init__(self):
        super(WinSoundBackend, self).__init__()

    def play(self):
        if not Settings.value(Settings.MUTE_CHALLENGE_SOUND):
            filename = self.wavfile()
            if filename:
                #noinspection PyBroadException
                try:
                    # winsound can only play one clip at a time and will throw error
                    winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP)
                except:
                    pass

    def notify(self):
        if not Settings.value(Settings.MUTE_NOTIFY_SOUND):
            filename = self.notifyfile()
            if filename:
                #noinspection PyBroadException
                try:
                    # winsound can only play one clip at a time and will throw error
                    winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP)
                except:
                    pass


class ExternalPlayerBackend(Backend):
    def __init__(self, player):
        super(ExternalPlayerBackend, self).__init__()
        self.player = player

    def play(self):
        if not Settings.value(Settings.MUTE_CHALLENGE_SOUND):
            filename = self.wavfile()
            if filename:
                Popen([self.player, filename])

    def notify(self):
        if not Settings.value(Settings.MUTE_NOTIFY_SOUND):
            filename = self.notifyfile()
            if filename:
                Popen([self.player, filename])



class PhononBackend(Backend):
    def __init__(self):
        super(PhononBackend, self).__init__()
        audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        Phonon.createPath(self.mediaObject, audioOutput)

    def play(self):
        if not Settings.value(Settings.MUTE_CHALLENGE_SOUND):
            self.mediaObject.setCurrentSource(Phonon.MediaSource(':/assets/sf2-challenge.mp3'))
            self.mediaObject.seek(0)
            self.mediaObject.play()

    def notify(self):
        if not Settings.value(Settings.MUTE_NOTIFY_SOUND):
            self.mediaObject.setCurrentSource(Phonon.MediaSource(':/assets/notify.mp3'))
            self.mediaObject.seek(0)
            self.mediaObject.play()


_backend = None
if IS_WINDOWS and winsound:
    _backend = WinSoundBackend()
else:
    # afplay on osx, the others are best guesses on linux
    for cmd in ['/usr/bin/afplay', '/usr/bin/aplay', '/usr/bin/play', '/usr/bin/mplayer']:
        if os.path.isfile(cmd):
            _backend = ExternalPlayerBackend(cmd)
            break
if not _backend and Phonon:
    _backend = PhononBackend()
if not _backend:
    _backend = NullBackend()


def play():
    _backend.play()

def notify():
    _backend.notify()
