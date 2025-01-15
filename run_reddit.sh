#!/usr/bin/env bash

cd "${BASH_SOURCE%/*}"

if [ ! -d ".venv" ]
then
   ./update.sh
fi

. .venv/bin/activate

python run_reddit.py