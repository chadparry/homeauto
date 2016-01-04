#!/usr/bin/env python

import argparse
import contextlib
import OpenZWave.RemoteManager
import OpenZWave.values
import spicerack
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

OZWD_HOST = 'localhost'
OZWD_PORT = 9090

def bool_parser(x):
	values = {
		'off': False,
		'on': True,
		'0': False,
		'1': True,
	}
	return values[x]

HANDLERS = {
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Bool: (bool_parser, OpenZWave.RemoteManager.Client.SetValue_Bool),
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Byte: (int, OpenZWave.RemoteManager.Client.SetValue_UInt8),
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Decimal: (str, OpenZWave.RemoteManager.Client.SetValue_Decimal),
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Int: (int, OpenZWave.RemoteManager.Client.SetValue_int32),
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_List: (str, OpenZWave.RemoteManager.Client.SetValue_List),
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Schedule: (str, OpenZWave.RemoteManager.Client.SetValue_Schedule),
	OpenZWave.RemoteManager.RemoteValueType.ValueType_Short: (int, OpenZWave.RemoteManager.Client.SetValue_int16),
	OpenZWave.RemoteManager.RemoteValueType.ValueType_String: (str, OpenZWave.RemoteManager.Client.SetValue_String),
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Button: (str, OpenZWave.RemoteManager.Client.SetValue_Button),
	#OpenZWave.RemoteManager.RemoteValueType.ValueType_Raw: (str, OpenZWave.RemoteManager.Client.SetValue_Raw),
}

def interpreted_value(x):
	if hasattr(spicerack.Value, x):
		return spicerack.Value[x].value
	return long(x, 0)
parser = argparse.ArgumentParser(description='Control ZWave nodes')
parser.add_argument('--value', type=interpreted_value,
		help='ZWave value ID')
parser.add_argument('--node', type=int,
		help='ZWave node ID')
parser.add_argument('--position', required=True,
		help='Desired value position')
args = parser.parse_args()

if args.value is not None:
	value_id = explicit_value_id = OpenZWave.values.unpackValueID(spicerack.home_id, args.value)
if args.node is not None:
	value_id = computed_value_id = OpenZWave.values.getSwitchValueID(spicerack.home_id, args.node)
if args.value is None and args.node is None:
	raise ValueError('Either the value or node argument needs to be provided')
if args.value is not None and args.node is not None and explicit_value_id != computed_value_id:
	raise ValueError('The value and node arguments do not reconcile')
(parser, setter) = HANDLERS[value_id._type]
parsed = parser(args.position)

socket = thrift.transport.TSocket.TSocket(OZWD_HOST, OZWD_PORT)
transport = thrift.transport.TTransport.TBufferedTransport(socket)
protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(transport)
client = OpenZWave.RemoteManager.Client(protocol)

transport.open()
with contextlib.closing(transport):
	setter(client, value_id, parsed)
