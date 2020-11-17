#!/bin/sh

trace() { echo "# $*" >&2; "$@"; }

set -e

[ $# -lt 2 ] && echo "usage: $0 [-T] <output_directory> <this_host_ip>" && exit 1
do_tcpdump=1
[ "$1" == "-T" ] && do_tcpdump=0 && shift
out_dir="$1"
host_ip=$2

echo "[+] running commands on host $host_ip" >&2
trace hostname > $out_dir/host_${host_ip}_cmd_hostname.txt
trace ip address show > $out_dir/host_${host_ip}_cmd_ip-address-show.txt
trace sudo ss -anp > $out_dir/host_${host_ip}_cmd_ss-anp.txt
trace ip neigh show > $out_dir/host_${host_ip}_cmd_ip-neighbour-show.txt
trace cat /etc/hosts > $out_dir/host_${host_ip}_cmd_cat_etc_hosts.txt

if [ $do_tcpdump -eq 1 ]; then
    echo "[+] running network capture on host $host_ip" >&2
    trace which tcpdump
    ip -o a |awk '{print $2}' |sort |uniq |while read iface; do
        trace sudo timeout 20 tcpdump -ni ${iface} -c 5000 -w $out_dir/host_${host_ip}_pcap_${iface}.pcap ||true
    done
fi

echo "[*] DONE, host $host_ip results stored in $out_dir" >&2
