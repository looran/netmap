#!/bin/sh

trace() { echo "# $*" >&2; "$@"; }

PATH="$PATH:/bin:/sbin:/usr/bin:/usr/sbin"
TCPDUMP_TIME=${TCPDUMP_TIME:-30}
TCPDUMP_PACKETS=${TCPDUMP_PACKETS:-30000}
set -e

[ $# -lt 2 ] && echo "usage: $0 [-T] <output_directory> <this_host_ip>" && exit 1
do_tcpdump=1
[ "$1" = "-T" ] && do_tcpdump=0 && shift
out_dir="$1"
host_ip=$2
now=$(date -u +%Y%m%d_%H%M%S_%Z)
echo "$now $host_ip tcpdump=$do_tcpdump TCPDUMP_TIME=$TCPDUMP_TIME TCPDUMP_PACKETS=$TCPDUMP_PACKETS" >> "$out_dir/generate_data_${now}_${host_ip}.log"

echo "[+] running commands on host $host_ip" >&2

trace hostname > $out_dir/host_${host_ip}_cmd_hostname.txt
trace uname -ap > $out_dir/host_${host_ip}_cmd_uname-ap.txt
trace uptime > $out_dir/host_${host_ip}_cmd_uptime.txt
trace mount > $out_dir/host_${host_ip}_cmd_mount.txt
trace df -h > $out_dir/host_${host_ip}_cmd_df-h.txt
trace ps -auxww > $out_dir/host_${host_ip}_cmd_ps-auxww.txt \
        || trace ps -ef > $out_dir/host_${host_ip}_cmd_ps-ef.txt
trace ps -efH > $out_dir/host_${host_ip}_cmd_ps-efH.txt
trace top -bn1 > $out_dir/host_${host_ip}_cmd_top-bn1.txt
trace cat /etc/passwd > $out_dir/host_${host_ip}_cmd_cat_etc_passwd.txt
trace cat /etc/hosts > $out_dir/host_${host_ip}_cmd_cat_etc_hosts.txt
echo > $out_dir/host_${host_ip}_cmd_ip_netns.txt
trace ip netns >> $out_dir/host_${host_ip}_cmd_ip_netns.txt

while read -r netns; do
    suffix=""
    netns="$(echo $netns |awk '{print $1}')"
    [ -n "$netns" ] \
        && echo "namespace $netns" && suffix="_netns-$netns" && pre="sudo ip netns exec $netns " \
        || pre="sudo nsenter -n -t1 "
    trace $pre ip address show > $out_dir/host_${host_ip}_cmd_ip-address-show${suffix}.txt
    trace which ss >/dev/null \
            && trace $pre ss -anp > $out_dir/host_${host_ip}_cmd_ss-anp${suffix}.txt \
            || trace $pre netstat -anp > $out_dir/host_${host_ip}_cmd_netstat-anp${suffix}.txt
    trace ip neigh show > $out_dir/host_${host_ip}_cmd_ip-neighbour-show${suffix}.txt
    if [ $do_tcpdump -eq 1 ]; then
        $pre ip address show |grep UP |sed -n 's/^[0-9]*: \([-_a-zA-Z0-9\.]*\).*/\1/p' |sort |uniq \
            |$pre xargs -P0 -t -I IFACE timeout -s 2 $TCPDUMP_TIME tcpdump -ni IFACE -c $TCPDUMP_PACKETS -w $out_dir/host_${host_ip}_pcap_IFACE${suffix}.pcap || true &
    fi
done < $out_dir/host_${host_ip}_cmd_ip_netns.txt

[ $do_tcpdump -eq 1 ] && echo waiting for tcpdumps && trace wait || true

echo "[*] DONE, host $host_ip results stored in $out_dir" >&2
