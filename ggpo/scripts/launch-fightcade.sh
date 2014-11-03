#!/bin/sh

# change to the app's directory
cd "${0%/*}"

# create symlink to ROMs folder in the user's home
if [ ! -e "ROMs" ] ; then 
	mkdir -p ${HOME}/ROMs
	ln -s ${HOME}/ROMs ROMs
fi

# launch fightcade client
./fightcade
