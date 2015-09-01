# -*- coding: utf-8 -*-
import cgi
import logging
import logging.handlers
import os
import sys
import re
import shutil
import time
from colortheme import ColorTheme
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import ggpo.common.sound
from ggpo.common.geolookup import geolookupInit
from ggpo.common.runtime import *
from ggpo.common import copyright
from ggpo.common.cliclient import CLI
from ggpo.common.playerstate import PlayerStates
from ggpo.common.settings import Settings
from ggpo.common.util import logdebug, openURL, findURLs, nl2br, replaceURLs, replaceReplayID, findGamesavesDir, \
    defaultdictinit, findFba
from ggpo.common.unsupportedsavestates import UnsupportedSavestates
from ggpo.common.allgames import *
from ggpo.gui.customemoticonsdialog import CustomEmoticonsDialog
from ggpo.gui.emoticonsdialog import EmoticonDialog
from ggpo.gui.playermodel import PlayerModel
from ggpo.gui.savestatesdialog import SavestatesDialog
from ggpo.gui.ui.ggpowindow_ui import Ui_MainWindow

# re-implement the QTreeWidgetItem
class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            return float(key1) < float(key2)
        except ValueError:
            return key1 < key2

class GGPOWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, QWidget_parent=None):
        super(GGPOWindow, self).__init__(QWidget_parent)
        self.setupUi(self)
        self.controller = None
        self.channels = {}
        self.expectFirstChannelResponse = True
        self.lastSplitterExpandedSizes = []
        self.lastStateChangeMsg = ''
        self.uiChatInputEdit.returnPressed.connect(self.returnPressed)
        self.setupMenu()
        self.uiEmoticonTbtn.setDefaultAction(self.uiEmoticonAct)
        self.uiEmoticonTbtn.setText(':)')
        self.addSplitterHandleToggleButton()
        self.uiChatHistoryTxtB.anchorClicked.connect(self.onAnchorClicked)
        self.autoAnnounceUnsupportedTime = 0
        self.refreshChannelsListTime = time.time()
        self.refreshListUsersTime = time.time()
        self.savestatesChecked = False
        if Settings.value(Settings.CHANNELS_FAVORITES) != None: # default value if it's not present in config file
            self.favorites = Settings.value(Settings.CHANNELS_FAVORITES)
        else:
            self.favorites = ''

        self.showfavorites=False
        if Settings.value(Settings.FILTER_FAVORITES):
            self.showfavorites = True
        self.hidemissing = False
        if Settings.value(Settings.HIDE_GAMES_WITHOUT_ROM):
            self.hidemissing = True
        self.uiChannelsTree.itemDoubleClicked.connect(self.AddRemoveFavorites) # call to double click handler

    def aboutDialog(self):
        QtGui.QMessageBox.information(self, 'About', copyright.about())

    def addSplitterHandleToggleButton(self):
        self.uiSplitter.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
        handle = self.uiSplitter.handle(1)
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        button = QtGui.QToolButton(handle)
        button.setArrowType(QtCore.Qt.LeftArrow)
        button.clicked.connect(self.onToggleSidebarAction)
        layout.addWidget(button)
        button = QtGui.QToolButton(handle)
        button.setArrowType(QtCore.Qt.RightArrow)
        button.clicked.connect(self.onToggleSidebarAction)
        layout.addWidget(button)
        handle.setLayout(layout)

    def appendChat(self, text):
        if Settings.value(Settings.SHOW_TIMESTAMP_IN_CHAT):
            text = time.strftime("%H:%M ") + text
        self.uiChatHistoryTxtB.append(text)

    @staticmethod
    def buildInSmoothingToActionName(smooth):
        return 'uiSmoothing{}Act'.format(smooth)

    @staticmethod
    def buildInStyleToActionName(styleName):
        return 'ui{}ThemeAct'.format(re.sub(r'[^a-zA-Z0-9]', '', styleName))

    def changeFont(self):
        font, ok = QtGui.QFontDialog.getFont()
        if ok:
            Settings.setPythonValue(Settings.CHAT_HISTORY_FONT,
                                    [font.family(), font.pointSize(), font.weight(), font.italic()])
            self.uiChatHistoryTxtB.setFont(font)

    def closeEvent(self, evnt):
        Settings.setValue(Settings.WINDOW_GEOMETRY, self.saveGeometry())
        Settings.setValue(Settings.WINDOW_STATE, self.saveState())
        Settings.setValue(Settings.SPLITTER_STATE, self.uiSplitter.saveState())
        Settings.setValue(Settings.TABLE_HEADER_STATE, self.uiPlayersTableV.horizontalHeader().saveState())
        Settings.setValue(Settings.CHANNELS_HEADER_STATE, self.uiChannelsTree.header().saveState())
        super(GGPOWindow, self).closeEvent(evnt)

    @staticmethod
    def logdebugTriggered(value):
        if value:
            level = logging.INFO
        else:
            level = logging.ERROR
        Settings.setBoolean(Settings.DEBUG_LOG, value)
        for handler in logdebug().handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.setLevel(level)
                break

    def CompositionEnableAct(self):
                self.controller.sigStatusMessage.emit("Enabled Desktop Composition")
                Settings.setBoolean(Settings.COMPOSITION_DISABLED, False)
                self.uiCompositionDisableAct.setChecked(False)
                self.uiCompositionEnableAct.setChecked(True)
                self.controller.desktopComposition(1)

    def CompositionDisableAct(self):
                self.controller.sigStatusMessage.emit("Disabled Desktop Composition")
                Settings.setBoolean(Settings.COMPOSITION_DISABLED, True)
                self.uiCompositionDisableAct.setChecked(True)
                self.uiCompositionEnableAct.setChecked(False)
                self.controller.desktopComposition(0)

    @staticmethod
    def loguserChatTriggered(value):
        Settings.setBoolean(Settings.USER_LOG_CHAT, value)

    @staticmethod
    def loguserPlayHistoryTriggered(value):
        Settings.setBoolean(Settings.USER_LOG_PLAYHISTORY, value)

    def ignoreAdded(self, name):
        self.appendChat(ColorTheme.statusHtml("* Adding " + name + " to ignore list."))

    def ignoreRemoved(self, name):
        self.appendChat(ColorTheme.statusHtml("* Removing " + name + " from ignore list."))

    def insertEmoticon(self):
        dlg = EmoticonDialog(self)
        if dlg.exec_():
            self.uiChatInputEdit.insert(dlg.value())
            self.uiChatInputEdit.setFocus()
            dlg.destroy()

    def joinChannel(self, *args):
        try:
            it = self.uiChannelsTree.currentItem().text(1)
        except AttributeError:
            it = ''
        if it and len(it) > 0:
            if not self.expectFirstChannelResponse:
                self.uiStatusbar.showMessage("Joining room, please wait...");
                self.uiChatHistoryTxtB.clear()
                self.controller.sendJoinChannelRequest(self.channels[it])
                self.uiChatInputEdit.setFocus()

    def locateCustomChallengeSound(self):
        oldval = Settings.value(Settings.CUSTOM_CHALLENGE_SOUND_LOCATION)
        if oldval and os.path.isdir(os.path.dirname(oldval)):
            dirname = os.path.dirname(oldval)
        else:
            dirname = os.path.expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate custom wave file', dirname,
                                                  "wav file (*.wav)")
        if fname:
            Settings.setValue(Settings.CUSTOM_CHALLENGE_SOUND_LOCATION, fname)
            ggpo.common.sound.play()
            for a in self.uiMenuChallengeSoundGroup.actions():
                if a.isChecked():
                    a.setChecked(False)

    def locateGGPOFBA(self):
        oldval = Settings.value(Settings.GGPOFBA_LOCATION)
        if oldval and os.path.isdir(os.path.dirname(oldval)):
            dirname = os.path.dirname(oldval)
        else:
            dirname = os.path.expanduser("~")

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate ggpofba-ng.exe', dirname,
                                                  "ggpofba-ng.exe (ggpofba-ng.exe)")
        if fname:
            Settings.setValue(Settings.GGPOFBA_LOCATION, fname)
            self.controller.checkInstallation()

    def locateGeoMMDB(self):
        oldval = Settings.value(Settings.GEOIP2DB_LOCATION)
        if oldval and os.path.isdir(os.path.dirname(oldval)):
            dirname = os.path.dirname(oldval)
        else:
            dirname = os.path.expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate Geo mmdb file', dirname,
                                                  "Geo mmdb (*.mmdb)")
        if fname:
            Settings.setValue(Settings.GEOIP2DB_LOCATION, fname)
            geolookupInit()

    def locateUnsupportedSavestatesDirAct(self):
        d = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory",
                                                   os.path.expanduser("~"),
                                                   QtGui.QFileDialog.ShowDirsOnly
                                                   | QtGui.QFileDialog.DontResolveSymlinks)
        if d and os.path.isdir(d):
            Settings.setValue(Settings.UNSUPPORTED_GAMESAVES_DIR, d)

    def locateROMsDir(self):
        d = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory",
                                                   os.path.expanduser("~"),
                                                   QtGui.QFileDialog.ShowDirsOnly
                                                   | QtGui.QFileDialog.DontResolveSymlinks)
        if d and os.path.isdir(d):
            Settings.setValue(Settings.ROMS_DIR, d)

        # create FBA ini file and setup ROMs dir
        self.controller.createFbaIni()
        self.controller.setupROMsDir()

        # refresh the channels list
        self.expectFirstChannelResponse = True
        self.controller.sigChannelsLoaded.emit()

    def notifyStateChange(self, name, msg):
        msg = name + msg
        if self.lastStateChangeMsg != msg:
            self.lastStateChangeMsg = msg
            flag = self.controller.getPlayerFlag(name) or ''
            self.appendChat(flag + ColorTheme.statusHtml(msg))

    def onActionFailed(self, txt):
        self.appendChat(ColorTheme.statusHtml(txt))

    def onAnchorClicked(self, qurl):
        if qurl.scheme() in ['http', 'https']:
            QtGui.QDesktopServices.openUrl(qurl)
        name = qurl.path()
        if name:
            if qurl.scheme() == 'accept':
                if name in self.controller.challengers:
                    self.controller.sendAcceptChallenge(name)
            elif qurl.scheme() == 'decline':
                if name in self.controller.challengers:
                    self.controller.sendDeclineChallenge(name)
                    self.controller.sigStatusMessage.emit("Declined {}'s challenge".format(name))
                    self.updateStatusBar()
            elif qurl.scheme() == 'replay':
                if '@' in name:
                    channel = name.split('@')[1]
                    replay_id = name.split('@')[0]
                else:
                    channel = self.controller.channel
                    replay_id = name
                quark = "quark:stream,"+channel+","+replay_id+",7001"
                self.controller.runFBA(quark)
                self.controller.sigStatusMessage.emit("Replaying game-id {}@{}".format(replay_id, channel))

    def onRemoteHasUpdates(self, added, updated, nochange):
        totalchanged = added + updated
        if totalchanged:
            self.appendChat(ColorTheme.statusHtml(
                "Syncronizing {} savestate(s). Please wait...".format(
                    totalchanged)))
            UnsupportedSavestates.sync(self.onStatusMessage)

    def onChallengeCancelled(self, name):
        self.appendChat(ColorTheme.statusHtml(name + " cancelled challenge"))
        self.updateStatusBar()

    def onChallengeDeclined(self, name):
        self.appendChat(ColorTheme.statusHtml(name + " declined your challenge"))
        self.updateStatusBar()

    def onChallengeReceived(self, name):
        self.appendChat(self.controller.getPlayerChallengerText(name))
        ggpo.common.sound.play()
        self.updateStatusBar()

    def onChatReceived(self, name, txt):
        if name=="System" and "GAME: " in txt and Settings.value(Settings.HIDE_INGAME_CHAT):
            return
        if name=="System" and "GAME: " in txt and not Settings.value(Settings.HIDE_INGAME_CHAT):
            txt = re.sub(r'<System> ', r'', txt)
        prefix = self.controller.getPlayerPrefix(name, Settings.value(Settings.SHOW_COUNTRY_FLAG_IN_CHAT))
        if (self.controller.username+" ".lower() in txt.lower() or " "+self.controller.username.lower() in txt.lower() or txt.lower()==self.controller.username.lower()):
            txt = cgi.escape(txt.strip()).replace(self.controller.username, "<b>{}</b>".format(self.controller.username))
            ggpo.common.sound.notify()
        else:
            txt = cgi.escape(txt.strip())
        urls = findURLs(txt)
        chat = prefix + txt
        if urls:
            chat = prefix + replaceURLs(txt)
        self.appendChat(replaceReplayID(chat))

    def onChannelJoined(self):
        self.updateStatusBar()
        if not self.savestatesChecked:
            UnsupportedSavestates.sync(self.onStatusMessage)
            self.savestatesChecked=True

    def onListChannelsReceived(self):

        if not self.expectFirstChannelResponse:
            root = self.uiChannelsTree.invisibleRootItem()
            child_count = root.childCount()
            for i in range(child_count):
                item = root.child(i)
                n = item.text(1)
                chan = self.channels[n]
                item.setText(0, str(self.controller.channels[chan]['users']))
        else:
            self.uiChannelsTree.clear()
            try:
                self.uiChannelsTree.itemSelectionChanged.disconnect(self.joinChannel)
            except:
                pass
            self.expectFirstChannelResponse = False

            self.channels = dict((c['title'], c['room']) for c in self.controller.channels.values())
            sortedRooms = sorted(self.channels.keys())

            lastChannel = Settings.value(Settings.SELECTED_CHANNEL)
            if lastChannel == None:
                lastChannel='lobby'
            n=0
            idx=0
            l=[]
            for i in sortedRooms:
                item = TreeWidgetItem()
                chan = self.channels[i]
                item.setText(0, str(self.controller.channels[chan]['users']))
                item.setText(1, i)
                if not self.controller.isRomAvailable(chan) and chan!='lobby':
                    item.setTextColor(0, QtGui.QColor(60, 60, 60))
                    item.setTextColor(1, QtGui.QColor(60, 60, 60))
                if "," + self.channels[i] + "," in self.favorites:
                    bold_font = QtGui.QFont()
                    bold_font.setBold(True)
                    item.setFont(1, bold_font)
                if chan==lastChannel:
                    idx=n

                if self.hidemissing==True and self.showfavorites==False:
                    if self.controller.isRomAvailable(chan) or chan==self.controller.channel:
                        l.append(item)
                        n+=1
                elif self.hidemissing==False and self.showfavorites==True:
                    if "," + self.channels[i] + "," in self.favorites:
                        l.append(item)
                        n+=1
                elif self.hidemissing==False and self.showfavorites==False:
                    l.append(item)
                    n+=1
                elif self.hidemissing==True and self.showfavorites==True:
                    if (self.controller.isRomAvailable(chan) or chan==self.controller.channel) and "," + self.channels[i] + "," in self.favorites:
                        l.append(item)
                        n+=1

            self.uiChannelsTree.addTopLevelItems(l)
            root = self.uiChannelsTree.invisibleRootItem()

            # QTreeWidget column sorting #
            self.uiChannelsTree.setSortingEnabled(True)
            self.uiChannelsTree.sortByColumn(1, Qt.AscendingOrder)
            # end column sorting #

            if lastChannel in self.controller.channels:
                self.uiChannelsTree.setItemSelected(root.child(0), False)
                self.uiChannelsTree.setItemSelected(root.child(idx), True)
                self.uiChannelsTree.scrollToItem(root.child(idx)) # scroll lobby list to last channel
                if self.controller.channel != lastChannel:
                    self.controller.sendJoinChannelRequest(lastChannel)
                elif self.controller.channel == 'lobby':
                    self.controller.sendJoinChannelRequest("lobby")
            else:
                self.controller.sendJoinChannelRequest("lobby")
                self.uiChannelsTree.setItemSelected(root.child(0), True)

            self.uiChannelsTree.itemSelectionChanged.connect(self.joinChannel)

    def AddRemoveFavorites(self):
        it = self.uiChannelsTree.currentItem().text(1)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        not_bold_font = QtGui.QFont()
        not_bold_font.setBold(False)

        if not("," + self.channels[it] + "," in self.favorites): # Add favorite
            self.favorites = self.favorites + "," + self.channels[it] + ","
            self.uiChannelsTree.currentItem().setFont(1, bold_font)
        else: # Remove favorite
            self.favorites = self.favorites.replace("," + self.channels[it] + ",",",")
            self.uiChannelsTree.currentItem().setFont(1, not_bold_font)
            if (not self.expectFirstChannelResponse) and Settings.value(Settings.FILTER_FAVORITES): # Update list when removing from the filtered list
                self.expectFirstChannelResponse=True
                self.controller.sigChannelsLoaded.emit()
            self.uiChannelsTree.setCurrentItem(None)

        pattern1 = re.compile(",*,") # trimming unwanted commas
        self.favorites = pattern1.sub(",", self.favorites)
        if self.favorites == ",": # if it's only a comma after RegEx, then clear the favorites
            self.favorites = ""
        Settings.setValue(Settings.CHANNELS_FAVORITES, self.favorites)

    def onMOTDReceived(self, channel, topic, msg):
        self.uiChatHistoryTxtB.setHtml('<font color="#034456"><strong>'+channel+'</strong> || <strong>'+ topic +'</strong></font><br/><br/>' + nl2br(replaceURLs(msg)) + '<br/><br/>Type /help to see a list of commands<br/><br/>')
        self.controller.checkInstallation()

    def onPlayerNewlyJoined(self, name):
        if self.controller.channel == 'unsupported' and self.controller.unsupportedRom and \
                not Settings.value(Settings.DISABLE_AUTO_ANNOUNCE_UNSUPPORTED) and \
                                time.time() - self.autoAnnounceUnsupportedTime > 3 and \
                        self.controller.username in self.controller.playing:
            basename = os.path.splitext(self.controller.unsupportedRom)[0]
            desc = ''
            if basename in allgames:
                desc = allgames[basename][FBA_GAMEDB_DESCRIPTION]
            QtCore.QTimer.singleShot(1000, lambda: self.controller.sendChat("* I'm playing {}".format(desc)))
            self.autoAnnounceUnsupportedTime = time.time()

    def onPlayerStateChange(self, name, state):
        if Settings.value(Settings.NOTIFY_PLAYER_STATE_CHANGE):
            if state == PlayerStates.QUIT:
                self.notifyStateChange(name, " left")
            elif state == PlayerStates.AVAILABLE:
                self.notifyStateChange(name, " becomes available")
            elif state == PlayerStates.PLAYING:
                self.notifyStateChange(name, " is in a game")
            elif state == PlayerStates.AFK:
                self.notifyStateChange(name, " is away")
        self.updateStatusBar()

        # refresh the channel list
        sizes = self.uiSplitter.sizes()
        if time.time() - self.refreshChannelsListTime > 300 and sizes[0] > 0:
            self.refreshChannelsListTime = time.time()
            self.controller.sendListChannels()

        if time.time() - self.refreshListUsersTime > 120:
            self.refreshListUsersTime = time.time()
            self.controller.sendListUsers()

    def onStatusMessage(self, msg):
        self.appendChat(ColorTheme.statusHtml(msg))

    def onToggleSidebarAction(self):
        sizes = self.uiSplitter.sizes()
        if sizes[0]:
            self.lastSplitterExpandedSizes = sizes[:]
            sizes[1] += sizes[0]
            sizes[0] = 0
        else:
            if len(self.lastSplitterExpandedSizes) > 0:
                sizes = self.lastSplitterExpandedSizes
            elif sizes[1]:
                sizes[0] = sizes[1] / 2
                sizes[1] /= 2
        self.uiSplitter.setSizes(sizes)

    def onSplitterHotkeyResizeAction(self, part, growth):
        def resizeCallback():
            increment = 5
            splitterPart, chatHistoryPart, playerViewPart = range(3)
            sizes = self.uiSplitter.sizes()
            if (growth > 0 and sizes[chatHistoryPart] < increment) or \
                    (growth < 0 and sizes[part] == 0):
                return
            total = sizes[part] + sizes[chatHistoryPart]
            if growth < 0:
                increment = min(sizes[part], increment)
                sizes[part] -= increment
                sizes[chatHistoryPart] += increment
            else:
                increment = min(sizes[chatHistoryPart], increment)
                sizes[part] += increment
                sizes[chatHistoryPart] -= increment
            self.uiSplitter.setSizes(sizes)

        return resizeCallback

    def restorePreference(self):
        theme = Settings.value(Settings.COLORTHEME)
        if theme:
            if theme == 'darkorange':
                self.uiDarkThemeAct.setChecked(True)
            elif theme == 'fightcade':
                self.uiGNGThemeAct.setChecked(True)
            elif theme == 'custom':
                fname = Settings.value(Settings.CUSTOM_THEME_FILENAME)
                self.setCustomQssfile(fname)
            else:
                cleanname = self.buildInStyleToActionName(theme)
                if hasattr(self, cleanname):
                    getattr(self, cleanname).setChecked(True)
        smooth = Settings.value(Settings.SMOOTHING)
        if smooth:
            cleanname = self.buildInSmoothingToActionName(smooth)
            if hasattr(self, cleanname):
                getattr(self, cleanname).setChecked(True)
        if Settings.value(Settings.MUTE_CHALLENGE_SOUND):
            self.uiMuteChallengeSoundAct.setChecked(True)
        if Settings.value(Settings.MUTE_NOTIFY_SOUND):
            self.uiMuteNotifySoundAct.setChecked(True)
        if Settings.value(Settings.NOTIFY_PLAYER_STATE_CHANGE):
            self.uiNotifyPlayerStateChangeAct.setChecked(True)
        if Settings.value(Settings.SHOW_COUNTRY_FLAG_IN_CHAT):
            self.uiShowCountryFlagInChatAct.setChecked(True)
        if Settings.value(Settings.SHOW_TIMESTAMP_IN_CHAT):
            self.uiShowTimestampInChatAct.setChecked(True)
        if Settings.value(Settings.HIDE_INGAME_CHAT):
            self.uiHideInGameChatAct.setChecked(True)
        if Settings.value(Settings.HIDE_GAMES_WITHOUT_ROM):
            self.hidemissing=True
            self.uiHideGamesWithoutRomAct.setChecked(True)
        if Settings.value(Settings.FILTER_FAVORITES):
            self.showfavorites=True
            self.uiFilterFavoriteLobbies.setChecked(True)
        if Settings.value(Settings.DISABLE_AUTOCOLOR_NICKS):
            self.uiDisableAutoColorNicks.setChecked(True)
        if Settings.value(Settings.AWAY):
            self.uiAwayAct.setChecked(True)
            self.uiAfkChk.setChecked(True)
            self.controller.sendToggleAFK(1)
        fontsetting = Settings.pythonValue(Settings.CHAT_HISTORY_FONT)
        if fontsetting:
            self.uiChatHistoryTxtB.setFont(QtGui.QFont(*fontsetting))
        self.restoreStateAndGeometry()

    def restoreStateAndGeometry(self):
        saved = Settings.value(Settings.WINDOW_GEOMETRY)
        if saved:
            self.restoreGeometry(saved)
        saved = Settings.value(Settings.WINDOW_STATE)
        if saved:
            self.restoreState(saved)
        saved = Settings.value(Settings.SPLITTER_STATE)
        if saved:
            self.uiSplitter.restoreState(saved)
        saved = Settings.value(Settings.TABLE_HEADER_STATE)
        if saved:
            self.uiPlayersTableV.horizontalHeader().restoreState(saved)
        saved = Settings.value(Settings.CHANNELS_HEADER_STATE)
        if saved:
            self.uiChannelsTree.header().restoreState(saved)
        else:
            self.uiChannelsTree.setColumnWidth(0,50)
            self.uiChannelsTree.setColumnWidth(1,300)

    def returnPressed(self):
        line = self.uiChatInputEdit.text().strip()
        if line:
            self.uiChatInputEdit.clear()
            if line[0] == '/':
                if line.startswith('/incoming'):
                    for name in self.controller.challengers:
                        self.appendChat(self.controller.getPlayerChallengerText(name))
                else:
                    CLI.process(self.controller, self.uiAwayAct.setChecked, line)
            else:
                self.controller.sendChat(line)

    def selectUnsupportedSavestate(self):
        if not self.controller.fba:
            self.onStatusMessage('ggpofba is not set, cannot locate unsupported_ggpo.fs')
            return
        d = findGamesavesDir()
        if not d or not os.path.isdir(d):
            self.onStatusMessage('Unsupported Savestates Directory is not set')
            return
        savestatesDialog = SavestatesDialog()
        if savestatesDialog.exec_():
            fname = savestatesDialog.fsfile
            dst = os.path.join(os.path.dirname(self.controller.fba), 'savestates', 'unsupported_ggpo.fs')
            shutil.copy(fname, dst)
            basefile = os.path.basename(fname)
            basename = os.path.splitext(basefile)[0]
            self.onStatusMessage('Saved {} as unsupported_ggpo.fs'.format(basefile))
            if self.controller.channel == 'unsupported':
                self.controller.setUnsupportedRom('')
                desc = ''
                if basename in allgames:
                    desc = ' {}'.format(allgames[basename][FBA_GAMEDB_DESCRIPTION])
                self.controller.sendChat("* {} switches to [{}]{}".format(self.controller.username, basename, desc))
            self.controller.setUnsupportedRom(basename)

    def setController(self, controller):
        self.controller = controller
        self.setupUserTable()
        self.uiChatInputEdit.setController(controller)
        controller.sigChannelJoined.connect(self.onChannelJoined)
        controller.sigPlayersLoaded.connect(self.updateStatusBar)
        controller.sigChannelsLoaded.connect(self.onListChannelsReceived)
        controller.sigMotdReceived.connect(self.onMOTDReceived)
        controller.sigActionFailed.connect(self.onActionFailed)
        controller.sigPlayerNewlyJoined.connect(self.onPlayerNewlyJoined)
        controller.sigPlayerStateChange.connect(self.onPlayerStateChange)
        controller.sigChatReceived.connect(self.onChatReceived)
        controller.sigChallengeDeclined.connect(self.onChallengeDeclined)
        controller.sigChallengeReceived.connect(self.onChallengeReceived)
        controller.sigChallengeCancelled.connect(self.onChallengeCancelled)
        controller.sigIgnoreAdded.connect(self.ignoreAdded)
        controller.sigIgnoreRemoved.connect(self.ignoreRemoved)
        controller.sigStatusMessage.connect(self.onStatusMessage)
        controller.sigServerDisconnected.connect(
            lambda: self.onStatusMessage("Disconnected from server. Please restart application"))

    def setCustomEmoticons(self):
        dlg = CustomEmoticonsDialog(self)
        if dlg.exec_():
            dlg.destroy()

    def setCustomQss(self):
        oldval = Settings.value(Settings.CUSTOM_THEME_FILENAME)
        if oldval and os.path.isdir(os.path.dirname(oldval)):
            dirname = os.path.dirname(oldval)
        else:
            dirname = os.path.expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate Qt Stylesheet qss file', dirname,
                                                  "qss file (*.qss)")
        if self.setCustomQssfile(fname):
            for a in self.uiMenuThemeGroup.actions():
                if a.isChecked():
                    a.setChecked(False)

    def setCustomQssfile(self, fname):
        if fname and os.path.isfile(fname):
            # noinspection PyBroadException
            try:
                QtGui.QApplication.instance().setStyleSheet(open(fname).read())
                Settings.setValue(Settings.COLORTHEME, 'custom')
                Settings.setValue(Settings.CUSTOM_THEME_FILENAME, fname)
                ColorTheme.SELECTED = ColorTheme.SAFE
                return True
            except:
                pass

    def setStyleBuiltin(self, styleName):
        if styleName in QtGui.QStyleFactory.keys():
            ColorTheme.SELECTED = ColorTheme.LIGHT
            QtGui.QApplication.instance().setStyleSheet('')
            QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(styleName))
            QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())
            Settings.setValue(Settings.COLORTHEME, styleName)

    def setStyleCallback(self, styleName):
        def setStyle(boolean):
            if boolean:
                self.setStyleBuiltin(styleName)

        return setStyle


    def setupMenu(self):
        self.setupMenuAction()
        self.setupMenuSettings()
        self.setupMenuHelp()

    def setupMenuAction(self):
        self.uiAwayAct.triggered.connect(self.toggleAFK)
        self.uiEmoticonAct.triggered.connect(self.insertEmoticon)
        self.uiToggleSidebarAction.triggered.connect(self.onToggleSidebarAction)
        channelPart, chatHistoryPart, playerViewPart = range(3)
        self.uiContractChannelSidebarAct.triggered.connect(self.onSplitterHotkeyResizeAction(channelPart, -1))
        self.uiExpandChannelSidebarAct.triggered.connect(self.onSplitterHotkeyResizeAction(channelPart, +1))
        self.uiContractPlayerListAct.triggered.connect(self.onSplitterHotkeyResizeAction(playerViewPart, -1))
        self.uiExpandPlayerListAct.triggered.connect(self.onSplitterHotkeyResizeAction(playerViewPart, +1))
        #self.uiSelectUnsupportedSavestateAct.triggered.connect(self.selectUnsupportedSavestate)
        #self.uiSyncUnsupportedSavestatesAct.triggered.connect(lambda: UnsupportedSavestates.sync(self.onStatusMessage))

    def setupMenuHelp(self):
        #self.uiSRKForumAct.triggered.connect(
        #    lambda: openURL('http://forums.shoryuken.com/categories/super-street-fighter-ii-turbo'))
        #self.uiSRKWikiAct.triggered.connect(lambda: openURL('http://wiki.shoryuken.com/Super_Street_Fighter_2_Turbo'))
        #self.uiJPWikiAct.triggered.connect(lambda: openURL('http://sf2.gamedb.info/wiki/'))
        #self.uiStrevivalAct.triggered.connect(lambda: openURL('http://www.strevival.com/'))
        #self.uiHitboxViewerAct.triggered.connect(lambda: openURL('http://www.strevival.com/hitbox/'))
        #self.uiSafejumpGuideAct.triggered.connect(lambda: openURL('http://www.strevival.com/hitbox/st-safejump/'))
        #self.uiMatchVideosAct.triggered.connect(lambda: openURL('http://www.strevival.com/yt/'))
        self.uiGNGWebAct.triggered.connect(lambda: openURL('http://www.fightcade.com'))
        self.actionReport_an_issue.triggered.connect(lambda: openURL('https://github.com/poliva/pyqtggpo/issues'))
        self.uiAboutAct.triggered.connect(self.aboutDialog)

    def setupMenuSettings(self):
        self.uiMuteChallengeSoundAct.toggled.connect(self.__class__.toggleSound)
        self.uiMuteNotifySoundAct.toggled.connect(self.__class__.toggleNotifySound)
        self.uiFontAct.triggered.connect(self.changeFont)
        self.setupMenuTheme()
        self.setupMenuSmoothing()
        self.setupMenuChallengeSound()
        self.uiCustomEmoticonsAct.triggered.connect(self.setCustomEmoticons)
        if not IS_WINDOWS or IS_WINDOWS_XP:
            self.uiDesktopCompositionMenu.menuAction().setVisible(False)
        else:
            self.uiCompositionEnableAct.triggered.connect(self.CompositionEnableAct)
            self.uiCompositionDisableAct.triggered.connect(self.CompositionDisableAct)
            self.uiCompositionDisableAct.setCheckable(True)
            self.uiCompositionEnableAct.setCheckable(True)
            if Settings.value(Settings.COMPOSITION_DISABLED):
                self.uiCompositionEnableAct.setChecked(False)
                self.uiCompositionDisableAct.setChecked(True)
                #self.CompositionDisableAct()
            else:
                self.uiCompositionDisableAct.setChecked(False)
                self.uiCompositionEnableAct.setChecked(True)

        #self.uiLocateGgpofbaAct.triggered.connect(self.locateGGPOFBA)
        self.uiLocateROMsAct.triggered.connect(self.locateROMsDir)
        #self.uiLocateUnsupportedSavestatesDirAct.triggered.connect(self.locateUnsupportedSavestatesDirAct)
        self.uiLocateCustomChallengeSoundAct.triggered.connect(self.locateCustomChallengeSound)
        #if GeoIP2Reader:
        #    self.uiLocateGeommdbAct.triggered.connect(self.locateGeoMMDB)
        #else:
        #    self.uiLocateGeommdbAct.setVisible(False)
        self.uiNotifyPlayerStateChangeAct.toggled.connect(self.__class__.toggleNotifyPlayerStateChange)
        self.uiShowCountryFlagInChatAct.toggled.connect(self.__class__.toggleShowCountryFlagInChat)
        self.uiShowTimestampInChatAct.toggled.connect(self.__class__.toggleShowTimestampInChatAct)
        self.uiHideInGameChatAct.toggled.connect(self.__class__.toggleHideInGameChatAct)
        #self.uiDisableAutoAnnounceAct.toggled.connect(self.__class__.toggleDisableAutoAnnounceUnsupported)
        self.uiDisableAutoColorNicks.toggled.connect(self.__class__.toggleDisableAutoColorNicks)
        self.uiHideGamesWithoutRomAct.toggled.connect(self.toggleHideGamesWithoutRomAct)
        self.uiFilterFavoriteLobbies.toggled.connect(self.toggleFilterFavoriteLobbies)
        if Settings.value(Settings.DEBUG_LOG):
            self.uiDebugLogAct.setChecked(True)
        if Settings.value(Settings.USER_LOG_CHAT):
            self.uiLogChatAct.setChecked(True)
        if Settings.value(Settings.USER_LOG_PLAYHISTORY):
            self.uiLogPlayHistoryAct.setChecked(True)
        self.uiDebugLogAct.triggered.connect(self.__class__.logdebugTriggered)
        self.uiLogChatAct.triggered.connect(self.__class__.loguserChatTriggered)
        self.uiLogPlayHistoryAct.triggered.connect(self.__class__.loguserPlayHistoryTriggered)

    def setupMenuChallengeSound(self):

        def GetChallengeSoundFile(name):
            fba = findFba()
            if fba:
                filename = os.path.join(os.path.dirname(fba), "assets", name+"-challenge.wav")
                if os.path.isfile(filename):
                    return filename
            filename = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "assets", name+"-challenge.wav")
            if filename and os.path.isfile(filename):
                return filename

        def SetChallengeSound(fname):
            Settings.setValue(Settings.CUSTOM_CHALLENGE_SOUND_LOCATION, fname)
            ggpo.common.sound.play()

        def onChallengeSoundToggled(boolean):
            if boolean:
                SetChallengeSound(GetChallengeSoundFile(self.sender().text()))

        self.uiMenuChallengeSoundGroup = QtGui.QActionGroup(self.uiChallengeSoundMenu, exclusive=True)

        self.uiactionBreakrev = QtGui.QAction("breakrev", self)
        self.uiactionBreakrev.setCheckable(True)
        self.uiactionBreakrev.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionBreakrev))

        self.uiactionCaptcomm = QtGui.QAction("captcomm", self)
        self.uiactionCaptcomm.setCheckable(True)
        self.uiactionCaptcomm.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionCaptcomm))

        self.uiactionDdsom = QtGui.QAction("ddsom", self)
        self.uiactionDdsom.setCheckable(True)
        self.uiactionDdsom.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionDdsom))

        self.uiactionDoubledr = QtGui.QAction("doubledr", self)
        self.uiactionDoubledr.setCheckable(True)
        self.uiactionDoubledr.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionDoubledr))

        self.uiactionGarou = QtGui.QAction("garou", self)
        self.uiactionGarou.setCheckable(True)
        self.uiactionGarou.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionGarou))

        self.uiactionJojobane = QtGui.QAction("jojobane", self)
        self.uiactionJojobane.setCheckable(True)
        self.uiactionJojobane.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionJojobane))

        self.uiactionKarnovr = QtGui.QAction("karnovr", self)
        self.uiactionKarnovr.setCheckable(True)
        self.uiactionKarnovr.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionKarnovr))

        self.uiactionKof2002 = QtGui.QAction("kof2002", self)
        self.uiactionKof2002.setCheckable(True)
        self.uiactionKof2002.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionKof2002))

        self.uiactionKof98 = QtGui.QAction("kof98", self)
        self.uiactionKof98.setCheckable(True)
        self.uiactionKof98.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionKof98))

        self.uiactionMatrim = QtGui.QAction("matrim", self)
        self.uiactionMatrim.setCheckable(True)
        self.uiactionMatrim.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionMatrim))

        self.uiactionMshvsf = QtGui.QAction("mshvsf", self)
        self.uiactionMshvsf.setCheckable(True)
        self.uiactionMshvsf.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionMshvsf))

        self.uiactionMslug3 = QtGui.QAction("mslug3", self)
        self.uiactionMslug3.setCheckable(True)
        self.uiactionMslug3.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionMslug3))

        self.uiactionMvsc = QtGui.QAction("mvsc", self)
        self.uiactionMvsc.setCheckable(True)
        self.uiactionMvsc.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionMvsc))

        self.uiactionRbffspec = QtGui.QAction("rbffspec", self)
        self.uiactionRbffspec.setCheckable(True)
        self.uiactionRbffspec.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionRbffspec))

        self.uiactionRingdest = QtGui.QAction("ringdest", self)
        self.uiactionRingdest.setCheckable(True)
        self.uiactionRingdest.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionRingdest))

        self.uiactionRotd = QtGui.QAction("rotd", self)
        self.uiactionRotd.setCheckable(True)
        self.uiactionRotd.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionRotd))

        self.uiactionSamsho2 = QtGui.QAction("samsho2", self)
        self.uiactionSamsho2.setCheckable(True)
        self.uiactionSamsho2.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionSamsho2))

        self.uiactionSf2 = QtGui.QAction("sf2", self)
        self.uiactionSf2.setCheckable(True)
        self.uiactionSf2.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionSf2))

        self.uiactionSfiii3n = QtGui.QAction("sfiii3n", self)
        self.uiactionSfiii3n.setCheckable(True)
        self.uiactionSfiii3n.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionSfiii3n))

        self.uiactionSsf2t = QtGui.QAction("ssf2t", self)
        self.uiactionSsf2t.setCheckable(True)
        self.uiactionSsf2t.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionSsf2t))

        self.uiactionSvc = QtGui.QAction("svc", self)
        self.uiactionSvc.setCheckable(True)
        self.uiactionSvc.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionSvc))

        self.uiactionVsav = QtGui.QAction("vsav", self)
        self.uiactionVsav.setCheckable(True)
        self.uiactionVsav.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionVsav))

        self.uiactionWhp = QtGui.QAction("whp", self)
        self.uiactionWhp.setCheckable(True)
        self.uiactionWhp.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionWhp))

        self.uiactionXmvsf = QtGui.QAction("xmvsf", self)
        self.uiactionXmvsf.setCheckable(True)
        self.uiactionXmvsf.toggled.connect(onChallengeSoundToggled)
        self.uiChallengeSoundMenu.addAction(self.uiMenuChallengeSoundGroup.addAction(self.uiactionXmvsf))


    def setupMenuSmoothing(self):
        # unfortunately Qt Designer doesn't support QActionGroup, we have to code it up
        self.uiMenuSmoothingGroup = QtGui.QActionGroup(self.uiSmoothingMenu, exclusive=True)

        def onSmoothingToggled(boolean):
            if boolean:
                result = re.search(r'[0-9]+', self.sender().text())
                if result:
                    Settings.setValue(Settings.SMOOTHING, result.group(0))

        desc = defaultdictinit({0: ' More jerky', 1: ' Default', 10: ' Laggy'})
        for smooth in range(11):
            act = QtGui.QAction('&' + str(smooth) + desc[smooth], self)
            act.setCheckable(True)
            act.toggled.connect(onSmoothingToggled)
            self.uiSmoothingMenu.addAction(self.uiMenuSmoothingGroup.addAction(act))
            cleanname = self.buildInSmoothingToActionName(smooth)
            setattr(self, cleanname, act)

    def setupMenuTheme(self):
        # unfortunately Qt Designer doesn't support QActionGroup, we have to code it up
        actionTitleShortcuts = set()

        def actionTitle(title):
            shortcutFound = False
            ret = ''
            for c in title:
                l = c.lower()
                if not shortcutFound and l in 'abcdefghijklmnopqrstuvwxy' and l not in actionTitleShortcuts:
                    ret += '&'
                    actionTitleShortcuts.add(l)
                    shortcutFound = True
                ret += c
            return ret

        self.uiMenuThemeGroup = QtGui.QActionGroup(self.uiThemeMenu, exclusive=True)

        self.uiGNGThemeAct = QtGui.QAction(actionTitle("FightCade"), self)
        self.uiGNGThemeAct.setCheckable(True)
        self.uiGNGThemeAct.toggled.connect(ColorTheme.setGNGTheme)
        self.uiThemeMenu.addAction(self.uiMenuThemeGroup.addAction(self.uiGNGThemeAct))

        self.uiDarkThemeAct = QtGui.QAction(actionTitle("Dark Orange"), self)
        self.uiDarkThemeAct.setCheckable(True)
        self.uiDarkThemeAct.toggled.connect(ColorTheme.setDarkTheme)
        self.uiThemeMenu.addAction(self.uiMenuThemeGroup.addAction(self.uiDarkThemeAct))

        for k in QtGui.QStyleFactory.keys():
            act = QtGui.QAction(actionTitle(k), self)
            act.setCheckable(True)
            act.toggled.connect(self.setStyleCallback(k))
            self.uiThemeMenu.addAction(self.uiMenuThemeGroup.addAction(act))
            cleanname = self.buildInStyleToActionName(k)
            setattr(self, cleanname, act)
        self.uiCustomQssFileAct = QtGui.QAction(actionTitle("Custom Qss stylesheet"), self)
        self.uiCustomQssFileAct.triggered.connect(self.setCustomQss)
        self.uiThemeMenu.addAction(self.uiCustomQssFileAct)

    def setupUserTable(self):
        model = PlayerModel(self.controller)
        self.uiPlayersTableV.setModel(model)
        self.uiPlayersTableV.clicked.connect(model.onCellClicked)
        self.uiPlayersTableV.doubleClicked.connect(model.onCellDoubleClicked)
        self.uiPlayersTableV.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiPlayersTableV.verticalHeader().setVisible(False)
        hh = self.uiPlayersTableV.horizontalHeader()
        hh.setMinimumSectionSize(25)
        hh.setHighlightSections(False)
        hh.resizeSection(PlayerModel.STATE, 25)
        width = hh.fontMetrics().boundingRect('Ping').width() + 18
        # windows's sort indicator is displayed at the top so no extra space needed
        if not IS_WINDOWS:
            width += 10
        hh.resizeSection(PlayerModel.PING, width)
        hh.resizeSection(PlayerModel.IGNORE, 25)
        hh.resizeSection(PlayerModel.PLAYER, 165)
        hh.resizeSection(PlayerModel.OPPONENT, 165)
        hh.setResizeMode(PlayerModel.STATE, QtGui.QHeaderView.Fixed)
        hh.setResizeMode(PlayerModel.PING, QtGui.QHeaderView.Fixed)
        hh.setResizeMode(PlayerModel.IGNORE, QtGui.QHeaderView.Fixed)
        self.uiPlayersTableV.setSortingEnabled(True)
        self.uiPlayersTableV.sortByColumn(PlayerModel.DEFAULT_SORT, Qt.AscendingOrder)
        hh.sortIndicatorChanged.connect(self.sortIndicatorChanged)

    def sortIndicatorChanged(self, index, order):
        if index not in self.uiPlayersTableV.model().sortableColumns:
            self.uiPlayersTableV.horizontalHeader().setSortIndicator(
                self.uiPlayersTableV.model().lastSort, self.uiPlayersTableV.model().lastSortOrder)

    def toggleAFK(self, state):
        self.controller.sendToggleAFK(state)

    @staticmethod
    def toggleDisableAutoAnnounceUnsupported(state):
        Settings.setBoolean(Settings.DISABLE_AUTO_ANNOUNCE_UNSUPPORTED, state)

    @staticmethod
    def toggleDisableAutoColorNicks(state):
        Settings.setBoolean(Settings.DISABLE_AUTOCOLOR_NICKS, state)

    @staticmethod
    def toggleNotifyPlayerStateChange(state):
        Settings.setBoolean(Settings.NOTIFY_PLAYER_STATE_CHANGE, state)

    @staticmethod
    def toggleShowCountryFlagInChat(state):
        Settings.setBoolean(Settings.SHOW_COUNTRY_FLAG_IN_CHAT, state)

    @staticmethod
    def toggleShowTimestampInChatAct(state):
        Settings.setBoolean(Settings.SHOW_TIMESTAMP_IN_CHAT, state)

    @staticmethod
    def toggleHideInGameChatAct(state):
        Settings.setBoolean(Settings.HIDE_INGAME_CHAT, state)

    def toggleHideGamesWithoutRomAct(self, state):
        Settings.setBoolean(Settings.HIDE_GAMES_WITHOUT_ROM, state)
        self.hidemissing = state
        if not self.expectFirstChannelResponse:
            self.expectFirstChannelResponse=True
            self.controller.sigChannelsLoaded.emit()

    def toggleFilterFavoriteLobbies(self, state):
        Settings.setBoolean(Settings.FILTER_FAVORITES, state)
        self.showfavorites = state
        if not self.expectFirstChannelResponse:
            self.expectFirstChannelResponse=True
            self.controller.sigChannelsLoaded.emit()

    @staticmethod
    def toggleSound(state):
        Settings.setBoolean(Settings.MUTE_CHALLENGE_SOUND, state)

    @staticmethod
    def toggleNotifySound(state):
        Settings.setBoolean(Settings.MUTE_NOTIFY_SOUND, state)

    def updateStatusBar(self):
        self.uiStatusbar.showMessage(self.controller.statusBarMessage())
