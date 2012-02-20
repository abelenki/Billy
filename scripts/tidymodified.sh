#!/bin/sh
THIS_DIRNAME=`dirname $0`;
PYTHON_TIDY=`readlink -f ${THIS_DIRNAME}/python-tidy.py`
for f in `git status -s | grep -E '^.M.+\.py' | sed -e s/^.M//g`;
    do
        DEST=`tempfile`
        SRC=`readlink -f ${f}`
        CMD="${PYTHON_TIDY} ${SRC} ${DEST}"
        OK=`${CMD}`

        if [ $? -eq 0 ]; then
            echo ${CMD};
            echo `mv ${DEST} ${SRC}`
        fi
done;
