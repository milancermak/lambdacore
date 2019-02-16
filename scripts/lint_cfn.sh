#!/bin/bash
set -eu

readonly DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly INFRASTRUCTURE_DIR="$DIR/../infrastructure"

EXIT_STATUS=0

echo 'Linting CFN templates'
find $INFRASTRUCTURE_DIR -name '*.yml' ! -name '*buildspec*' -print0 | xargs -0 -n1 cfn-lint --template || EXIT_STATUS=$?

[ $EXIT_STATUS == 0 ] && echo -e 'All good\n'

exit $EXIT_STATUS
