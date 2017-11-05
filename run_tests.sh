succ="\x1b[0;32;1mSuccess!\x1b[0;31;0m\n"
fail="\x1b[0;31;1mFAILED!\x1b[0;31;0m\n"
printf "flake8: "
flake8 $1 &> /dev/null
if (($? == 0))
then
	printf $succ
else
	printf $fail
fi
printf "pylint: "
pylint $1 &> /dev/null
if (($? == 0))
then
        printf $succ
else
        printf $fail
fi
printf "nosetests without device: "
nosetests -a '!require_dev' &> /dev/null
if (($? == 0))
then
        printf $succ
else
	printf $fail
fi
printf "nosetests with dev: "
nosetests --tc-file .testconfig.yaml --tc-format yaml &> /dev/null
if (($? == 0))
then
        printf $succ
else
        printf $fail
fi

