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
	cp -R assets config fightcade ggpo ggpofba-ng.exe ggpofba.sh ggponet.dll __init__.py kailleraclient.dll LICENSE linux-install.sh main.py README.md VERSION cheats flyers previews recordings ROMs savestates screenshots titles /tmp/FightCade/
	rm -rf /tmp/FightCade/ggpo/resources/assets/
	rm -rf /tmp/FightCade/ggpo/scripts/
	cd /tmp ; tar cvfz fightcade-linux-v0`cat FightCade/VERSION`.tar.gz FightCade
	rm -rf /tmp/FightCade savestates/
	ls -lat /tmp/fightcade-linux-v0* |head -n 1

win: cleanbuild
	/Development/python-windows-packager/package.sh ./ggpofba.py ggpofba
	cp dist/ggpofba.exe .
	/Development/python-windows-packager/package.sh ./main.py fightcade
	cp dist/fightcade.exe ./FightCade.exe
	rm -rf build dist
	mkdir /tmp/FightCade/
	cp -R assets config FightCade.exe ggpofba.exe ggpofba-ng.exe ggponet.dll kailleraclient.dll LICENSE VERSION cheats flyers previews recordings ROMs savestates screenshots titles /tmp/FightCade/
	cd /tmp ; zip -r fightcade-win32-v0`cat FightCade/VERSION`.zip FightCade
	rm -rf /tmp/FightCade savestates/ FightCade.exe fightcade.spec ggpofba.exe ggpofba.spec
	ls -lat /tmp/fightcade-win32-v0* |head -n 1

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
