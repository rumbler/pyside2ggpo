PYUIC = pyuic4
PYRCC = pyrcc4

UIFILES := $(wildcard ggpo/gui/ui/*.ui)
UIPYFILES := $(UIFILES:.ui=_ui.py)
QRCFILES := $(wildcard ggpo/resources/*.qrc)
QRCPYFILES := $(QRCFILES:.qrc=_rc.py)

%_ui.py: %.ui
	$(PYUIC) $< --output $@

%_rc.py : %.qrc
	$(PYRCC) $< -o $@

.PHONY: all ui qrc clean
all: ui qrc
ui: $(UIPYFILES)
qrc: $(QRCPYFILES)

clean:
	rm -f $(UIPYFILES) $(UIPYFILES:.py=.pyc) $(QRCPYFILES:.py=.pyc) 

linux: cleanbuild
	rm -rf /tmp/FightCade/
	mkdir /tmp/FightCade/
	cp -R assets config fightcade ggpo ggpofba-ng.exe ggpofba.sh ggponet.dll __init__.py kailleraclient.dll LICENSE main.py README.md VERSION cheats flyers previews recordings ROMs savestates screenshots titles /tmp/FightCade/
	rm -rf /tmp/FightCade/ggpo/resources/assets/
	echo "sudo apt-get install wine python-qt4-phonon python-qt4" > /tmp/FightCade/install.sh
	chmod 755 /tmp/FightCade/install.sh
	cd /tmp ; tar cvfz fightcade-linux-v0`cat FightCade/VERSION`.tar.gz FightCade
	rm -rf /tmp/FightCade
	ls -lat /tmp/fightcade-linux-v0* |head -n 1

win: cleanbuild
	/Development/python-windows-packager/package.sh ./main.py fightcade
osx: cleanbuild
	#pyinstaller --onefile -w -i ggpo/resources/img/icon.icns -n fightcade --runtime-hook ggpo/scripts/runtimehook.py main.py
	pyinstaller -w -i ggpo/resources/img/icon.icns -n fightcade --runtime-hook ggpo/scripts/runtimehook.py main.py

dmg:
	cd .. ; \
	hdiutil create -srcfolder FightCade.app -volname GGPO-NG -fs HFS+ -fsargs '-c c=64,a=16,e=16' -format UDRW -size 60M FightCade_tmp.dmg; \
	hdiutil convert FightCade_tmp.dmg -format UDZO -imagekey zlib-level=9 -o FightCade.dmg ; \
	rm -f FightCade_tmp.dmg

cleanbuild:
	rm -rf build dist
	rm -rf cheats flyers previews recordings ROMs savestates screenshots titles
	mkdir cheats flyers previews recordings ROMs savestates screenshots titles
	cp ../fightcadestates/*.fs savestates/
