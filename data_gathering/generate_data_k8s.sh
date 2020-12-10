#!/bin/bash

# generate_data_k8s.sh - get containers network informations from the kubernetes master
# this is an example script with cryptic syntax to make it as short as possible.
# it probably should not be run on production as it lacks checking of all sort.
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
SSH_NODES_CMD=${SSH_NODES_CMD:-"ssh"}
echo "SSH_NODES_CMD=$SSH_NODES_CMD"

echo "[+] running commands on all kubernetes pods"
which kubectl
kubectl get pod --all-namespaces -o jsonpath="{range .items[*]}{.metadata.namespace}{','}{.metadata.name}{','}{.status.phase}{','}{.status.podIP}{','}{.spec.nodeName}{','}{.status.hostIP}{','}{.status.containerStatuses[*]['name', 'containerID']}{'\n'}{end}" |while IFS=',' read k_namespace k_name k_status k_pod_ip k_node_name k_host_ip k_containers; do
    paste -d/ <(echo ${k_containers%%"docker"*} |tr ' ' '\n') <(echo ${k_containers#*"docker://"} |sed 's/docker:\/\///g' |tr ' ' '\n') | while IFS='/' read c_name c_id; do
        c_pid=$(trace $SSH_NODES_CMD root@$k_node_name "docker inspect -f '{{.State.Pid}}' $c_id" ||true)
        echo "[+] pod '$k_namespace $k_name' host '$k_node_name' container '$c_name' pid '$c_pid'" >&2
        [ -z "$c_pid" ] && echo "WARNING: container has disapeared from host node" >&2 && continue
        [ $c_pid -eq 0 ] && echo "WARNING: container is down" >&2 && continue
        echo "$k_name.$c_name" > $out_dir/host_${k_pod_ip}_cmd_hostname.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ip address show" > $out_dir/host_${k_pod_ip}_cmd_ip-address-show.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ss -anp" > $out_dir/host_${k_pod_ip}_cmd_ss-anp.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -t $c_pid ip neigh show" > $out_dir/host_${k_pod_ip}_cmd_ip-neighbour-show.txt
        trace $SSH_NODES_CMD root@$k_node_name "nsenter -u -p -n -m -t $c_pid /bin/cat /etc/hosts" > $out_dir/host_${k_pod_ip}_cmd_cat_etc_hosts.txt ||true # we use -m to enter filesystem mount namespace and try to find cat
        # XXX tcpdump
    done
done

echo "[+] getting services and endpoints IPs"
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
