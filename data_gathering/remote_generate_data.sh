#!/bin/bash

trace() { echo "# $*"; "$@"; }
D="$(dirname $0)"
SSH_OPTS=${SSH_OPTS:-""}

set -e

[ $# -lt 2 ] && echo "usage: $0 [-v] [-T] <output_directory> <ip|sshalias>[:k8s][:ssh_pre=\"SSH-CMD-PREFIX\"] ...]" && exit 1
gendata_opts=""
[ "$1" = "-v" ] && gendata_opts="$gendata_opts -v" && shift
[ "$1" = "-T" ] && gendata_opts="$gendata_opts -T" && shift
output_dir="$1" && shift
[ ! -e "$output_dir" ] && echo "error: directory does not exist: $output_dir" && exit 1
now=$(date +%Y%m%d_%H%M%S)
echo "$now $*" >> "$output_dir/remote_generate_data_${now}.log"
echo "SSH_OPTS='$SSH_OPTS'"

for remote_host in "$@"; do
	sshalias=$(echo $remote_host |cut -d: -f1)
	ip=$(ssh -G $sshalias |egrep -i "^hostname" |cut -d' ' -f2)
	k8s=0
	ssh_pre=""
	while read opt; do
		case $opt in
			k8s) k8s=1; ;;
			ssh_pre*) ssh_pre="$(echo $opt |cut -d= -f2-)"; ;;
		esac
	done < <(echo $remote_host |cut -d: -f2- |tr ':' '\n')
	echo "[+] gathering data from $sshalias ($ip) ssh_pre='$ssh_pre' k8s=$k8s"
	trace $ssh_pre ssh $SSH_OPTS $sshalias "mkdir -p /tmp/netmap/data"
	trace $ssh_pre scp $SSH_OPTS $D/generate_data.sh $sshalias:/tmp/netmap/
	trace $ssh_pre ssh $SSH_OPTS $sshalias "/tmp/netmap/generate_data.sh $gendata_opts /tmp/netmap/data $ip"
	if [ $k8s -eq 1 ]; then
		trace $ssh_pre scp $SSH_OPTS $D/generate_data_k8s.sh $sshalias:/tmp/netmap/
		trace $ssh_pre ssh $SSH_OPTS $sshalias "SSH_NODES_CMD="$SSH_NODES_CMD" /tmp/netmap/generate_data_k8s.sh $gendata_opts /tmp/netmap/data $ip"
	fi
	trace $ssh_pre rsync -e "ssh $SSH_OPTS" -avPz $sshalias:"/tmp/netmap/data/" $output_dir || trace $ssh_pre scp $SSH_OPTS -r $sshalias:"/tmp/netmap/data/*" $output_dir
	trace $ssh_pre ssh $SSH_OPTS $sshalias "rm -rf /tmp/netmap"
done

files_count=$(ls -1 $output_dir |wc -l)
echo "[*] DONE, hosts output in $output_dir $files_count files"

