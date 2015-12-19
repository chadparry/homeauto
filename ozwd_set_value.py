#!/usr/bin/env python

import argparse
import contextlib
import ctypes
import OpenZWave.RemoteManager
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

OZWD_HOST = 'localhost'
OZWD_PORT = 9090
HOME_ID = 0xD501C6D1
DEFAULT_COMMAND_CLASS_ID = 0x25 # COMMAND_CLASS_SWITCH_BINARY
DEFAULT_INSTANCE_ID = 1
DEFAULT_VALUE_INDEX = 0
DEFAULT_TYPE = OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool

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
	# This conversion has a reference implementation at
	# https://github.com/OpenZWave/open-zwave/blob/master/cpp/src/value_classes/ValueID.h.
	id1 = args.value & 0xFFFFFFFF
	id2 = args.value >> 32
	value_id = explicit_value_id = OpenZWave.RemoteManager.RemoteValueID(
			_homeId=ctypes.c_int32(HOME_ID).value,
			_nodeId=(args.value & 0xFF000000) >> 24,
			_genre=(args.value & 0x00C00000) >> 22,
			_commandClassId=(args.value & 0x003FC000) >> 14,
			_instance=(args.value & 0xFF00000000000000) >> 56,
			_valueIndex=(args.value & 0x00000FF0) >> 4,
			_type=args.value & 0x0000000F)
if args.node is not None:
	value_id = computed_value_id = OpenZWave.RemoteManager.RemoteValueID(
			_homeId=ctypes.c_int32(HOME_ID).value,
			_nodeId=args.node,
			_genre=OpenZWave.RemoteManager.RemoteValueGenre.ValueGenre_User,
			_commandClassId=DEFAULT_COMMAND_CLASS_ID,
			_instance=DEFAULT_INSTANCE_ID,
			_valueIndex=DEFAULT_VALUE_INDEX,
			_type=DEFAULT_TYPE)
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
