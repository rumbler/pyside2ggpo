#!/bin/sh

# change to the app's directory
cd "${0%/*}"

# check if this is Yosemite or earlier
ver=$(sw_vers -productVersion)
min=$(echo "$ver" |cut -f 2 -d ".")

# copy files from right OS version
if [ $min -ge 10 ]; then
	cp -R Yosemite/* .
else
	cp -R Mavericks/* .
fi

# launch fightcade client
./fightcade
