#!/bin/sh

find_python() {

	python -V 2>&1 |grep "^Python 2\." >/dev/null
	if [ $? -eq 0 ]; then
		PYTHON=python
	else
		python2 -V 2>&1 |grep "^Python 2\." >/dev/null
		if [ $? -eq 0 ]; then
			PYTHON=python2
		else
			python2.7 -V 2>&1 |grep "^Python 2\." >/dev/null
			if [ $? -eq 0 ]; then
				PYTHON=python2.7
			else
				python2.6 -V 2>&1 |grep "^Python 2\." >/dev/null
				if [ $? -eq 0 ]; then
					PYTHON=python2.6
				fi
			fi
		fi
	fi
	if [ -z "${PYTHON}" ]; then
		echo "ERROR: can't find python 2.x"
		exit 1
	fi
}
