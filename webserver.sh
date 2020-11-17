#!/bin/sh

DIR="$(dirname $0)"

set -e

[ $# -ne 1 ] && echo "usage: $0 <input_data_directory>" && exit 1

set -x

export FLASK_APP=netmap_flask.py
export FLASK_DEBUG=${FLASK_DEBUG:-0}
export NETMAP_INPUT_DATA_DIRECTORY="$(realpath $1)"
export NETMAP_DEBUG=${NETMAP_DEBUG:-$FLASK_DEBUG}

cd $DIR/flask
flask run
