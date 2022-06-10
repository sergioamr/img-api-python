#!/usr/bin/env bash

cd "${BASH_SOURCE%/*}"

export IMG_API_KEY=1234
export WTF_CSRF_SECRET_KEY=1234
export IMG_API_BASE_ENDPOINT=dummy

. .venv/bin/activate

python run_tests.py