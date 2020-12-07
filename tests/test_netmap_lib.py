#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
import netmap

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'
print("INPUT_DATA_DIRECTORY = %s" % INPUT_DATA_DIRECTORY)

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

== Statistics ==
{'parsed_command_output': 3, 'parsed_pcaps': 0, 'last_modification': '20201117_190845', 'nodes_count': 3, 'streams_count': 2}"""
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

if __name__ == "__main__":
    unittest.main()
