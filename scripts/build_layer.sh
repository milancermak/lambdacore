#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

readonly DIR="$( cd "$(dirname "$0")" ; pwd -P )"
readonly ROOT_DIR="$DIR/.."
readonly LAYER_DIR="$ROOT_DIR/lambdacore"

# the resulting library (layer) needs to be in a directory named
# python, so that when it is extracted in the Lambda exec env,
# into /opt, is can be easily import-ed; see:
# https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path
mkdir "$ROOT_DIR/python"
cp -r "$LAYER_DIR" python
pip install -r "$LAYER_DIR/requirements.txt" -t python --no-cache-dir
zip -rm layer.zip python -x '*/__pycache__/*' '*/requirements.txt'
