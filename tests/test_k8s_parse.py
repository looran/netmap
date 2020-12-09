#!/usr/bin/env python3

# run only one test:
# python -m unittest test_netfoot.Netfoot_log_unittest.test_infos_lookup

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / 'lib'))
from k8s_parse import K8s_parse

INPUT_DATA_DIRECTORY = Path(__file__).resolve().parent.parent / 'demo_data'

EXPECTED_RESULTS = {
    'k8s_example/host_192.168.0.3_cmd_netmap_k8s_services_list.txt': [
        {
            "service_name": 'login',
            "service_ip": '172.16.0.1',
            "service_pods": [ [ '10.0.0.1', 'login-pod-1' ], [ '10.0.0.2', 'login-pod-2' ], ],
            "service_ports": [ [ 'TCP', '8080', 'http-login-page' ], ],
        },
        {
            "service_name": 'backend',
            "service_ip": '172.16.0.2',
            "service_pods": [ [ '10.0.0.21', 'backend-pod-1' ], [ '10.0.0.22', 'backend-pod-2' ], [ '10.0.0.23', None], ],
            "service_ports": [ [ 'TCP', '3306', 'mysql' ], [ 'TCP', '5000', 'debug' ], [ 'TCP', '22', None], ],
        },
        {
            "service_name": 'dummy',
            "service_ip": None,
            "service_pods": [ [ '10.0.0.21', 'backend-pod-1' ], ],
            "service_ports": [ [ 'TCP', '50000', 'dummytest' ], ],
        },
    ]
}

class System_files_parse_unittest(unittest.TestCase):
    def test_etc_hosts(self):
        self.maxDiff = None
        txtfile = "k8s_example/host_192.168.0.3_cmd_netmap_k8s_services_list.txt"
        k8s_services = K8s_parse.netmap_service_list(INPUT_DATA_DIRECTORY / txtfile)
        self.assertEqual(EXPECTED_RESULTS[txtfile], k8s_services)

if __name__ == "__main__":
    unittest.main()
