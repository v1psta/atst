#!/bin/bash
#
# script/generate_build_info: Generates buildinfo.html and buildinfo.json and 
#                             places them in a publically accessable static asset
#                             folder

source "$(dirname "${0}")"/../script/include/global_header.inc.sh

# Config
APP_NAME="ATST"
BUILD_URL="https://travis-ci.org/$TRAVIS_REPO_SLUG/builds/$TRAVIS_BUILD_ID"
STATIC_DIR="./static"

echo "### Generate Build Info ###"

echo "Gathering info from git..."
COMMIT_AUTHOR=$(git log -1 --pretty=%aN)
COMMIT_AUTHOR_EMAIL=$(git log -1 --pretty=%aE)
# Escape all double quotes in commit message and switch newlines for \n 
# (for JSON compatability)
COMMIT_MESSAGE_JSON=$(git log -1 --pretty=format:%B | sed -e 's#\([^\\]\)"#\1\\"#g' | awk 1 ORS='\\n')
# Escape all < and > characters in commit message, insert pivotal story links,
# and trade newlines for <BR/> tags
COMMIT_MESSAGE_HTML=$(git log -1 --pretty=format:%B | sed -e 's#>#&gt;#g' | sed -e 's#<#&lt;#g' | awk 1 ORS='<BR/>')

# Assemble https based git repo url
GIT_REPO=$(git config --get remote.origin.url | cut -d ':' -f 2)
GIT_URL="https://github.com/${GIT_REPO}"
# Drop the trailing .git for generating github links
GITHUB_BASE_URL="${GIT_URL%.git}"

APP_CONTAINER_CREATE_DATE=$(date '+%Y-%m-%d')
APP_CONTAINER_CREATE_TIME=$(date '+%H:%M:%S')

echo "Generating public/buildinfo.json ..."
cat > ${STATIC_DIR}/buildinfo.json <<ENDJSON
{
  "build_info" : {
    "project" : "${APP_NAME}",
    "build_id" : "${TRAVIS_BUILD_ID}",
    "url" : "${BUILD_URL}"
  },
  "app_package_info" : {
    "create_date" : "${APP_CONTAINER_CREATE_DATE}",
    "create_time" : "${APP_CONTAINER_CREATE_TIME}"
  },
  "git_info" : {
    "repository" : "${GIT_URL}",
    "branch" : "${TRAVIS_BRANCH}",
    "commit" : {
      "sha" : "${TRAVIS_COMMIT}",
      "author_name" : "${COMMIT_AUTHOR}",
      "author_email" : "${COMMIT_AUTHOR_EMAIL}",
      "message" : "${COMMIT_MESSAGE_JSON}"
    }
  }
}
ENDJSON

echo "Generating public/buildinfo.html ..."
cat > ${STATIC_DIR}/buildinfo.html <<ENDHTML
<HTML>
<HEAD>
        <TITLE>${APP_NAME} build ${BUILD_NUMBER} info</TITLE>
        <STYLE>
                table {
                                display: table;
                                border-width: 1px;
                                border-color: green;
                                border-spacing: 0px;
                }
                td {
                                padding: 5px;
                                vertical-align: top;
                }
                td.label {
                                text-align: right;
                                font-weight: bold;
                }
        </STYLE>
</HEAD>
<BODY>
<TABLE border="1">
<TR>
        <TH colspan="2">BuildInfo</TH>
</TR>
<TR>
        <TD class="label">App Package Creation Time:</TD>
        <TD>${APP_CONTAINER_CREATE_DATE} ${APP_CONTAINER_CREATE_TIME}</TD>
</TR>
<TR>
        <TD class="label">Build Number:</TD>
        <TD><A target="_blank" href="${BUILD_URL}consoleFull">${BUILD_NUMBER}</A></TD>
</TR>
<TR>
        <TD class="label">Commit SHA:</TD>
        <TD><A target="_blank" href="${GITHUB_BASE_URL}/commit/${TRAVIS_COMMIT}">${TRAVIS_COMMIT}</A></TD>
</TR>
<TR>
        <TD class="label">Commit Author:</TD>
        <TD>${COMMIT_AUTHOR} &lt;${COMMIT_AUTHOR_EMAIL}&gt;</TD>
</TR>
<TR>
        <TD class="label">Commit Message:</TD>
        <TD>${COMMIT_MESSAGE_HTML}</TD>
</TR>
</TABLE>
</BODY>
</HTML>
ENDHTML
