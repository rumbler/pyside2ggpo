# -*- coding: utf-8 -*-
import pickle
import os.path
import sys
from PyQt4.QtCore import QSettings


# noinspection PyClassHasNoInit
class Settings:
    # list of saved setting for autocomplete and avoid typos
    AWAY = 'away'
    IGNORED = 'ignored'
    SELECTED_CHANNEL = 'channel'
    AUTOLOGIN = 'autoLogin'
    USERNAME = 'username'
    PASSWORD = 'password'
    PORT = 'port'
    SMOOTHING = 'smoothing'
    MUTE_CHALLENGE_SOUND = 'mute'
    MUTE_NOTIFY_SOUND = 'mutenotify'
    NOTIFY_PLAYER_STATE_CHANGE = 'notifyPlayerStateChange'
    SHOW_COUNTRY_FLAG_IN_CHAT = 'showCountryFlagInChat'
    SHOW_TIMESTAMP_IN_CHAT = 'ShowTimestampInChat'
    HIDE_INGAME_CHAT = 'HideInGameChat'
    HIDE_GAMES_WITHOUT_ROM = 'HideGamesWithoutRom'
    DISABLE_AUTOCOLOR_NICKS = 'DisableAutoColorNicks'
    WINDOW_GEOMETRY = 'mainWindowGeometry'
    WINDOW_STATE = 'mainWindowState'
    SPLITTER_STATE = 'splitterState'
    TABLE_HEADER_STATE = 'tableHeaderState'
    CHANNELS_HEADER_STATE = 'channelsTreeState'
    EMOTICON_DIALOG_GEOMETRY = 'emoticonDialogGeometry'
    SAVESTATES_DIALOG_GEOMETRY = 'savestatesDialogGeometry'
    SAVESTATES_DIALOG_TABLE_HEADER_STATE = 'savestatesDialogTableHeaderState'
    COLORTHEME = 'colortheme'
    CUSTOM_THEME_FILENAME = 'customThemeFilename'
    CUSTOM_EMOTICONS = 'customEmoticons'
    CHAT_HISTORY_FONT = 'chatFont'
    DEBUG_LOG = 'debuglog'
    COMPOSITION_DISABLED = 'compositionDisabled'
    USER_LOG_CHAT = 'userlogchat'
    USER_LOG_PLAYHISTORY = 'userlogplayhistory'
    SAVE_USERNAME_PASSWORD = 'saveUsernameAndPassword'
    #GGPOFBA_LOCATION = 'ggpofbaLocation'
    ROMS_DIR = 'romsLocation'
    GEOIP2DB_LOCATION = 'geoip2dbLocation'
    CUSTOM_CHALLENGE_SOUND_LOCATION = 'customChallengeSoundLocation'
    UNSUPPORTED_GAMESAVES_DIR = 'unsupportedGamesavesDir'
    DISABLE_AUTO_ANNOUNCE_UNSUPPORTED = 'disableAutoAnnounceUnsupported'
    CHANNELS_FAVORITES = 'channelsFavorites'
    FILTER_FAVORITES = 'filterFavorites'

    _settings = QSettings(os.path.join(os.path.abspath(os.path.expanduser("~")), 'ggpo-ng.ini'), QSettings.IniFormat)

    @staticmethod
    def setBoolean(key, val):
        if val:
            val = '1'
        else:
            val = ''
        Settings._settings.setValue(key, val)

    @staticmethod
    def setPythonValue(key, val):
        try:
            Settings._settings.setValue(key, pickle.dumps(val))
        except pickle.PickleError:
            pass

    @staticmethod
    def pythonValue(key):
        # noinspection PyBroadException
        try:
            return pickle.loads(Settings._settings.value(key))
        except:
            return None

    @staticmethod
    def setValue(key, val):
        Settings._settings.setValue(key, val)

    @staticmethod
    def value(key):
        return Settings._settings.value(key)
