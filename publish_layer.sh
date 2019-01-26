#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

aws lambda publish-layer-version \
--layer-name py-core \
--compatible-runtimes python3.6 python3.7 \
--license-info Apache-2.0 \
--zip-file fileb://layer.zip
