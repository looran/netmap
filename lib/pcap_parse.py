import os
import socket
from logging import info, debug, warning

try:
    import dpkt
    PCAP_PARSE_ENABLED = True
except Exception as e:
    print("warning: could not import dpkt, pcap parsing will be disabled:\n%s" % e)
    PCAP_PARSE_ENABLED = False

def find_stream(streams, src, srcport, dst, dstport, proto):
    # test if stream exists
    oneway = (src, srcport, dst, dstport, proto)
    if oneway in streams:
        return oneway
    # test if stream exists in the opposite direction
    orother = (dst, dstport, src, srcport, proto)
    if orother in streams:
        return orother
    # it did not exist, so create the stream
    streams[oneway] = { "packets": 0, "bytes": 0, "first_packet": None }
    return oneway

class Pcap_parse(object):
    @classmethod
    def parse(cls, path):
        debug("Pcap_parse %s" % path)
        if PCAP_PARSE_ENABLED is False:
            warning("pcap parsing is disabled")
            return {}
        streams = dict()
        with path.open('rb') as f:
            try: cap = dpkt.pcap.Reader(f)
            except Exception as e:
                try: cap = dpkt.pcapng.Reader(f)
                except Exception as e2:
                    warning("could not open pcap file %s :\npcap error: %s\npcapng error: %s" % (path, e, e2))
                    return {}
            n = 0
            while True:
                n += 1
                try: ts, pkt = next(cap)
                except StopIteration:
                    break
                except Exception as e:
                    warning("could not read packet %d, interrupting parse : %s\n    in %s" % (n, e, path))
                    return streams
                try: eth = dpkt.ethernet.Ethernet(pkt)
                except Exception as e:
                    warning("could not open ethernet layer from packet %d %s : %s\n    in %s" % (n, ts, e, path))
                    continue
                if not isinstance(eth.data, dpkt.ip.IP):
                    continue
                ip = eth.data
                src = socket.inet_ntoa(ip.src)
                dst = socket.inet_ntoa(ip.dst)
                transname = type(ip.data).__name__.lower()
                trans = ip.data
                if transname in ["tcp", "udp", "sctp"]:
                    sport = trans.sport
                    dport = trans.dport
                elif transname in ["icmp"]:
                    sport = dport = None
                else:
                    continue
                key = find_stream(streams, src, sport, dst, dport, transname)
                streams[key]['packets'] += 1
                streams[key]['bytes'] += int(ip.len)
                if streams[key]['first_packet'] is None:
                    streams[key]['first_packet'] = n
        return streams
