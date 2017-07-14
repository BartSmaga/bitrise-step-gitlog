#!/bin/bash

# fail if any commands fails
set -e

# debug log
#set -x

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OPT="--last 1"

if [ -n "${ticket_prefix}" ] ; then
    OPT+=" --ticket_prefix=${ticket_prefix}"
fi

# JIRA options
if [ -n "${jira_url}" ] ; then
    OPT+=" --jira-url=${jira_url}"
fi
if [ -n "${jira_username}" ] ; then
    OPT+=" --jira-username=${jira_username}"
fi
if [ -n "${jira_password}" ] ; then
    OPT+=" --jira-password=${jira_password}"
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

exit 1
exit 0
