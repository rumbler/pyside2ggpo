# -*- coding: utf-8 -*-
import hashlib
import logging
import logging.handlers
import os
import re
import sys
import urllib2
from collections import defaultdict
from PyQt4 import QtGui, QtCore
from ggpo.common.runtime import *
from ggpo.common.settings import Settings
from ggpo.common import copyright
from os.path import expanduser


def checkUpdate():
    versionurl = 'https://raw.github.com/poliva/pyqtggpo/master/VERSION'
    #noinspection PyBroadException
    try:
        response = urllib2.urlopen(versionurl, timeout=2)
        latestVersion = int(response.read().strip())
        return latestVersion - int(copyright.__version__)
    except:
        pass


def defaultdictinit(startdic):
    if not startdic:
        raise KeyError
    d = None
    for v in startdic.values():
        d = defaultdict(type(v))
        break
    for k, v in startdic.items():
        d[k] = v
    return d


def findGamesavesDir():
    try:
        d = os.path.join(os.path.dirname(findFba()),"savestates")
        if d and os.path.isdir(d):
            return d
    except:
        pass
    # noinspection PyBroadException
    try:
        os.makedirs(d)
        return d
    except:
        pass


def findURLs(url):
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)


def findFba():
    #saved = Settings.value(Settings.GGPOFBA_LOCATION)
    #if saved and os.path.isfile(saved):
    #    return saved

    FBA="ggpofba-ng.exe"

    # try to guess install directory:
    dirtest = os.path.abspath(os.path.dirname(sys.argv[0]))
    if not os.path.isfile(os.path.join(dirtest,FBA)):
        dirtest = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isfile(os.path.join(dirtest,FBA)):
        dirtest = os.getcwd()
    if not os.path.isfile(os.path.join(dirtest,FBA)):
        return None

    FBA=os.path.join(dirtest,FBA)
    return FBA


_loggerInitialzed = False


def logdebug():
    global _loggerInitialzed
    if not _loggerInitialzed:
        _loggerInitialzed = True
        loggerInit()
    return logging.getLogger('GGPODebug')


def loguser():
    global _loggerInitialzed
    if not _loggerInitialzed:
        _loggerInitialzed = True
        loggerInit()
    return logging.getLogger('GGPOUser')


def loggerInit():
    debuglog = logging.getLogger('GGPODebug')
    debuglog.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(expanduser("~"), 'fightcade-debug.log'), mode='a', maxBytes=500000, backupCount=10)
    if Settings.value(Settings.DEBUG_LOG):
        fh.setLevel(logging.INFO)
    else:
        fh.setLevel(logging.ERROR)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    debuglog.addHandler(fh)
    debuglog.addHandler(ch)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        debuglog.error("<Uncaught exception>", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = handle_exception

    if __name__ == "__main__":
        raise RuntimeError("Test unhandled")

    userlog = logging.getLogger('GGPOUser')
    userlog.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(expanduser("~"), 'fightcade.log'), mode='a', maxBytes=500000, backupCount=10)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s', "%Y-%m-%d %H:%M")
    fh.setFormatter(formatter)
    userlog.addHandler(fh)


def openURL(url):
    # noinspection PyCallByClass
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


def packagePathJoin(*args):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, *args))


def replaceURLs(text):
    return re.sub(r'(https?:\/\/\S+)',
                  r'<a href="\1"><font color=green>\1</font></a>', text)

def replaceReplayID(text):
    return re.sub(r'(challenge\-[0-9]{4}\-[0-9]{10,11}[.][0-9]{2}(\@[a-z0-9_]+)?)',r'<a href="replay:\1"><font color=green>\1</font></a>',text)

def nl2br(s):
    return '<br/>\n'.join(s.split('\n'))

def sha256digest(fname):
    return hashlib.sha256(open(fname, 'rb').read()).hexdigest()
