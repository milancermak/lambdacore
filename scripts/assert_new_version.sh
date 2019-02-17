#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

readonly DIR="$( cd "$(dirname "$0")" ; pwd -P )"
readonly ROOT_DIR="$DIR/.."
readonly NEW_VERSION="$(cat $ROOT_DIR/SAR_APP_VERSION.txt)"
readonly PUBLISHED_VERSION="$(aws serverlessrepo list-application-versions \
                                  --application-id $APP_ID \
                                  --query 'Versions[0].SemanticVersion')"

if [ "$NEW_VERSION" == "$PUBLISHED_VERSION" ]; then
    echo "Trying to deploy version $NEW_VERSION that already exitst in SAR"
    exit 1
fi
