#!/bin/bash
succ="\x1b[0;32;1mSuccess!\x1b[0;31;0m\n"
fail="\x1b[0;31;1mFAILED!\x1b[0;31;0m\n"
printf "flake8: "
flake8 bluew --ignore=F401 &> /dev/null
if (($? == 0))
then
	printf $succ
else
	printf $fail
fi
printf "pylint: "
pylint --rcfile=.pylintrc --notes=FIXME bluew &> /dev/null
if (($? == 0))
then
        printf $succ
else
        printf $fail
fi
printf "mypy: "
mypy --no-warn-no-return --ignore-missing-imports . &> /dev/null
if (($? == 0))
then
        printf $succ
else
        printf $fail
fi
printf "nosetests with dev: "
nosetests tests --tc-file=tests/.testconfig.yaml --tc-format=yaml &> .nosedump
if (($? == 0))
then
        printf $succ
else
        printf $fail
fi

