#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
from system_files_parse import System_files_parse

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'

EXPECTED_RESULTS = {
    'network1/host_192.168.0.3_cmd_cat_etc_hosts.txt': {
        '127.0.0.1': ['cha']
    }
}

class System_files_parse_unittest(unittest.TestCase):
    def test_etc_hosts(self):
        cmdfile = "network1/host_192.168.0.3_cmd_cat_etc_hosts.txt"
        hosts = System_files_parse.etc_hosts((INPUT_DATA_DIRECTORY / cmdfile).read_text())
        self.assertEqual(EXPECTED_RESULTS[cmdfile], hosts)

if __name__ == "__main__":
    unittest.main()
