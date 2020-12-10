#!/bin/sh

trace() { echo "# $*" >&2; "$@"; }

PATH="$PATH:/bin:/sbin:/usr/bin:/usr/sbin"
set -e

[ $# -lt 2 ] && echo "usage: $0 [-v] [-T] <output_directory> <this_host_ip>" && exit 1
redir_stderr=/dev/null
[ "$1" = "-v" ] && redir_stderr=/dev/stderr && shift
do_tcpdump=1
[ "$1" = "-T" ] && do_tcpdump=0 && shift
out_dir="$1"
host_ip=$2
now=$(date +%Y%m%d_%H%M%S)
echo "$now $host_ip $*" >> "$out_dir/generate_data_${now}_${host_ip}.log"

echo "[+] running commands on host $host_ip" >&2
trace hostname > $out_dir/host_${host_ip}_cmd_hostname.txt
trace ip address show > $out_dir/host_${host_ip}_cmd_ip-address-show.txt
trace sudo ss -anp > $out_dir/host_${host_ip}_cmd_ss-anp.txt
trace ip neigh show > $out_dir/host_${host_ip}_cmd_ip-neighbour-show.txt
trace cat /etc/hosts > $out_dir/host_${host_ip}_cmd_cat_etc_hosts.txt

if [ $do_tcpdump -eq 1 ]; then
    echo "[+] running network capture on host $host_ip" >&2
    trace which tcpdump
    ip -o a |awk '{print $2}' |sort |uniq \
        |sudo timeout 30 xargs -P0 -t -I IFACE tcpdump -ni IFACE -c 30000 -w $out_dir/host_${host_ip}_pcap_IFACE.pcap 2>$redir_stderr ||true
fi

echo "[*] DONE, host $host_ip results stored in $out_dir" >&2
