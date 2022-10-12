import re
import pprint
from logging import info, debug, warning
from collections import Counter

class Iproute2_parse(object):
    DEBUG = False

    @classmethod
    def ip_address_show(cls, fpath):
        text = fpath.read_text()
        interfaces = dict()

        current_iface = None
        for line in text.split('\n'):
            cls._debug("parse: %s" % line)
            m = re.match(r"^(?P<ifnum>[0-9]*): (?P<ifname>[a-zA-Z0-9-]*)[@]?(?P<ifname_master>[a-zA-Z0-9-]*): .*", line)
            if m:
                if current_iface:
                    interfaces[current_iface['name']] = current_iface
                current_iface = { 'name': m.group('ifname'), 'num': m.group('ifnum'), 'master': m.group('ifname_master'), 'ip': list() }
            else:
                if not current_iface:
                    print("warning: no interface found at begining of file : %s" % line)
                    continue
                m = re.match(r"^[ \t]*link/(?P<link_type>[a-z]*) (?P<link_addr>[0-9a-f.:]*) .*", line)
                if m:
                    current_iface['link_type'] = m.group('link_type')
                    current_iface['link_addr'] = m.group('link_addr')
                else:
                    m = re.match(r"^[ \t]*inet(?P<ipver>[6]?) (?P<ip>[0-9a-f.:]*)/(?P<masklen>[0-9]*) .*", line)
                    if m:
                        current_iface['ip'].append(m.group('ip'))
                    else:
                        cls._debug("could not parse line, skipping: %s" % line)
                        continue
        if current_iface:
            interfaces[current_iface['name']] = current_iface

        cls._debug(pprint.pformat(interfaces))
        return interfaces

    @classmethod
    def ip_neighbour_show(cls, fpath):
        text = fpath.read_text()
        neighbours = dict()

        for line in text.split('\n'):
            if len(line) <= 1:
                continue
            cls._debug("parse: %s" % line)
            m = re.match(r"^(?P<ip>[0-9a-f.:]+)[ \t]+dev[ \t]+(?P<ifname>[a-zA-Z0-9-]+)[ \t]+(lladdr)?[ \t]*(?P<link_addr>[0-9a-f.:]*)[ \t]*(ref)?[ \t]*(?P<ref>[0-9]*)[ \t]*(used)?[ \t]*(?P<used>[0-9/]*)[ \t]*(probes)?[ \t]*(?P<probes>[0-9]*)[ \t]*(?P<status>[A-Z]+)", line)
            if m:
                if m.group('status') not in ['FAILED']:
                    neighbours[m.group('ip')] = {'interface': m.group('ifname'), 'link_addr': m.group('link_addr'), 'status': m.group('status')}
            else:
                print("warning: could not parse line %s" % line)

        cls._debug(pprint.pformat(neighbours))
        return neighbours

    @classmethod
    def ss(cls, fpath):
        text = fpath.read_text()
        streams = list()

        for line in text.split('\n')[1:]:
            if len(line) <= 1:
                continue
            cls._debug("parse: %s" % line.strip())
            m = re.match(r"^(?P<proto>[a-z0-9-_]+)[ \t]+(?P<state>[A-Z0-9-_]+)[ \t]+(?P<recvq>[0-9]+)[ \t]+(?P<sendq>[0-9]+)[ \t]+(?P<local>[^ \t]*[: ]?[^: \t]*)[ \t]+(?P<remote>[^ \t]*[: ]?[^: \t]*)[ \t]+(?P<process>[^ \t]*)", line)
            if m:
                cls._debug(m.groups())
                s = m.groupdict()
                s['local'] = s['local'].strip()
                s['remote'] = s['remote'].strip()
                if s['proto'] in ['nl']:
                    s['local'] = s['local'].rsplit(':', 1)
                    s['remote'] = s['remote'].rsplit(':', 1)
                elif s['proto'] in ['tcp', 'udp', 'sctp']:
                    s['local_ip'], s['local_port'] = s['local'].rsplit(':', 1)
                    s['remote_ip'], s['remote_port'] = s['remote'].rsplit(':', 1)
                    s['local_ip'] = s['local_ip'].replace('[', '').replace(']', '').replace('::ffff:','')
                    if '%' in s['local_ip']:
                        s['local_ip'], s['local_iface'] = s['local_ip'].split('%')
                    s['remote_ip'] = s['remote_ip'].replace('[', '').replace(']', '').replace('::ffff:','')
                    if s['local_port'].isdigit():
                        s['local_port'] = int(s['local_port'])
                    if s['remote_port'].isdigit():
                        s['remote_port'] = int(s['remote_port'])
                elif s['proto'] in ['u_str', 'u_seq']:
                    s['local'] = s['local'].rsplit(' ', 1)
                    s['remote'] = s['remote'].rsplit(' ', 1)
                users = re.match(r'^users:\((?P<users>.*)\)$', s['process'])
                if users:
                    process_names = re.findall(r'\(\"(?P<process_name>[^\"]+)\",pid=(?P<pid>[0-9]+),fd=(?P<fd>[0-9]+)\)', users.groups()[0])
                    if len(process_names) > 0:
                        counts = dict(Counter([ i[0] for i in process_names ]))
                        s["process_name"] = ",".join([ "%s%s" % (k, "[%d]" % v if v > 1 else "") for k, v in counts.items() ])
                streams.append(s)
            else:
                print("warning: could not parse line %s" % line)

        cls._debug(pprint.pformat(streams))
        return streams


    @classmethod
    def _debug(cls, msg):
        if cls.DEBUG:
            debug("iproute2_parse debug: %s" % str(msg))
