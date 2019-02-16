#!/bin/sh

SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
ROOT_DIR="$SCRIPT_DIR/.."
SRC_DIR="$ROOT_DIR/lambdacore"
TESTS_DIR="$ROOT_DIR/tests"

EXIT_STATUS=0 # captures the fail code if any of the lint command fails; the final value is returned as the exit value of the script

echo 'Linting src'
# running pylint on src files with the default configuration
find $SRC_DIR -name '*.py' -not -path '*/lib/*' | xargs pylint --rcfile=$ROOT_DIR/.pylintrc || EXIT_STATUS=$?

echo 'Linting tests'
# disabling extra lint warnings for test files
find $TESTS_DIR -name '*.py' ! -name 'conftest.py' | xargs pylint --rcfile=$ROOT_DIR/.pylintrc --disable=multiple-imports,no-name-in-module,wrong-import-position,import-error,redefined-outer-name,ungrouped-imports,line-too-long,invalid-name || EXIT_STATUS=$(($EXIT_STATUS + $?))

exit $EXIT_STATUS
