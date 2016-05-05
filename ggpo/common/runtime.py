# -*- coding: utf-8 -*-
import platform
import os
from shutil import move

__all__ = ['IS_WINDOWS', 'IS_OSX', 'IS_LINUX', 'IS_WINDOWS_XP', 'Phonon', 'GeoIP2Reader', 'winsound', 'CONFIG_DIR']

IS_WINDOWS = False
IS_OSX = False
IS_LINUX = False
IS_WINDOWS_XP = False

_platform = platform.system()
if _platform == 'Windows':
    IS_WINDOWS = True
elif _platform == 'Darwin':
    IS_OSX = True
elif _platform == 'Linux':
    IS_LINUX = True
if IS_WINDOWS and platform.release() == 'XP':
    IS_WINDOWS_XP = True

Phonon = None
try:
    from PyQt4.phonon import Phonon
except ImportError:
    pass

GeoIP2Reader = None
try:
    from geoip2.database import Reader as GeoIP2Reader
except ImportError:
    pass

winsound = None
if IS_WINDOWS:
    try:
        import winsound
    except ImportError:
        pass

if IS_WINDOWS:
    CONFIG_DIR=os.path.join(os.path.abspath(os.path.expanduser("~")), 'fightcade-config')
else:
    CONFIG_DIR=os.path.join(os.path.abspath(os.path.expanduser("~")), '.config/fightcade')

try:
    os.makedirs(CONFIG_DIR)
except:
    pass

try:
    old_cfg=os.path.join(os.path.abspath(os.path.expanduser("~")), 'ggpo-ng.ini')
    if os.path.isfile(old_cfg):
        new_cfg=os.path.join(CONFIG_DIR,'fightcade.ini')
        move(old_cfg, new_cfg)
except:
    pass

try:
    old_emu_bkp=os.path.join(os.path.abspath(os.path.expanduser("~")), 'ggpofba-ng.bkp.ini')
    if os.path.isfile(old_emu_bkp):
        move(old_emu_bkp, os.path.join(CONFIG_DIR,'ggpofba-ng.bkp.ini'))
except:
    pass
