#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
import netmap

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'

EXPECTED_RESULTS = {
    'network1': {
        'summary': """== Network 'network1' summary ==
Nodes:
Node cha
   lo 00:00:00:00:00:00
      tcp/22 sshd
      127.0.0.1
      ::1
   vboxnet0 22:22:22:22:22:22
      192.168.56.1
      fe80::800:27ff:fe00:0
   enp0s31f6 55:55:55:55:55:55
      192.168.0.3
         192.168.0.3:47670 61.200.0.167:443 firefox
         192.168.0.3:57400 41.58.204.138:443 
Node 
   None None
      61.200.0.167
         192.168.0.3:47670 61.200.0.167:443 firefox
Node 
   None None
      41.58.204.138
         192.168.0.3:57400 41.58.204.138:443 
Streams:
   192.168.0.3:47670 61.200.0.167:443 firefox
   192.168.0.3:57400 41.58.204.138:443 
""",
        'map': ([
            {'category': 'node', 'isGroup': 'true', 'key': 'cha', 'text': 'cha'},
            {'category': 'node_ip', 'group': 'cha', 'key': 'cha_lo_127.0.0.1', 'text': '127.0.0.1'},
            {'category': 'node_ip', 'group': 'cha', 'key': 'cha_lo_::1', 'text': '::1'},
            {'category': 'node_ip', 'group': 'cha', 'key': 'cha_vboxnet0_192.168.56.1', 'text': '192.168.56.1'},
            {'category': 'node_ip', 'group': 'cha', 'key': 'cha_vboxnet0_fe80::800:27ff:fe00:0', 'text': 'fe80::800:27ff:fe00:0'},
            {'category': 'node_ip', 'group': 'cha', 'key': 'cha_enp0s31f6_192.168.0.3', 'text': '192.168.0.3'},
            {'category': 'node_ip', 'key': '_None_61.200.0.167', 'text': '61.200.0.167'},
            {'category': 'node_ip', 'key': '_None_41.58.204.138', 'text': '41.58.204.138'}
        ], [
            {'category': 'stream', 'color': 'rgba(200, 200, 200, 0.52)', 'font': '8pt sans-serif', 'from': 'cha_enp0s31f6_192.168.0.3', 'text': '47670:443 firefox', 'to': '_None_61.200.0.167'},
           {'category': 'stream', 'color': 'rgba(200, 200, 200, 0.52)', 'font': '8pt sans-serif', 'from': 'cha_enp0s31f6_192.168.0.3', 'text': '57400:443 ', 'to': '_None_41.58.204.138'}
        ])
    },
    'k8s_example': {
        'summary': """== Network 'k8s_example' summary ==
Nodes:
Node login login-pod-1
   lo 00:00:00:00:00:00
      127.0.0.1
      ::1
   vboxnet0 22:22:22:22:22:22
      192.168.56.1
      fe80::800:27ff:fe00:0
   enp0s31f6 55:55:55:55:55:55
      192.168.0.3
   eth0 55:55:55:55:55:55
      10.0.0.1
   login None
      TCP/8080 http-login-page
      172.16.0.1
Node login login-pod-2
   None None
      10.0.0.2
   login None
      TCP/8080 http-login-page
      172.16.0.1
Node backend backend-pod-1 dummy
   None None
      10.0.0.21
   backend None
      TCP/3306 mysql
      TCP/5000 debug
      TCP/22 
      172.16.0.2
Node backend backend-pod-2
   None None
      10.0.0.22
   backend None
      TCP/3306 mysql
      TCP/5000 debug
      TCP/22 
      172.16.0.2
Node backend
   None None
      10.0.0.23
   backend None
      TCP/3306 mysql
      TCP/5000 debug
      TCP/22 
      172.16.0.2
Streams:
""",
        'map': ([
            {"category": "node", "key": "login_login-pod-1", "isGroup": "true", "text": "login\nlogin-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_lo_127.0.0.1", "text": "127.0.0.1", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_lo_::1", "text": "::1", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_vboxnet0_192.168.56.1", "text": "192.168.56.1", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_vboxnet0_fe80::800:27ff:fe00:0", "text": "fe80::800:27ff:fe00:0", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_enp0s31f6_192.168.0.3", "text": "192.168.0.3", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_eth0_10.0.0.1", "text": "10.0.0.1", "group": "login_login-pod-1"},
            {"category": "node_ip", "key": "login_login-pod-1_login_172.16.0.1", "text": "172.16.0.1", "group": "login_login-pod-1"},
            {"category": "node", "key": "login_login-pod-2", "isGroup": "true", "text": "login\nlogin-pod-2"},
            {"category": "node_ip", "key": "login_login-pod-2_None_10.0.0.2", "text": "10.0.0.2", "group": "login_login-pod-2"},
            {"category": "node_ip", "key": "login_login-pod-2_login_172.16.0.1", "text": "172.16.0.1", "group": "login_login-pod-2"},
            {"category": "node", "key": "backend_backend-pod-1_dummy", "isGroup": "true", "text": "backend\nbackend-pod-1\ndummy"},
            {"category": "node_ip", "key": "backend_backend-pod-1_dummy_None_10.0.0.21", "text": "10.0.0.21", "group": "backend_backend-pod-1_dummy"},
            {"category": "node_ip", "key": "backend_backend-pod-1_dummy_backend_172.16.0.2", "text": "172.16.0.2", "group": "backend_backend-pod-1_dummy"},
            {"category": "node", "key": "backend_backend-pod-2", "isGroup": "true", "text": "backend\nbackend-pod-2"},
            {"category": "node_ip", "key": "backend_backend-pod-2_None_10.0.0.22", "text": "10.0.0.22", "group": "backend_backend-pod-2"},
            {"category": "node_ip", "key": "backend_backend-pod-2_backend_172.16.0.2", "text": "172.16.0.2", "group": "backend_backend-pod-2"},
            {"category": "node", "key": "backend", "isGroup": "true", "text": "backend"},
            {"category": "node_ip", "key": "backend_None_10.0.0.23", "text": "10.0.0.23", "group": "backend"},
            {"category": "node_ip", "key": "backend_backend_172.16.0.2", "text": "172.16.0.2", "group": "backend"},
        ],
        [])
    }
}


class Netmap_lib_unittest(unittest.TestCase):
    def test_network1_summary(self):
        self.maxDiff = None
        networkdir_name = "network1"
        network_dir = INPUT_DATA_DIRECTORY / networkdir_name
        nm = netmap.Netmap(network_dir)
        nm.process()
        self.assertEqual(EXPECTED_RESULTS[networkdir_name]["summary"], nm.summary())

    def test_network1_map(self):
        self.maxDiff = None
        networkdir_name = "network1"
        network_dir = INPUT_DATA_DIRECTORY / networkdir_name
        nm = netmap.Netmap(network_dir)
        nm.process()
        self.assertEqual(EXPECTED_RESULTS[networkdir_name]["map"], nm.map())

    def test_k8sexample_summary(self):
        self.maxDiff = None
        networkdir_name = "k8s_example"
        network_dir = INPUT_DATA_DIRECTORY / networkdir_name
        nm = netmap.Netmap(network_dir)
        nm.process()
        self.assertEqual(EXPECTED_RESULTS[networkdir_name]["summary"], nm.summary())

    def test_k8sexample_map(self):
        self.maxDiff = None
        networkdir_name = "k8s_example"
        network_dir = INPUT_DATA_DIRECTORY / networkdir_name
        nm = netmap.Netmap(network_dir)
        nm.process()
        import json
        Path('/tmp/test.txt').write_text(json.dumps(nm.map()))
        self.assertEqual(EXPECTED_RESULTS[networkdir_name]["map"], nm.map())

if __name__ == "__main__":
    unittest.main()
