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

.PHONY: all ui qrc clean osxapp osxdmg osxclean
all: ui qrc
ui: $(UIPYFILES)
qrc: $(QRCPYFILES)

clean:
	rm -f $(UIPYFILES) $(UIPYFILES:.py=.pyc) $(QRCPYFILES:.py=.pyc) 

linux: cleanbuild
	pyinstaller --onefile -i ggpo/resources/img/icon.ico -n fightcade --runtime-hook ggpo/scripts/runtimehook.py main.py
win: cleanbuild
	/Development/python-windows-packager/package.sh ./main.py fightcade
osx: cleanbuild
	pyinstaller --onefile -w -i ggpo/resources/img/icon.icns -n fightcade --runtime-hook ggpo/scripts/runtimehook.py main.py

dmg: osx
	cd dist; \
	hdiutil create -srcfolder FightCade.app -volname FightCade -fs HFS+ -fsargs '-c c=64,a=16,e=16' -format UDRW -size 60M fightcade_tmp.dmg; \
	hdiutil convert fightcade_tmp.dmg -format UDZO -imagekey zlib-level=9 -o fightcade.dmg ; \
	rm -f fightcade_tmp.dmg

cleanbuild:
	rm -rf build dist
