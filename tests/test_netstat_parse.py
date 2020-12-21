#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
from netstat_parse import Netstat_parse

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'

EXPECTED_RESULTS = {
    'unit_tests/host_192.168.1.1_cmd_netstat-anp.txt': [
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '0.0.0.0:12345', 'remote': '0.0.0.0:*', 'state': 'LISTEN', 'process': '3406/toto', 'local_ip': '0.0.0.0', 'local_port': 12345, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '3406', 'process_name': 'toto'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:233', 'remote': '0.0.0.0:*', 'state': 'LISTEN', 'process': '3171/titi', 'local_ip': '127.0.0.1', 'local_port': 233, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '3171', 'process_name': 'titi'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '0.0.0.0:12346', 'remote': '0.0.0.0:*', 'state': 'LISTEN', 'process': '3405/toto', 'local_ip': '0.0.0.0', 'local_port': 12346, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '3405', 'process_name': 'toto'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '0.0.0.0:53434', 'remote': '0.0.0.0:*', 'state': 'LISTEN', 'process': '3379/toto', 'local_ip': '0.0.0.0', 'local_port': 53434, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '3379', 'process_name': 'toto'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '0.0.0.0:43922', 'remote': '0.0.0.0:*', 'state': 'LISTEN', 'process': '3039/tata', 'local_ip': '0.0.0.0', 'local_port': 43922, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '3039', 'process_name': 'tata'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:32011', 'remote': '192.168.1.2:56885', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 32011, 'remote_ip': '192.168.1.2', 'remote_port': 56885},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:52361', 'remote': '192.168.1.2:22', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 52361, 'remote_ip': '192.168.1.2', 'remote_port': 22},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:233', 'remote': '127.0.0.1:63783', 'state': 'ESTABLISHED', 'process': '3031/titi', 'local_ip': '127.0.0.1', 'local_port': 233, 'remote_ip': '127.0.0.1', 'remote_port': 63783, 'pid': '3031', 'process_name': 'titi'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:32011', 'remote': '192.168.1.2:56856', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 32011, 'remote_ip': '192.168.1.2', 'remote_port': 56856},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:233', 'remote': '127.0.0.1:63620', 'state': 'ESTABLISHED', 'process': '3031/titi', 'local_ip': '127.0.0.1', 'local_port': 233, 'remote_ip': '127.0.0.1', 'remote_port': 63620, 'pid': '3031', 'process_name': 'titi'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:32011', 'remote': '192.168.1.2:56960', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 32011, 'remote_ip': '192.168.1.2', 'remote_port': 56960},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:233', 'remote': '127.0.0.1:63622', 'state': 'ESTABLISHED', 'process': '3031/titi', 'local_ip': '127.0.0.1', 'local_port': 233, 'remote_ip': '127.0.0.1', 'remote_port': 63622, 'pid': '3031', 'process_name': 'titi'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:32011', 'remote': '192.168.1.2:56876', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 32011, 'remote_ip': '192.168.1.2', 'remote_port': 56876},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:63783', 'remote': '127.0.0.1:12345', 'state': 'ESTABLISHED', 'process': '3526/moustik', 'local_ip': '127.0.0.1', 'local_port': 63783, 'remote_ip': '127.0.0.1', 'remote_port': 12345, 'pid': '3526', 'process_name': 'moustik'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:12345', 'remote': '192.168.1.8:8888', 'state': 'ESTABLISHED', 'process': '3526/toto', 'local_ip': '192.168.1.1', 'local_port': 12345, 'remote_ip': '192.168.1.8', 'remote_port': 8888, 'pid': '3526', 'process_name': 'toto'},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.1.1:32011', 'remote': '192.168.1.2:56970', 'state': 'TIME_WAIT', 'process': '-', 'local_ip': '192.168.1.1', 'local_port': 32011, 'remote_ip': '192.168.1.2', 'remote_port': 56970},
        {'proto': 'tcp', 'recv_q': '0', 'send_q': '0', 'local': ':::22', 'remote': ':::*', 'state': 'LISTEN', 'process': '2223/sshd', 'local_ip': '::', 'local_port': 22, 'remote_ip': '::', 'remote_port': '*', 'pid': '2223', 'process_name': 'sshd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '0', 'local': '192.168.2.11:123', 'remote': '0.0.0.0:*', 'state': '', 'process': '2233/ntpd', 'local_ip': '192.168.2.11', 'local_port': 123, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '2233', 'process_name': 'ntpd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '376', 'local': '192.168.1.1:123', 'remote': '0.0.0.0:*', 'state': '', 'process': '2233/ntpd', 'local_ip': '192.168.1.1', 'local_port': 123, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '2233', 'process_name': 'ntpd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '0', 'local': '127.0.0.1:123', 'remote': '0.0.0.0:*', 'state': '', 'process': '2233/ntpd', 'local_ip': '127.0.0.1', 'local_port': 123, 'remote_ip': '0.0.0.0', 'remote_port': '*', 'pid': '2233', 'process_name': 'ntpd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '0', 'local': 'fe80::f816:3eff:fe5:123', 'remote': ':::*', 'state': '', 'process': '2233/ntpd', 'local_ip': 'fe80::f816:3eff:fe5', 'local_port': 123, 'remote_ip': '::', 'remote_port': '*', 'pid': '2233', 'process_name': 'ntpd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '0', 'local': '::1:123', 'remote': ':::*', 'state': '', 'process': '2233/ntpd', 'local_ip': '::1', 'local_port': 123, 'remote_ip': '::', 'remote_port': '*', 'pid': '2233', 'process_name': 'ntpd'},
        {'proto': 'udp', 'recv_q': '0', 'send_q': '0', 'local': ':::49240', 'remote': ':::*', 'state': '', 'process': '2584/blab', 'local_ip': '::', 'local_port': 49240, 'remote_ip': '::', 'remote_port': '*', 'pid': '2584', 'process_name': 'blab'},
        {'proto': 'raw', 'recv_q': '0', 'send_q': '1504', 'local': '0.0.0.0', 'remote': '0.0.0.0', 'state': '7', 'process': '2971/sctpd', 'pid': '2971', 'process_name': 'sctpd'},
        {'proto': 'raw', 'recv_q': '0', 'send_q': '0', 'local': '0.0.0.0', 'remote': '0.0.0.0', 'state': '7', 'process': '2971/sctpd', 'pid': '2971', 'process_name': 'sctpd'},
        {'proto': 'raw', 'recv_q': '0', 'send_q': '0', 'local': '::', 'remote': '::', 'state': '7', 'process': '2971/sctpd', 'pid': '2971', 'process_name': 'sctpd'}
    ],
}

class Netstat_parse_unittest(unittest.TestCase):
    def test_netstat_singlefile(self):
        Netstat_parse.DEBUG = False
        cmdfile = "unit_tests/host_192.168.1.1_cmd_netstat-anp.txt"
        streams = Netstat_parse.netstat(INPUT_DATA_DIRECTORY / cmdfile)
        self.assertEqual(EXPECTED_RESULTS[cmdfile], streams)

if __name__ == "__main__":
    unittest.main()
