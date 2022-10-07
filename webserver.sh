#!/bin/sh

usageexit() {
	cat <<-_EOF
usage: $0 [-C] [-d] [-d] [-a <anonymize_hex_salt>] <input_data_directory> [<flask options>]
   -C : disable cache
   -d : activate debug output, twice disables multithreading
   -a <salt> : anonymise output network data
_EOF
	exit 1
}
trace() { echo "$ $*" >&2; "$@"; }

DIR="$(dirname $0)"

set -e

[ $# -lt 1 -o "$1" = "-h" ] && usageexit

[ "$1" = "-C" ] && NETMAP_DISABLE_CACHE=1 && shift
[ "$1" = "-d" ] && FLASK_DEBUG=1 && NETMAP_DEBUG=1 && shift
[ "$1" = "-d" ] && NETMAP_DEBUG=2 && shift
[ "$1" = "-a" ] && NETMAP_ANONYMIZE_HEX_SALT=$2 && shift && shift
input_data_directory="$1" && shift

trace export FLASK_APP=netmap_flask.py
trace export FLASK_DEBUG=${FLASK_DEBUG:-0}
trace export NETMAP_INPUT_DATA_DIRECTORY="$(realpath $input_data_directory)"
trace export NETMAP_DISABLE_CACHE="${NETMAP_DISABLE_CACHE:-0}"
trace export NETMAP_DEBUG=${NETMAP_DEBUG:-$FLASK_DEBUG}
trace export NETMAP_ANONYMIZE_HEX_SALT=${NETMAP_ANONYMIZE_HEX_SALT:-""}

trace cd $DIR/flask
trace python3 -m flask run $@
