import re
from collections import defaultdict

class K8s_parse(object):
    @classmethod
    def netmap_service_list(cls, text):
        services = list()

        current_service = None
        for line_n, line in enumerate(text.split('\n'), 1):
            if len(line) == 0:
                continue
            m = re.match(r"^(?P<service_name>[0-9a-zA-Z\.\-_]+) (?P<service_ip>([0-9a-f:\.]+|None))", line)
            if m:
                if current_service:
                    services.append(current_service)
                service_ip = m.group('service_ip') if m.group('service_ip') != 'None' else None
                current_service = {
                    "service_name": m.group('service_name'),
                    "service_ip": service_ip,
                    "service_pods": list(),
                    "service_ports": list(),
                }
            else:
                m = re.match(r"^   (?P<pod_ip>[0-9a-f:\.]+)( Pod )?(?P<pod_name>.*)", line)
                if m:
                    if not current_service:
                        cls._warn("line %s: found pod information while not in service context, skipping : %s" % (line_n, line))
                        continue
                    pod_name = m.group('pod_name') if len(m.group('pod_name')) > 0 else None
                    current_service["service_pods"].append([m.group('pod_ip'), pod_name])
                else:
                    m = re.match(r"^   (?P<proto>[A-Z]+)/(?P<port>[0-9]+)( )?(?P<name>.*)", line)
                    if m:
                        if not current_service:
                            cls._warn("line %s: found port information while not in service context, skipping : %s" % (line_n, line))
                            continue
                        port_name = m.group('name') if len(m.group('name')) > 0 else None
                        current_service["service_ports"].append([m.group('proto'), m.group('port'), port_name])
                    else:
                        cls._warn("line %d: could not parse, skipping: %s" % (line_n, line))
                
        if current_service:
            services.append(current_service)

        return services

    @classmethod
    def _warn(cls, message):
        print("WARNING K8s_parse: %s" % message)
