# netmap - network mapping from system commands output and pcap traces

netmap generates text analysis and interactive graphical map of a network from system commands output and pcap traces from multiple nodes.

Features:
* Input from simple text files system commands output and standard network pcap traces
* Text output analysis gives a quick overview of nodes and network streams
* Graphical map output showing network nodes helps understand visually the architecture of a network
* Interactivity of the map allows to place network nodes manually in a fashion where it makes best sense for understanding
* Network streams between nodes show application-level communications

Compatibility
* On monitored machines
	* Linux with iproute2 installed, optionally tcpdump
	* Supports Kubernetes pods, executes commands from the master in all pods, see `data_gathering/generate_data_k8s.sh`
* On visualisation machine
	* python3 and python3-flask

### Usage

1. Create a directory for the network data, like `mkdir -p netmap_data/mynetwork/`
2. Gather commands output and pcap traces from the nodes in your network
	1. On the local node, here 192.168.0.1: `./data_gathering/generate_data.sh netmap_data/mynetwork/ 192.168.0.1`
	2. From remote notes: `./data_gathering/remote_generate_data.sh netmap_data/mynetwork/ 192.168.0.250 10.10.10.1`
	3. You can also gather gata from your own scripts and store the result to `netmap_data/mynetwork/` following [#Data input format] naming.
3. Run `./netmap_cli.py netmap_data/ mynetwork` to have an overview of the gathered data
4. Run `./webserver.sh netmap_data/` and connect to http://127.0.0.1:5000/ to view the network map

For demo purposes you can run `./webserver.sh ./demo_data/` and it will read dummy network data from demo_data/ directory.

### Source code layout

``` bash
netmap_cli.py [options] <input_data_directory> [<network_name>]
	generate text output analysis about the network
webserver.sh <input_data_directory>
	start the webserver to generate an interactive graphical map of the network
data_gathering/
	example scripts for data gathering on local and remote hosts
demo_data/
	dummy system commands output and pcap traces for demo purposes
flask/
	webapp for network map visualisation
lib/
	network data processing libraries
test/
	unit tests for processing commands output and pcaps
```

### Data input format

netmap takes as input a directory containing the network data to analyse, each network in it's own directory.

A network directory can contain 2 types of files:
* system commands output such as `ip address show`, `ss -anp` or `cat /etc/hosts`
* network captures made by `tcpdump` for example

#### Files naming interpreted by netmap

``` bash
network1/
network1/host_<host_ip>_cmd_ip-address-show.txt
network1/host_<host_ip>_cmd_ip-neighbour-show.txt
network1/host_<host_ip>_cmd_ss-anp.txt
network1/host_<host_ip>_cmd_etc_hosts.txt
network1/host_<host_ip>_pcap_<interface>.pcap
```

### Interactive network map

The network map is generated from commands output files and network traces files from the `input_data_directory`.

Refreshing the web page will give you an up-to-date map from the current data. A cache file is generated and used if the `input_data_directory` has not been modified.

You can export the graph to PNG or SVG by clicking the "Download" buttons on the web interface.

See help at the bottom of the network map web page.

### Example manual data gathering

On host 192.168.0.1:

``` bash
$ ip address show > host_192.168.0.1_cmd_ip-address-show.txt
$ sudo ss -anp > host_192.168.0.1_cmd_ss-anp.txt
$ ip neighbour show > host_192.168.0.1_cmd_ip-neighbour-show.txt
$ cat /etc/hosts > host_192.168.0.1_cmd_cat_etc_hosts.txt
$ sudo tcpdump -ni enp0s31f6 -c 100 -w host_192.168.0.1_pcap_enp0s31f6.pcap
```

### Unit tests

Parsing some `ip` command output is part of unittests.

``` bash
make tests
```

### TODO

* implement pcap import
* color link label background depending on port, choose color dynamically
* k8s: re-verify that we don't miss containers
* maybe when highlight node make the other nodes/links almost transparent
