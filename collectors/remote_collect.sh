#!/bin/bash

usageexit() {
    cat <<-_EOF
usage: $0 [-P] [-v] [-T] <output_directory> <ip|sshalias>[:k8s][:ssh_pre="SSH-CMD-PREFIX"][:tmp_dir="$TMP_DIR"] ...
   -p : enable parallel collecting when multiple targets are specified
   -v : passed to generate_data.sh
   -T : passed to generate_data.sh
target options:
   k8s : use kubernetes-specific collector script for this target
   ssh_pre : prefix ssh connection with the given command for this target
   tmp_dir : use given temporary directory for this target
environment variables:
   SSH_OPTS : options to pass to ssh to reach remote target
_EOF
    exit 1
}

trace() { echo "# $*"; "$@"; }
D="$(dirname $0)"
SSH_OPTS=${SSH_OPTS:-""}
TMP_DIR=${TMP_DIR:-"/tmp"}

collect() {
	sshalias=$(echo $remote_host |cut -d: -f1)
	ip=$sshalias
	k8s=0
	ssh_pre=""
    tmp_dir="$TMP_DIR"
	while read opt; do
		case $opt in
			k8s) k8s=1; ;;
			ssh_pre*) ssh_pre="$(echo $opt |cut -d= -f2-)"; ;;
			tmp_dir*) tmp_dir="$(echo $opt |cut -d= -f2-)"; ;;
		esac
	done < <(echo $remote_host |cut -d: -f2- |tr ':' '\n')
	echo "[+] collecting data from $sshalias ($ip) ssh_pre='$ssh_pre' k8s=$k8s"
	trace $ssh_pre ssh $SSH_OPTS $sshalias "mkdir -p $tmp_dir/netmap/data"
	trace $ssh_pre scp $SSH_OPTS $D/generate_data.sh $sshalias:$tmp_dir/netmap/
	trace $ssh_pre ssh -t $SSH_OPTS $sshalias "TCPDUMP_TIME=$TCPDUMP_TIME TCPDUMP_PACKETS=$TCPDUMP_PACKETS $tmp_dir/netmap/generate_data.sh $gendata_opts $tmp_dir/netmap/data $ip"
	if [ $k8s -eq 1 ]; then
		trace $ssh_pre scp $SSH_OPTS $D/generate_data_k8s.sh $sshalias:$tmp_dir/netmap/
		trace $ssh_pre ssh -t $SSH_OPTS $sshalias "SSH_NODES_CMD="$SSH_NODES_CMD" TCPDUMP_TIME=$TCPDUMP_TIME TCPDUMP_PACKETS=$TCPDUMP_PACKETS $tmp_dir/netmap/generate_data_k8s.sh $gendata_opts $tmp_dir/netmap/data $ip"
	fi
	trace $ssh_pre rsync -e "ssh $SSH_OPTS" -avPz $sshalias:"$tmp_dir/netmap/data/" $output_dir || trace $ssh_pre scp $SSH_OPTS -r $sshalias:"$tmp_dir/netmap/data/*" $output_dir
	trace $ssh_pre ssh $SSH_OPTS $sshalias "rm -rf $tmp_dir/netmap"
}

set -e

[ $# -lt 2 ] && usageexit
parallel=0
gendata_opts=""
[ "$1" = "-p" ] && parallel=1 && shift
[ "$1" = "-v" ] && gendata_opts="$gendata_opts -v" && shift
[ "$1" = "-T" ] && gendata_opts="$gendata_opts -T" && shift
output_dir="$1" && shift
trace mkdir -p "$output_dir"
now=$(date -u +%Y%m%d_%H%M%S_%Z)
echo "$now $(whoami)@$(hostname) remote $* SSH_OPTS=$SSH_OPTS" >> "$output_dir/remote_generate_data_${now}.log"
echo "SSH_OPTS='$SSH_OPTS'"

for remote_host in "$@"; do
    if [ $parallel -eq 1 ]; then
        collect &
    else
        collect
    fi
done

[ $parallel -eq 1 ] \
    && echo wait for data collection to finish on multiple targets \
    && trace wait

files_count=$(ls -1 $output_dir |wc -l)
echo "[*] DONE, hosts output in $output_dir $files_count files"

