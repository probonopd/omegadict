#!/bin/bash

# Push files to Bintray
# https://bintray.com/docs/api/

trap 'exit 1' ERR

which curl || exit 1
which grep || exit 1

API=https://api.bintray.com

FILE=$1
[ -f "$FILE" ] || exit 1

BINTRAY_USER="probono"
BINTRAY_API_KEY=$BINTRAY_API_KEY # env
BINTRAY_REPO="omegadict"
PCK_NAME="dicts"

if [ ! $(env | grep BINTRAY_API_KEY ) ] ; then
  echo "Environment variable \$BINTRAY_API_KEY missing"
  exit 1
fi

# Do not upload artefacts generated as part of a pull request
if [ $(env | grep TRAVIS_PULL_REQUEST ) ] ; then
  if [ "$TRAVIS_PULL_REQUEST" != "false" ] ; then
    echo "Not uploading since this is a pull request"
    exit 0
  fi
fi

CURL="curl -u${BINTRAY_USER}:${BINTRAY_API_KEY} -H Content-Type:application/json -H Accept:application/json"

VERSION="1"

if [ "$VERSION" == "" ] ; then
  echo "* VERSION missing, exiting"
  exit 1
else
  echo "* VERSION $VERSION"
fi

echo ""
echo "Uploading and publishing ${FILE}..."
${CURL} -T ${FILE} "${API}/content/${BINTRAY_USER}/${BINTRAY_REPO}/${PCK_NAME}/${VERSION}/$(basename ${FILE})?publish=1&override=1"
