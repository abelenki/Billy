#!/bin/sh
#nosetests --with-gae --gae-lib-root=../google_appengine -v

APPENGINE_PATH='../google_appengine'
TEST_COMMAND="nosetests --with-gae --gae-lib-root=$APPENGINE_PATH -v $1"

if [ -z $1 ]
then
    TEST_COMMAND=${TEST_COMMAND} $1
fi
for i in `find . -name "*.pyc"`; do rm $i; done;
echo ${TEST_COMMAND}
$TEST_COMMAND
