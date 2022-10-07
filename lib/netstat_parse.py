import re
import pprint
import socket

class Netstat_parse(object):
    DEBUG = False
    PROTOCOL_TABLE = {num:name[8:] for name,num in vars(socket).items() if name.startswith("IPPROTO")}

    @classmethod
    def netstat(cls, fpath):
        text = fpath.read_text()
        streams = list()

        cls._debug("netstat %s" % fpath)
        for line in text.split('\n')[1:]:
            if len(line) <= 1:
                continue
            cls._debug("parse: %s" % line.strip())
            m = re.match(r"^(?P<proto>[0-9a-zA-Z\.\-_]+)[ ]+(?P<recv_q>[0-9]+)[ ]+(?P<send_q>[0-9]+)[ ]+(?P<local>[0-9a-f\.:\*]+)[ ]+(?P<remote>[0-9a-f\.:\*]+)[ ]+(?P<state>[A-Z0-9a-f_-]*)[ ]+(?P<process>[0-9a-zA-Z-_\/]+)[ ]*", line)
            if m:
                cls._debug(m.groups())
                s = m.groupdict()
                if s['proto'] in ['tcp', 'tcp6', 'udp', 'udp6', 'sctp']:
                    s['local_ip'], s['local_port'] = s['local'].rsplit(':', 1)
                    s['remote_ip'], s['remote_port'] = s['remote'].rsplit(':', 1)
                    if s['local_port'].isdigit():
                        s['local_port'] = int(s['local_port'])
                    if s['remote_port'].isdigit():
                        s['remote_port'] = int(s['remote_port'])
                    s['proto'] = s['proto'].replace('6', '')
                elif s['proto'] == 'raw':
                    s['local'], proto_local = s['local'].rsplit(':', 1)
                    s['remote'], _ = s['remote'].rsplit(':', 1)
                    if proto_local in cls.PROTOCOL_TABLE:
                        s['proto'] = cls.PROTOCOL_TABLE[proto_local]
                m = re.match(r'^(?P<pid>[0-9]+)/(?P<process_name>[^ ]+)', s['process'])
                if m:
                    s.update(m.groupdict())
                streams.append(s)
            else:
                if (re.match(r"^Proto", line)
                        or re.match(r"^Active UNIX domain sockets", line)
                        or re.match(r"^unix.*", line)):
                    pass # safely ignore these lines
                else:
                    print("warning: could not parse line %s" % line)

        cls._debug(pprint.pformat(streams))
        return streams


    @classmethod
    def _debug(cls, msg):
        if cls.DEBUG:
            print("iproute2_parse debug: %s" % str(msg))
