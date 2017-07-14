#!/bin/bash

# fail if any commands fails
set -e

# debug log
#set -x

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OPT="--last 1"

if [ -n "${ticket_prefix}" ] ; then
    OPT+=" --ticket_prefix ${ticket_prefix}"
fi

cd ${THIS_SCRIPT_DIR}

pip3 install virtualenv
virtualenv .
source ./bin/activate
pip3 install -r requirements.txt

CHANGELOG=`./gitlog.py ${OPT} ${BITRISE_SOURCE_DIR}`

echo "${CHANGELOG}"

if which envman >/dev/null; then
	envman add --key GITLOG_MESSAGE --value "${CHANGELOG}"
fi

exit 0
