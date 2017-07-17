#!/bin/bash

# fail if any commands fails
set -e

# debug log
#set -x

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OPT=""

if [ -n "${last_n}" ] ; then
    OPT+=" --last=${last_n}"
fi
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

if [ -d "${deploy_dir}" ]; then
    CHANGELOG_PATH="${deploy_dir}"/CHANGELOG.md
    echo "Writing the changelog to ${CHANGELOG_PATH}"
    echo "${CHANGELOG}" > ${CHANGELOG_PATH}
    envman add --key GITLOG_PATH --value "${CHANGELOG_PATH}"
fi

echo "${CHANGELOG}"

if which envman >/dev/null; then
    envman add --key GITLOG_MESSAGE --value "${CHANGELOG}"
fi

exit 0
