import re
from collections import defaultdict

class System_files_parse(object):
    @classmethod
    def etc_hosts(cls, fpath):
        text = fpath.read_text()
        hosts = defaultdict(list)
        for line in text.split('\n'):
            m = re.match(r"^(?P<ip>[0-9a-f.:]+)[ \t]+(?P<names>.*)", line)
            if m:
                for name in m.group('names').split(' '):
                    if len(name) > 0 and not re.match(r'.*localhost.*', name):
                        hosts[m.group('ip')].append(name)
        return hosts
