#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
from iproute2_parse import Iproute2_parse

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'

EXPECTED_RESULTS = {
    'network1/host_192.168.0.3_cmd_ip-address-show.txt': {
        'bond0': {'ip': [], 'link_addr': '12:34:56:67:90:01', 'link_type': 'ether', 'master': '', 'name': 'bond0', 'num': '2'},
        'dummy0': {'ip': [], 'link_addr': '11:11:11:11:11:11', 'link_type': 'ether', 'master': '', 'name': 'dummy0', 'num': '3'},
        'enp0s20f0u2u1': {'ip': [], 'link_addr': '44:44:44:44:44:44', 'link_type': 'ether', 'master': '', 'name': 'enp0s20f0u2u1', 'num': '139'},
        'enp0s31f6': {'ip': ['192.168.0.3'], 'link_addr': '55:55:55:55:55:55', 'link_type': 'ether', 'master': '', 'name': 'enp0s31f6', 'num': '140'},
        'erspan0': {'ip': [], 'link_addr': '00:00:00:00:00:00', 'link_type': 'ether', 'master': 'NONE', 'name': 'erspan0', 'num': '6'},
        'gre0': {'ip': [], 'link_addr': '0.0.0.0', 'link_type': 'gre', 'master': 'NONE', 'name': 'gre0', 'num': '4'},
        'gretap0': {'ip': [], 'link_addr': '00:00:00:00:00:00', 'link_type': 'ether', 'master': 'NONE', 'name': 'gretap0', 'num': '5'},
        'lo': {'ip': ['127.0.0.1', '::1'], 'link_addr': '00:00:00:00:00:00', 'link_type': 'loopback', 'master': '', 'name': 'lo', 'num': '1'},
        'sit0': {'ip': [], 'link_addr': '0.0.0.0', 'link_type': 'sit', 'master': 'NONE', 'name': 'sit0', 'num': '7'},
        'vboxnet0': {'ip': ['192.168.56.1', 'fe80::800:27ff:fe00:0'], 'link_addr': '22:22:22:22:22:22', 'link_type': 'ether', 'master': '', 'name': 'vboxnet0', 'num': '136'},
        'vboxnet1': {'ip': [], 'link_addr': '33:33:33:33:33:33', 'link_type': 'ether', 'master': '', 'name': 'vboxnet1', 'num': '137'}
    },
    'network1/host_192.168.0.3_cmd_ip-neighbour-show.txt': {
        '192.168.0.1': {'interface': 'enp0s31f6', 'link_addr': '66:66:66:66:66:66', 'status': 'DELAY'},
        '192.168.0.2': {'interface': 'enp0s31f6', 'link_addr': '77:77:77:77:77:77', 'status': 'STALE'},
        '192.168.0.9': {'interface': 'enp0s31f6', 'link_addr': '88:88:88:88:88:88', 'status': 'REACHABLE'}
    },
    'network1/host_192.168.0.3_cmd_ss-anp.txt': [
        {'local': ['rtnl', 'chrome/22367'], 'netid': 'nl', 'process': '', 'recvq': '0', 'remote': ['*'], 'sendq': '0', 'state': 'UNCONN'},
        {'local': ['rtnl', 'kernel'], 'netid': 'nl', 'process': '', 'recvq': '0', 'remote': ['*'], 'sendq': '0', 'state': 'UNCONN'},
        {'local': ['rtnl', 'chrome/22398'], 'netid': 'nl', 'process': '', 'recvq': '0', 'remote': ['*'], 'sendq': '0', 'state': 'UNCONN'},
        {'fd': '135', 'local': ['*', '28353244'], 'netid': 'u_str', 'pid': '2721', 'process': 'users:(("chrome",pid=2721,fd=135))', 'process_name': 'chrome', 'recvq': '0', 'remote': ['*', '28353245'], 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '158', 'local': ['*', '28305372'], 'netid': 'u_str', 'pid': '18601', 'process': 'users:(("firefox",pid=18601,fd=158))', 'process_name': 'firefox', 'recvq': '0', 'remote': ['*', '28305373'], 'sendq': '0', 'state': 'ESTAB'},
        {'local': ['*', '12296314'], 'netid': 'u_str', 'process': 'users:(("Privileged', 'recvq': '0', 'remote': ['*', '12296313'], 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '36', 'local': ['@/tmp/dbus-XExEFoOIgZ', '3183505'], 'netid': 'u_str', 'pid': '3874', 'process': 'users:(("dbus-daemon",pid=3874,fd=36))', 'process_name': 'dbus-daemon', 'recvq': '0', 'remote': ['*', '3189060'], 'sendq': '0', 'state': 'ESTAB'},
        {'local': ['*', '27009941'], 'netid': 'u_seq', 'process': 'users:(("chrome",pid=32398,fd=4),("chrome",pid=31721,fd=4),("chrome",pid=31677,fd=4),("chrome",pid=31492,fd=4),("chrome",pid=31455,fd=4),("chrome",pid=31447,fd=4),("chrome",pid=31431,fd=4),("chrome",pid=31416,fd=4),("chrome",pid=31405,fd=4),("chrome",pid=31369,fd=4),("chrome",pid=31352,fd=4),("chrome",pid=31319,fd=4),("chrome",pid=29046,fd=4),("chrome",pid=28941,fd=4),("chrome",pid=28923,fd=4),("chrome",pid=28633,fd=4),("chrome",pid=28592,fd=4),("chrome",pid=28567,fd=4),("chrome",pid=28548,fd=4),("chrome",pid=28528,fd=4),("chrome",pid=28507,fd=4),("chrome",pid=27075,fd=4),("chrome",pid=26992,fd=4),("chrome",pid=26860,fd=4),("chrome",pid=26840,fd=4),("chrome",pid=26814,fd=4),("chrome",pid=24174,fd=4),("chrome",pid=24158,fd=4),("chrome",pid=23355,fd=4),("chrome",pid=23262,fd=4),("chrome",pid=22683,fd=4),("chrome",pid=22611,fd=4),("chrome",pid=22603,fd=4),("chrome",pid=22587,fd=4),("chrome",pid=22561,fd=4),("chrome",pid=22539,fd=4),("chrome",pid=22489,fd=4),("chrome",pid=22394,fd=4),("chrome",pid=22374,fd=4),("chrome",pid=22372,fd=4),("chrome-sandbox",pid=22371,fd=4),("chrome",pid=22370,fd=4),("chrome",pid=22367,fd=114),("chrome",pid=11993,fd=4),("chrome",pid=11973,fd=4),("chrome",pid=10401,fd=4),("chrome",pid=10379,fd=4),("chrome",pid=9013,fd=4),("chrome",pid=8684,fd=4),("chrome",pid=8623,fd=4),("chrome",pid=8047,fd=4),("chrome",pid=7974,fd=4),("chrome",pid=5426,fd=4),("chrome",pid=5385,fd=4),("chrome",pid=3036,fd=4),("chrome",pid=2788,fd=4),("chrome",pid=2721,fd=4),("chrome",pid=2690,fd=4),("chrome",pid=2567,fd=4),("chrome",pid=2531,fd=4),("chrome",pid=2495,fd=4),("chrome",pid=2411,fd=4),("chrome",pid=2309,fd=4),("chrome",pid=1343,fd=4),("chrome",pid=1229,fd=4),("chrome",pid=1206,fd=4))', 'recvq': '0', 'remote': ['*', '27009942'], 'sendq': '0', 'state': 'ESTAB'},
        {'local': ['*', '27014431'], 'netid': 'u_seq', 'process': 'users:(("chrome",pid=22394,fd=123),("chrome",pid=22367,fd=159))', 'recvq': '0', 'remote': ['*', '27014432'], 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '15', 'local': ['*', '2843'], 'netid': 'u_str', 'pid': '4168', 'process': 'users:(("blueman-applet",pid=4168,fd=15))', 'process_name': 'blueman-applet', 'recvq': '0', 'remote': ['*', '2842'], 'sendq': '0', 'state': 'ESTAB'},
        {'local': '0.0.0.0:32785', 'local_ip': '0.0.0.0', 'local_port': 32785, 'netid': 'udp', 'process': '', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '0', 'state': 'UNCONN'},
        {'fd': '3', 'local': '127.0.0.1:22', 'local_ip': '127.0.0.1', 'local_port': 22, 'netid': 'tcp', 'pid': '9688', 'process': 'users:(("sshd",pid=9688,fd=3))', 'process_name': 'sshd', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '0', 'state': 'LISTEN'},
        {'fd': '32', 'local': '192.168.0.3:58804', 'local_ip': '192.168.0.3', 'local_port': 58804, 'netid': 'tcp', 'pid': '18601', 'process': 'users:(("firefox",pid=18601,fd=32))', 'process_name': 'firefox', 'recvq': '0', 'remote': '192.168.1.1:443', 'remote_ip': '192.168.1.1', 'remote_port': 443, 'sendq': '1', 'state': 'SYN-SENT'},
        {'fd': '47', 'local': '192.168.0.3:47670', 'local_ip': '192.168.0.3', 'local_port': 47670, 'netid': 'tcp', 'pid': '18601', 'process': 'users:(("firefox",pid=18601,fd=47))', 'process_name': 'firefox', 'recvq': '0', 'remote': '61.200.0.167:443', 'remote_ip': '61.200.0.167', 'remote_port': 443, 'sendq': '0', 'state': 'ESTAB'},
        {'local': '192.168.0.3:57400', 'local_ip': '192.168.0.3', 'local_port': 57400, 'netid': 'tcp', 'process': '', 'recvq': '0', 'remote': '41.58.204.138:443', 'remote_ip': '41.58.204.138', 'remote_port': 443, 'sendq': '0', 'state': 'TIME-WAIT'}
    ],
    'unit_tests/host_192.168.0.1_cmd_ss-anp.txt': [
        {'fd': '5', 'local': '127.0.0.1:1031', 'local_ip': '127.0.0.1', 'local_port': 1031, 'netid': 'tcp', 'pid': '26715', 'process': 'users:(("ssh",pid=26715,fd=5))', 'process_name': 'ssh', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '128', 'state': 'LISTEN'},
        {'fd': '3', 'local': '127.0.0.1:1032', 'local_ip': '127.0.0.1', 'local_port': 1032, 'netid': 'tcp', 'pid': '5090', 'process': 'users:(("autossh",pid=5090,fd=3))', 'process_name': 'autossh', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '1', 'state': 'LISTEN'},
        {'local': '127.0.0.1:4949', 'local_ip': '127.0.0.1', 'local_port': 4949, 'netid': 'tcp', 'process': 'users:(("/usr/sbin/munin",pid=29361,fd=5),("munin-node",pid=9344,fd=5))', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '128', 'state': 'LISTEN'},
        {'fd': '13', 'local': '127.0.0.53%lo:53', 'local_ip': '127.0.0.53', 'local_iface': 'lo', 'local_port': 53, 'netid': 'tcp', 'pid': '801', 'process': 'users:(("systemd-resolve",pid=801,fd=13))', 'process_name': 'systemd-resolve', 'recvq': '0', 'remote': '0.0.0.0:*', 'remote_ip': '0.0.0.0', 'remote_port': '*', 'sendq': '128', 'state': 'LISTEN'},
        {'fd': '6', 'local': '127.0.0.1:56952', 'local_ip': '127.0.0.1', 'local_port': 56952, 'netid': 'tcp', 'pid': '26715', 'process': 'users:(("ssh",pid=26715,fd=6))', 'process_name': 'ssh', 'recvq': '59504', 'remote': '127.0.0.1:22', 'remote_ip': '127.0.0.1', 'remote_port': 22, 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '3', 'local': '192.168.0.2:22', 'local_ip': '192.168.0.2', 'local_port': 22, 'netid': 'tcp', 'pid': '29123', 'process': 'users:(("sshd",pid=29123,fd=3))', 'process_name': 'sshd', 'recvq': '0', 'remote': '192.168.0.4:37094', 'remote_ip': '192.168.0.4', 'remote_port': 37094, 'sendq': '216', 'state': 'ESTAB'},
        {'fd': '6', 'local': '127.0.0.1:1032', 'local_ip': '127.0.0.1', 'local_port': 1032, 'netid': 'tcp', 'pid': '5090', 'process': 'users:(("autossh",pid=5090,fd=6))', 'process_name': 'autossh', 'recvq': '0', 'remote': '127.0.0.1:48480', 'remote_ip': '127.0.0.1', 'remote_port': 48480, 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '5', 'local': '127.0.0.1:34566', 'local_ip': '127.0.0.1', 'local_port': 34566, 'netid': 'tcp', 'pid': '5090', 'process': 'users:(("autossh",pid=5090,fd=5))', 'process_name': 'autossh', 'recvq': '0', 'remote': '127.0.0.1:1031', 'remote_ip': '127.0.0.1', 'remote_port': 1031, 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '3', 'local': '192.168.0.2:38134', 'local_ip': '192.168.0.2', 'local_port': 38134, 'netid': 'tcp', 'pid': '19220', 'process': 'users:(("ssh",pid=19220,fd=3))', 'process_name': 'ssh', 'recvq': '0', 'remote': '192.168.0.1:22', 'remote_ip': '192.168.0.1', 'remote_port': 22, 'sendq': '0', 'state': 'ESTAB'},
        {'fd': '8', 'local': '127.0.0.1:48480', 'local_ip': '127.0.0.1', 'local_port': 48480, 'netid': 'tcp', 'pid': '26715', 'process': 'users:(("ssh",pid=26715,fd=8))', 'process_name': 'ssh', 'recvq': '0', 'remote': '127.0.0.1:1032', 'remote_ip': '127.0.0.1', 'remote_port': 1032, 'sendq': '0', 'state': 'ESTAB'},
    ],
}

class Iproute2_parse_unittest(unittest.TestCase):
    def test_ip_address_show(self):
        Iproute2_parse.DEBUG = False
        cmdfile = "network1/host_192.168.0.3_cmd_ip-address-show.txt"
        interfaces = Iproute2_parse.ip_address_show((INPUT_DATA_DIRECTORY / cmdfile).read_text())
        self.assertEqual(EXPECTED_RESULTS[cmdfile], interfaces)

    def test_ip_neighbour_show(self):
        Iproute2_parse.DEBUG = False
        cmdfile = "network1/host_192.168.0.3_cmd_ip-neighbour-show.txt"
        interfaces = Iproute2_parse.ip_neighbour_show((INPUT_DATA_DIRECTORY / cmdfile).read_text())
        self.assertEqual(EXPECTED_RESULTS[cmdfile], interfaces)

    def test_ss(self):
        self.maxDiff = None
        Iproute2_parse.DEBUG = False
        cmdfile = "network1/host_192.168.0.3_cmd_ss-anp.txt"
        streams = Iproute2_parse.ss((INPUT_DATA_DIRECTORY / cmdfile).read_text())
        self.assertEqual(EXPECTED_RESULTS[cmdfile], streams)

    def test_ss_address_with_percents(self):
        self.maxDiff = None
        Iproute2_parse.DEBUG = False
        cmdfile = "unit_tests/host_192.168.0.1_cmd_ss-anp.txt"
        streams = Iproute2_parse.ss((INPUT_DATA_DIRECTORY / cmdfile).read_text())
        self.assertEqual(EXPECTED_RESULTS[cmdfile], streams)

if __name__ == "__main__":
    unittest.main()
