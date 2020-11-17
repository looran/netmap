#!/bin/sh

trace() { echo "# $*"; "$@"; }
D="$(dirname $0)"

set -e

[ $# -lt 2 ] && echo "usage: $0 [-T] <output_directory> <host_ip>:<host_sshalias>[:k8s] ...]" && exit 1
gendata_opts=""
[ "$1" == "-T" ] && gendata_opts="-T" && shift
output_dir="$1" && shift
remote_hosts="$@"

for remote_host in $remote_hosts; do
	ip=$(echo $remote_host |cut -d: -f1)
	sshalias=$(echo $remote_host |cut -d: -f2)
	k8s=$(echo $remote_host |cut -d: -f3)
	echo "[+] fetching data from $ip ($sshalias)"
	trace ssh $sshalias "mkdir -p /tmp/netmap/data"
	trace rsync -avP $D/generate_data.sh $sshalias:/tmp/netmap/
	trace ssh $sshalias "/tmp/netmap/generate_data.sh $gendata_opts /tmp/netmap/data $ip"
	if [ ! -z "$k8s" ]; then
		trace rsync -avP $D/generate_data_k8s.sh $sshalias:/tmp/netmap/
		trace ssh $sshalias "SSH_NODES_CMD="$SSH_NODES_CMD" /tmp/netmap/generate_data_k8s.sh $gendata_opts /tmp/netmap/data"
	fi
	trace rsync -avP "$sshalias:/tmp/netmap/data/" $output_dir
	trace ssh $sshalias "rm -rf /tmp/netmap"
done

files_count=$(ls -1 $output_dir |wc -l)
echo "[*] DONE, hosts output in $output_dir, $files_count files"

