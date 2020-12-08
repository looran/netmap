import re
import time
import logging
from pathlib import Path
from logging import info, debug, warning
from collections import defaultdict, Counter

from iproute2_parse import Iproute2_parse
from system_files_parse import System_files_parse
from k8s_parse import K8s_parse
from anonymize import Anonymize

PROGRAM_VERSION = '0.1'
PROGRAM_HEADER = 'netmap v%s' % PROGRAM_VERSION

class Node(object):
    def __init__(self):
        self.node_ifaces = dict()   # { 'ifname': Node_iface, ... }
        self.names = set()         # [ name, ... ]
        self.found_in = list()      # [ <reference_to_source>, ... ]

    def find_node_ip(self, ip):
        for node_iface in self.node_ifaces.values():
            if ip in node_iface.node_ips:
                return node_iface.node_ips[ip]
        return None

    def add_or_update_ip(self, ip, ifname, mac=None):
        debug("add_or_udpate_ip node='%s' ip=%s ifname=%s" % (self.names, ip, ifname))
        node_ip = self.find_node_ip(ip)
        if node_ip:
            node_iface = node_ip.node_iface
        else:
            if ifname in self.node_ifaces:
                node_iface = self.node_ifaces[ifname]
            else:
                node_iface = Node_iface(self, ifname, mac)
                self.node_ifaces[ifname] = node_iface
            node_ip = Node_ip(node_iface, ip)
            node_iface.node_ips[ip] = node_ip
        if ifname and ifname != node_iface.name and node_iface.name in [None, 'any']: # rename interface to correct name
            self.rename_iface(node_iface, ifname)
        if mac:
            node_iface.mac = mac
        return node_ip

    def find_or_create_iface(self, ifname, mac=None):
        if ifname in self.node_ifaces:
            return self.node_ifaces[ifname]
        node_iface = Node_iface(self, ifname, mac)
        self.node_ifaces[ifname] = node_iface
        return node_iface

    def list_node_ips(self):
        node_ips = list()
        for node_iface in self.node_ifaces.values():
            for node_ip in node_iface.node_ips.values():
                node_ips.append(node_ip)
        return node_ips

    def copy_from(self, othernode):
        for otheriface in othernode.node_ifaces.values():
            if otheriface.name in self.node_ifaces:
                self.node_ifaces[otheriface.name].copy_from(otheriface)
            else:
                self.node_ifaces[otheriface.name] = otheriface
        self.names = self.names.union(othernode.names)

    def rename_iface(self, node_iface, ifname):
        debug("node renaming iface from %s to %s:\n%s" % (node_iface.name, ifname, self.to_str()))
        if ifname in self.node_ifaces:
            debug("node renaming ifname=%s already exists, copying iface content" % ifname)
            self.node_ifaces[ifname].copy_from(node_iface)
            self.node_ifaces.pop(node_iface.name)
        else:
            debug("node renaming iface=%s does not exist, direct renaming" % ifname)
            self.node_ifaces[ifname] = self.node_ifaces.pop(node_iface.name)
            self.node_ifaces[ifname].name = ifname

    def anonymize(self, anon):
        self.names = set([anon.text(x) for x in self.names])
        node_ifaces = dict()
        for ifacename, iface in self.node_ifaces.items():
            iface.anonymize(anon)
            node_ifaces[iface.name] = iface
        self.node_ifaces = node_ifaces

    def to_str(self):
        s = "Node %s\n" % self.names
        for ifname, iface in self.node_ifaces.items():
            s += "iface: %s:\n%s" % (ifname, iface.to_str())
        return s

class Node_iface(object):
    def __init__(self, node, name=None, mac=None):
        self.node = node            # Node
        self.node_ips = dict()      # { <ip>: Node_ip, ... }
        self.name = name            # str
        self.mac = mac              # str
        self.services = dict()      # { (<proto>, <port>): Service, ... }
        self.neighbours = dict()    # { <ip>: Node_ip, ... }

    def add_or_update_service(self, proto, port, name):
        port = int(port)
        if (proto, port) in self.services:
            service = self.services[(proto, port)]
            if name:
                service.names.add(name)
        else:
            service = Service(self, proto, port, name)
            self.services[(proto, port)] = service

    def copy_from(self, node_iface):
        for node_ip in node_iface.node_ips.values():
            if node_ip.ip not in self.node_ips:
                self.node_ips[node_ip.ip] = node_ip
        if self.mac is None and node_iface.mac:
            self.mac = node_iface.mac
        for service in node_iface.services.values():
            if (service.proto, service.port) not in self.services:
                self.services[(service.proto, service.port)] = service
        for node_ip in node_iface.neighbours.values():
            if node_ip.ip not in self.neighbours:
                self.neighbours[node_ip.ip] = node_ip

    def anonymize(self, anon):
        if self.name not in ['lo']:
            if self.name:
                self.name = anon.text(self.name)
            if self.mac:
                self.mac = anon.mac(self.mac)
        node_ips = dict()
        for nodeip in self.node_ips.values():
            nodeip.anonymize(anon)
            node_ips[nodeip.ip] = nodeip
        self.node_ips = node_ips
        services = dict()
        for service in self.services.values():
            service.anonymize(anon)
            services[(anon.text(service.proto), anon.int(service.port))] = service
        self.services = services
        neighbours = dict()
        for neighbour in self.neighbours.values():
            neighbour.anonymize(anon)
            neighbours[neighbour.ip] = neighbour
        self.neighbours = neighbours

    def to_str(self):
        s = "Node_iface %s\n" % self.name
        for nodeip in self.node_ips.values():
            s += "ip: %s\n" % nodeip.ip
        return s

class Node_ip(object):
    def __init__(self, node_iface, ip):
        debug("Node_ip node_iface=%s ip=%s" % (node_iface.name, ip))
        self.node_iface = node_iface # Node_iface
        self.ip = ip                # str
        self.streams = list()       # [ Stream, ... ]
        self.anonymized = False     # Node_ips are referenced in multiple places so we need a way to ensure anonymizing them only once

    def get_id(self):
        return "%s_%s_%s" % ('_'.join(sorted(self.node_iface.node.names)), self.node_iface.name, self.ip)

    def anonymize(self, anon):
        if self.anonymized is False and self.ip not in ['127.0.0.1', '::1']:
            self.ip = anon.ip(self.ip)
            self.anonymized = True

class Service(object):
    def __init__(self, node_iface, proto, port, name=""):
        self.node_iface = node_iface # Node_iface
        self.proto = proto      # str
        self.port = port        # int
        self.names = set()       # [ name, ... ]
        if name and name != "":
            self.names.add(name)

    def anonymize(self, anon):
        self.proto = anon.text(self.proto)
        self.port = anon.int(self.port)
        self.names = set([anon.text(x) for x in self.names])

class Stream(object):
    def __init__(self, src_node_ip, src_port, dst_node_ip, dst_port):
        self.src_node_ip = src_node_ip  # Node_ip
        self.src_port = src_port        # int
        self.dst_node_ip = dst_node_ip  # Node_ip
        self.dst_port = dst_port        # int
        self.dst_service = None         # Service
        self.name = ""                  # str
        self.found_in = list()          # [ <reference_to_source>, ... ]

    def anonymize(self, anon):
        self.src_port = anon.int(self.src_port)
        self.dst_port = anon.int(self.dst_port)
        if self.dst_service:
            self.dst_service.anonymize(anon)
        self.name = anon.text(self.name)

class Network(object):
    def __init__(self, network_name):
        self.network_name = network_name
        self.nodes = list()     # [ Node, ... ]
        self.streams = list()   # [ Stream, ... ]

    def find_node(self, ip):
        node_ip = self.find_node_ip(ip)
        if node_ip:
            return node_ip.node_iface.node
        return None

    def find_node_ip(self, ip):
        for node in self.nodes:
            for node_iface in node.node_ifaces.values():
                if ip in node_iface.node_ips:
                    return node_iface.node_ips[ip]
        return None

    def create_node_ip(self, ip, iface=None, mac=None):
        node = Node()
        node_ip = node.add_or_update_ip(ip, iface, mac)
        self.nodes.append(node)
        return node_ip

    def find_or_create_node_ip(self, ip, iface=None, mac=None):
        node_ip = self.find_node_ip(ip)
        if not node_ip:
            node_ip = self.create_node_ip(ip, iface, mac)
        return node_ip

    def find_or_create_stream(self, src_node_ip, src_port, dst_node_ip, dst_port):
        for stream in self.streams:
            if ((src_node_ip == stream.src_node_ip and src_port == stream.src_port
                    and dst_node_ip == stream.dst_node_ip and dst_port == stream.dst_port)
                 or
                (src_node_ip == stream.dst_node_ip and src_port == stream.dst_port
                    and dst_node_ip == stream.src_node_ip and dst_port == stream.src_port)):
                return stream
        stream = Stream(src_node_ip, src_port, dst_node_ip, dst_port)
        self.streams.append(stream)
        return stream

    def delete_node(self, node):
        self.nodes.remove(node)
        del(node)

    def anonymize(self, anon):
        self.network_name = anon.text(self.network_name)
        for node in self.nodes:
            node.anonymize(anon)
        for stream in self.streams:
            stream.anonymize(anon)

    def to_str(self):
        s = "== Network '%s' summary ==\n" % self.network_name
        s += "Nodes:\n"
        for node in self.nodes:
            s += "Node %s\n" % ' '.join(sorted(node.names))
            for node_iface in node.node_ifaces.values():
                s += "   %s %s\n" % (node_iface.name, node_iface.mac)
                for service in node_iface.services.values():
                    s += "      %s/%s %s\n" % (service.proto, service.port, ','.join(sorted(service.names)))
                for node_ip in node_iface.node_ips.values():
                    s += "      %s\n" % node_ip.ip
                    for stream in node_ip.streams:
                        s += "         %s:%s %s:%s %s\n" % (stream.src_node_ip.ip, stream.src_port, stream.dst_node_ip.ip, stream.dst_port, stream.name)
                if len(node_iface.neighbours) > 0:
                    s += "      Neighbours\n"
                    for neigh_ip in node_iface.neighbours.keys():
                        s += "         %s\n" % neigh_ip
        s += "Streams:\n"
        for stream in self.streams:
            s += "   %s:%s %s:%s %s\n" % (stream.src_node_ip.ip, stream.src_port, stream.dst_node_ip.ip, stream.dst_port, stream.name)
        return s

    def to_map(self):
        def peers_streams_reduce(peers_streams):
            for i in [0, 1]:
                new = defaultdict(list)
                rig = Counter(list(zip(*peers_streams.keys()))[i])
                for r, count in rig.items():
                    for ports, names in peers_streams.items():
                        if ports[i] == r:
                            p = list(ports)
                            if count > 1:
                                p[i^1] = '*'
                            new[tuple(p)].extend(names)
                peers_streams = new
            return peers_streams
        map_nodes = list()
        map_links = list()
        streams = defaultdict(lambda: defaultdict(lambda: defaultdict(set))) # { <srcip>: { <dstip>: { [<srcport>, <dstport>]: [ stream, ... ] } } }
        for node in self.nodes:
            if len(node.names) > 0:
                node_name = '\n'.join(sorted(node.names))
                node_key = '_'.join(sorted(node.names))
            elif len(node.list_node_ips()) > 1:
                node_name = 'node ' + ' '.join([node_ip.ip for node_ip in node.list_node_ips()])
                node_key = 'node_' + ''.join([node_ip.ip for node_ip in node.list_node_ips()])
            else:
                node_name = None
                node_key = None
            if node_name:
                map_nodes.append({
                    "category": "node",
                    "key": node_key,
                    "isGroup": "true",
                    "text": node_name,
                })
            for node_iface in node.node_ifaces.values():
                for node_ip in node_iface.node_ips.values():
                    mapnode = {
                        "category": "node_ip",
                        "key": node_ip.get_id(),
                        "text": node_ip.ip,
                    }
                    if node_key:
                        mapnode['group'] = node_key
                    map_nodes.append(mapnode)
                    for stream in node_ip.streams:
                        streams[stream.src_node_ip][stream.dst_node_ip][(stream.src_port, stream.dst_port)].add(stream.name)
                if len(node_iface.node_ips) > 0:
                    for neigh_ip in node_iface.neighbours.values():
                        map_links.append({
                            "category": "neighbour",
                            "from": list(node_iface.node_ips.values())[0].ip,
                            "to": neigh_ip.ip,
                            "text": "%s" % (node_iface.name),
                            "color": "lightgrey",
                        })
        for srcip, dstips in streams.items():
            for dstip, peers_streams in dstips.items():
                peers_streams = peers_streams_reduce(peers_streams)
                for ports, names in peers_streams.items():
                    if len(names) > 1:
                        names = "x%d %s" % (len(names), ' '.join(set(names)))
                    else:
                        names = ' '.join(names)
                    text = "%s:%s %s" % (ports[0], ports[1], names)
                    map_links.append({
                        "category": "stream",
                        "from": srcip.get_id(),
                        "to": dstip.get_id(),
                        "text": text,
                        "color": "rgba(200, 200, 200, 0.52)",
                        "font": "8pt sans-serif",
                    })
        return map_nodes, map_links

class Netmap(object):
    def __init__(self, network_dir, anonymize_hex_salt=None, debugval=False):
        self.network_dir = network_dir
        if anonymize_hex_salt:
            self.anonymizer = Anonymize(anonymize_hex_salt)
        else:
            self.anonymizer = None
        logging.basicConfig(level=logging.INFO if debugval == 0 else logging.DEBUG, format="%(levelname)s %(message)s")
        if debugval >= 2:
            Iproute2_parse.DEBUG = True
        debug("network data directory: %s" % self.network_dir)
        if not self.network_dir.exists():
            raise Exception("network data directory does not exist : %s" % self.network_dir)
        self.network = Network(network_dir.name)
        self.stats = {"parsed_input_file":0, "last_modification": 0}

    def process(self):
        FILES_ORDER = [
            ("cmd", "ip-address-show", None,            self._process_cmd_ip_address_show),
            ("cmd", "ip-route-show", None,              self._process_cmd_ip_route_show),
            ("cmd", "hostname", None,                   self._process_cmd_hostname),
            ("cmd", "cat_etc_hosts", None,              self._process_cmd_cat_etc_hosts),
            ("cmd", "ip-neighbour-show", None,          self._process_cmd_ip_neighbour_show),
            ("cmd", "netmap_k8s_services_list", None,   self._process_cmd_netmap_k8s_services_list),
            ("cmd", "ss-anp", None,                     self._process_cmd_ss_anp),
            ("pcap", "*", "(?P<ip>[0-9.]*)",            self._process_pcap),
        ]
        for fcat, ftype, fargs, fprocess in FILES_ORDER:
            for fpath in self.network_dir.glob('host_*_%s_%s.txt' % (fcat, ftype)):
                fmatch = re.match(r"host_(?P<ip>[0-9.]*)_%s_%s.txt" % (fcat, ftype if fargs is None else fargs), fpath.name)
                if not fmatch:
                    warning("ignored file because host ip is not recognised : %s" % fpath)
                    continue
                if fpath.stat().st_mtime > self.stats["last_modification"]:
                    self.stats["last_modification"] = fpath.stat().st_mtime
                debug("parsing input cmd file %s : %s" % (fpath, fmatch.groups()))
                node_ip = self.network.find_or_create_node_ip(fmatch.group('ip'))
                node_iface = node_ip.node_iface
                node = node_iface.node
                if fprocess(fpath, fmatch, node_ip, node_iface, node):
                    self.stats["parsed_input_file"] += 1
        self.stats["nodes_count"] = len(self.network.nodes)
        self.stats["streams_count"] = len(self.network.streams)
        self.stats["last_modification"] = time.strftime("%Y%m%d_%H%M%S", time.gmtime(self.stats["last_modification"]))
        if self.anonymizer:
            self.network.anonymize(self.anonymizer)
            self.stats["data_gathering_logs"] = ""
        else:
            self.stats["data_gathering_logs"] = ''.join(sorted(["%s" % (f.read_text()) for f in self.network_dir.glob('*.log')]))

    def summary(self):
        return self.network.to_str()

    def statistics(self):
        return "== Statistics ==\n%s" % self.stats

    def map(self):
        nodes, links = self.network.to_map()
        return nodes, links

    def _process_cmd_ip_address_show(self, fpath, fmatch, node_ip, node_iface, node):
        for iface in Iproute2_parse.ip_address_show(fpath.read_text()).values():
            for ip in iface['ip']:
                othernode_ip = self.network.find_node_ip(ip)
                if othernode_ip and othernode_ip.node_iface.node != node and not othernode_ip.node_iface.name:
                    # another node_ip already exists with same ip and has not been identified from a host system yet (no iface name)
                    # lets integrate it to current node
                    debug("ip '%s' trigger '%s' copy_from '%s'/'%s'" % (ip, node.names, othernode_ip.node_iface.node.names, othernode_ip.node_iface.name))
                    node.copy_from(othernode_ip.node_iface.node)
                    self.network.delete_node(othernode_ip.node_iface.node)
                linkaddr = iface['link_addr'] if 'link_addr' in iface else None
                dbgnodeip = node.add_or_update_ip(ip, iface['name'], linkaddr)
        return True
        
    def _process_cmd_ip_route_show(self, fpath, fmatch, node_ip, node_iface, node):
        warning("ip-route-show parsing is not yet supported %s" % fpath.name)
        return False

    def _process_cmd_hostname(self, fpath, fmatch, node_ip, node_iface, node):
        hostname = fpath.read_text().strip()
        node.names.add(hostname)
        return True

    def _process_cmd_cat_etc_hosts(self, fpath, fmatch, node_ip, node_iface, node):
        for ip, names in System_files_parse.etc_hosts(fpath.read_text()).items():
            if ip == '127.0.0.1' or self.network.find_node(ip) == node:
                node.names.update(set(names))
        return True

    def _process_cmd_ip_neighbour_show(self, fpath, fmatch, node_ip, node_iface, node):
        # 20201110_1711 LG disable neighbours for now, until we have a way to make them less visible
        #for neigh_ip, neigh_infos in Iproute2_parse.ip_neighbour_show(fpath.read_text()).items():
        #    neigh_node_ip = self.network.find_or_create_node_ip(neigh_ip)
        #    node_ip.node_iface.neighbours[neigh_ip] = neigh_node_ip
        return False

    def _process_cmd_netmap_k8s_services_list(self, fpath, fmatch, node_ip, node_iface, node):
        for ks in K8s_parse.netmap_service_list(fpath.read_text()):
            debug("_process_cmd_netmap_k8s_services_list: %s" % ks)
            for pod_ip, pod_name in ks['service_pods']:
                pod_node_ip = self.network.find_or_create_node_ip(pod_ip)
                pod_node = pod_node_ip.node_iface.node
                if pod_name:
                    pod_node.names.add(pod_name)
                if ks['service_name']:
                    pod_node.names.add(ks['service_name'])
                if ks['service_ip']:
                    service_node_ip = pod_node.add_or_update_ip(ks['service_ip'], ks['service_name'])
                    for port_proto, port_number, port_name in ks['service_ports']:
                        service_node_ip.node_iface.add_or_update_service(port_proto, port_number, port_name)
        return True

    def _process_cmd_ss_anp(self, fpath, fmatch, node_ip, node_iface, node):
        for sst in Iproute2_parse.ss(fpath.read_text()):
            if sst['netid'] in ['tcp', 'udp', 'sctp']:
                if sst['state'] == 'LISTEN':
                    if sst['local_ip'] in ['0.0.0.0', '::', '*']:
                        iface = node.find_or_create_iface('any')
                    else:
                        if 'local_iface' in sst: # if iface is explicitely specified, deamon might be binded on different ip
                            nip = node.add_or_update_ip(sst['local_ip'], sst['local_iface'])
                        else:
                            nip = node.find_node_ip(sst['local_ip'])
                            if not nip:
                                raise Exception("Interface not found for ip %s : %s" % (sst['local_ip'], str(sst)))
                        iface = nip.node_iface
                    if (sst['netid'], sst['local_port']) not in iface.services:
                        iface.add_or_update_service(sst['netid'], sst['local_port'], sst['process_name'] if 'process_name' in sst else "")
                elif sst['state'] in ['ESTAB', 'TIME-WAIT', 'CLOSE-WAIT', 'FIN-WAIT2']:
                    local_node_ip = self.network.find_or_create_node_ip(sst['local_ip'])
                    remote_node_ip = self.network.find_or_create_node_ip(sst['remote_ip'])
                    stream = self.network.find_or_create_stream(
                            local_node_ip, sst['local_port'], remote_node_ip, sst['remote_port'])
                    if stream not in local_node_ip.streams:
                        local_node_ip.streams.append(stream)
                    if stream not in remote_node_ip.streams:
                        remote_node_ip.streams.append(stream)
                    if 'process_name' in sst:
                        stream.name = sst['process_name']
        return True

    def _process_pcap(self, fpath, fmatch, node_ip, node_iface, node):
        warning("pcap parsing is not yet supported %s" % fpath.name)
        return False
