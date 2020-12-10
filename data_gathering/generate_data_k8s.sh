#!/bin/bash

# generate_data_k8s.sh - get containers network informations from the kubernetes master
# this is an example script with cryptic syntax to make it as short as possible.
# it probably should not be run on production as it lacks checking of all sort.
# if tcpdump mode is active, it will start lots of tcpdump in parallel.
# requirements:
# * 'kubectl get pod --all-namespaces' can list all pods of the k8s cluster
# * passwordless root ssh to host nodes names
#     for example you could use sshpass or specific ssh configuration file
#     in environnment variable SSH_NODES_CMD
# 2020, Laurent Ghigonis <ooookiwi@gmail.com>

trace() { echo "# $*" >&2; "$@"; }

set -e

[ $# -lt 1 -o "$1" = "-h" ] && echo "usage: $0 [-v] [-T] <output_directory> <this_host_ip>" && exit 1
do_tcpdump=1
redir_stderr=/dev/null
[ "$1" = "-v" ] && redir_stderr=/dev/stderr && shift
[ "$1" == "-T" ] && do_tcpdump=0 && shift
out_dir="$1"
host_ip="$2"
now=$(date +%Y%m%d_%H%M%S)
echo "$now $host_ip $*" >> "$out_dir/generate_data_k8s_${now}_${host_ip}.log"
SSH_NODES_CMD=${SSH_NODES_CMD:-"ssh -oControlMaster=auto -oControlPath=/tmp/netmap/ssh-master-%r@%n:%p -oControlPersist=5 -q"}
echo "SSH_NODES_CMD=$SSH_NODES_CMD" >&2

echo "[+] running commands on all kubernetes pods" >&2
which kubectl
[ $do_tcpdump -eq 1 ] && tcpdump_pids="" ||true
while IFS=',' read -r k_namespace k_name k_status k_pod_ip k_node_name k_host_ip k_containers <&3; do
    while IFS='/' read -r c_name c_id <&4; do
        c_pid=$(trace $SSH_NODES_CMD root@$k_node_name "docker inspect -f '{{.State.Pid}}' $c_id" ||true)
        echo "[+] pod '$k_namespace $k_name' host '$k_node_name' container '$c_name' pid '$c_pid' ip '$k_pod_ip'" >&2
        [ -z "$c_pid" ] && echo "WARNING: container has disapeared from host node" >&2 && continue
        [ $c_pid -eq 0 ] && echo "WARNING: container is down" >&2 && continue
        echo "$k_name.$c_name" > $out_dir/host_${k_pod_ip}_cmd_hostname.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ip address show" > $out_dir/host_${k_pod_ip}_cmd_ip-address-show.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ss -anp" > $out_dir/host_${k_pod_ip}_cmd_ss-anp.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ip neigh show" > $out_dir/host_${k_pod_ip}_cmd_ip-neighbour-show.txt
        # we use -m to enter filesystem mount namespace and try to find cat
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -m -t $c_pid /bin/cat /etc/hosts" > $out_dir/host_${k_pod_ip}_cmd_cat_etc_hosts.txt ||true
        if [ $do_tcpdump -eq 1 ]; then
            while read iface <&5; do
                trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid timeout -s 2 30 tcpdump -ni $iface -U -c 30000 -w - 2>$redir_stderr; sleep 6" > $out_dir/host_${k_pod_ip}_pcap_${iface}.pcap &
				sleep 0.3 # don't be too demanding on ssh, or connection may fail and we would end up with a corrupted PCAP
                tcpdump_pids="$tcpdump_pids $!"
            done 5< <(trace $SSH_NODES_CMD root@$k_node_name "which tcpdump >/dev/null && nsenter -u -p -n -t $c_pid ip -o a |awk '{print \$2}' |sort |uniq")
        fi
    done 4< <(paste -d/ <(echo ${k_containers%%"docker"*} |tr ' ' '\n') <(echo ${k_containers#*"docker://"} |sed 's/docker:\/\///g' |tr ' ' '\n'))
done 3< <(kubectl get pod --all-namespaces -o jsonpath="{range .items[*]}{.metadata.namespace}{','}{.metadata.name}{','}{.status.phase}{','}{.status.podIP}{','}{.spec.nodeName}{','}{.status.hostIP}{','}{.status.containerStatuses[*]['name', 'containerID']}{'\n'}{end}")

if [ $do_tcpdump -eq 1 ]; then
    sleep 1
    echo "[+] waiting for tcpdump captures to finish on all pods" >&2
    trace wait $tcpdump_pids ||true
fi

echo "[+] getting services and endpoints IPs" >&2
while read s_name s_namespace s_cluster_ip <&4; do
	echo "$s_name $s_cluster_ip"
	while read ep_ip ep_kind ep_name <&3; do
		echo "   $ep_ip $ep_kind $ep_name"
	done 3< <(kubectl get endpoints $s_name -n $s_namespace -o jsonpath="{range .subsets[0].addresses[*]}{.ip}{' '}{.targetRef.kind}{' '}{.targetRef.name}{'\n'}{end}")
	while read ep_proto ep_port ep_name <&3; do
		echo "   $ep_proto/$ep_port $ep_name"
	done 3< <(kubectl get endpoints $s_name -n $s_namespace -o jsonpath="{range .subsets[0].ports[*]}{.protocol}{' '}{.port}{' '}{.name}{'\n'}{end}")
done 4< <(kubectl get service --all-namespaces -o jsonpath="{range .items[*]}{.metadata.name} {.metadata.namespace} {.spec.clusterIP}{'\n'}{end}") |tee $out_dir/host_${host_ip}_cmd_netmap_k8s_services_list.txt >&2

echo "[*] DONE, kubernetes pods results stored in $out_dir" >&2
