#!/bin/sh

DIR="$(dirname $0)"

set -e

[ $# -lt 1 -o "$1" = "-h" ] && echo "usage: $0 [-C] [-d] [-a <anonymize_hex_salt>] <input_data_directory> [<flask options>]" && exit 1

set -x

[ "$1" = "-C" ] && NETMAP_DISABLE_CACHE=1 && shift
[ "$1" = "-d" ] && FLASK_DEBUG=1 && shift
[ "$1" = "-a" ] && NETMAP_ANONYMIZE_HEX_SALT=$2 && shift && shift
input_data_directory="$1" && shift

export FLASK_APP=netmap_flask.py
export FLASK_DEBUG=${FLASK_DEBUG:-0}
export NETMAP_INPUT_DATA_DIRECTORY="$(realpath $input_data_directory)"
export NETMAP_DISABLE_CACHE="${NETMAP_DISABLE_CACHE:-0}"
export NETMAP_DEBUG=${NETMAP_DEBUG:-$FLASK_DEBUG}
export NETMAP_ANONYMIZE_HEX_SALT=${NETMAP_ANONYMIZE_HEX_SALT:-""}

cd $DIR/flask
python3 -m flask run $@
