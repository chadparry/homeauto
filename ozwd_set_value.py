#!/usr/bin/env python

import argparse
import contextlib
import ctypes
import OpenZWave.RemoteManager
import OpenZWave.values
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

OZWD_HOST = 'localhost'
OZWD_PORT = 9090
HOME_ID = 0xD501C6D1

def interpreted_long(x):
	return long(x, 0)
class PositionAction(argparse.Action):
	def __init__(self, option_strings, dest, **kwargs):
		super(PositionAction, self).__init__(
				option_strings, dest, **kwargs)
	def __call__(self, parser, namespace, values, option_string=None):
		position = {'off': False, 'on': True}[values]
		setattr(namespace, self.dest, position)
parser = argparse.ArgumentParser(description='Control ZWave switches')
parser.add_argument('--value', type=interpreted_long,
		help='ZWave value ID')
parser.add_argument('--node', type=int,
		help='ZWave node ID')
parser.add_argument('--position', choices=['off', 'on'], required=True,
		action=PositionAction,
		help='Desired switch position')
args = parser.parse_args()

if args.value is not None:
	value_id = explicit_value_id = OpenZWave.values.unpackValueID(HOME_ID, args.value)
if args.node is not None:
	value_id = computed_value_id = OpenZWave.values.getSwitchValueID(HOME_ID, args.node)
if args.value is None and args.node is None:
	raise ValueError('Either the value or node argument needs to be provided')
if args.value is not None and args.node is not None and explicit_value_id != computed_value_id:
	raise ValueError('The value and node arguments do not reconcile')

socket = thrift.transport.TSocket.TSocket(OZWD_HOST, OZWD_PORT)
transport = thrift.transport.TTransport.TBufferedTransport(socket)
protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(transport)
client = OpenZWave.RemoteManager.Client(protocol)

transport.open()
with contextlib.closing(transport):
	client.SetValue_Bool(value_id, args.position)
