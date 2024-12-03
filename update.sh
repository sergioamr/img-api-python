#!/usr/bin/env bash

cd "${BASH_SOURCE%/*}"

if [ ! -d ".venv" ]
then
   echo "INSTALLING VENV "
   python3 -m venv .venv


. .venv/bin/activate

pip3 install -r requirements.txt --upgrade
