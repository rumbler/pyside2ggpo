#!/bin/bash

# make sure this is run as root
uid=$(id -ur)
if [ "$uid" != "0" ]; then
        echo "ERROR: This script must be run as root."
	echo "try: sudo $0"
        exit 1
fi

# ubuntu/debian based distributions
if [ -x /usr/bin/apt-get ]; then
	apt-get install wine python-qt4-phonon python-qt4
	exit $?
fi

# archlinux
if [ -x /usr/bin/pacman ]; then
	pacman -S multilib/wine extra/pyqt4-common extra/python-pyqt4 extra/phonon-qt4
	exit $?
fi
