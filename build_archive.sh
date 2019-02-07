#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

if [ -e layer.zip ]; then
    rm layer.zip
fi

if [ -d python ]; then
    rm -r ./python
fi

# the resulting library (layer) needs to be in a directory named
# python, so that when it is extracted in the Lambda exec env,
# into /opt, is can be easily import-ed; see:
# https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path
mkdir python
cp -r lambdacore python
pip install -r lambdacore/requirements.txt -t python --no-cache-dir
zip -rm layer.zip python -x '*/__pycache__/*'
