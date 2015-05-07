#!/bin/bash

# make sure this is run as root
uid=$(id -ur)
if [ "$uid" != "0" ]; then
        echo "ERROR: This script must be run as root."
	if [ -x /usr/bin/sudo ]; then
		echo "try: sudo $0"
	fi
        exit 1
fi

# ubuntu/debian based distributions
if [ -x /usr/bin/apt-get ]; then
	apt-get install wine python-qt4-phonon python-qt4
	exit $?
fi

# archlinux
if [ -x /usr/bin/pacman ]; then
	pacman -S multilib/wine multilib/lib32-mpg123 extra/pyqt4-common extra/python-pyqt4 extra/phonon-qt4 extra/python2-pyqt4 extra/python2-sip
	exit $?
fi

# fedora (untested)
if [ -x /usr/bin/yum ]; then
	yum install wine pyqt4
	exit $?
fi

# suse/opensuse (untested)
if [ -x /usr/bin/zypper ] ; then
	zypper in wine python-qt4
	exit $?
fi

echo "Your distribution is not supported :("
echo "Please install 'pyqt4' and 'wine' to run fightcade."
exit 1
