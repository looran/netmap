#!/usr/bin/env python3

# netmap - network map generation from system commands and pcap traces
# netmap.py - generate text output analysis about the network
# Copyright (c) 2019, 2020 Laurent Ghigonis <ooookiwi@gmail.com>

VERSION = '1.0'
EPILOG=""" """

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / 'lib'))
import netmap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='netmap %s\ngenerate text output analysis about a network' % VERSION, epilog=EPILOG, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', dest='anonymize_hex_salt', help='Anonymize IP addresses, MAC and names. hexlified 16 bytes salt must be provided = 32 hex characters max.')
    parser.add_argument('-d', dest='debug', action='count', default=0, help='Show debug messages. Can be specified up to 2 times.')
    parser.add_argument('input_data_directory', help='input directory of system commands output and pcap traces')
    parser.add_argument('network_name', nargs='?', help='name of the network to analyse from input_data_directory. if not specified, list networks avaible for analysis.')
    args = parser.parse_args()
    
    data_dir = Path(args.input_data_directory).resolve()
    if not data_dir.exists():
        print("error: input_data_directory does not exist : %s" % data_dir)
        sys.exit(1)
    if args.network_name:
        network_dir = data_dir / args.network_name
        if not network_dir.exists():
            print("error: network directory '%s' does not exist in input_data_directory : %s" % (args.network_name, network_dir))
            sys.exit(1)
        netmap = netmap.Netmap(network_dir, anonymize_hex_salt=args.anonymize_hex_salt, debugval=args.debug)
        netmap.process()
        print(netmap.summary())
    else:
        print("Networks in %s:" % data_dir)
        print('\n'.join([str(x.name) for x in data_dir.iterdir() if x.is_dir()]))
