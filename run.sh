#!/usr/bin/env bash

cd "${BASH_SOURCE%/*}"

if [ ! -d ".venv" ]
then
   ./update.sh
fi

export IMG_API_KEY=1234
export WTF_CSRF_SECRET_KEY=1234
export IMG_API_BASE_ENDPOINT=dummy

# set the environment variables in case you need to customize some path or setting
set -a
source .env || true
set +a


. .venv/bin/activate


python run_fetch_stocktwits.py
