import contextlib
import OpenZWave.RemoteManager
import spicerack
import stompy.simple
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

STOMP_TOPIC = '/topic/zwave/monitor'

@contextlib.contextmanager
def get_thrift_client():
	socket = thrift.transport.TSocket.TSocket(spicerack.OZWD_HOST, spicerack.OZWD_PORT)
	transport = thrift.transport.TTransport.TBufferedTransport(socket)
	protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(transport)
	client = OpenZWave.RemoteManager.Client(protocol)

	transport.open()
	try:
		yield client
	finally:
		transport.close()

@contextlib.contextmanager
def stompy_connection(client, username=None, password=None, clientid=None):
	try:
		yield client.connect(username, password, clientid)
	finally:
		client.disconnect()

@contextlib.contextmanager
def stompy_subscription(client, destination, ack='auto', conf=None):
	try:
		yield client.subscribe(destination, ack, conf)
	finally:
		client.unsubscribe(destination, conf)

@contextlib.contextmanager
def get_stompy_client():
	stomp = stompy.simple.Client(host=spicerack.OZWD_HOST, port=spicerack.STOMPY_PORT)
	with stompy_connection(stomp):
		with stompy_subscription(stomp, STOMP_TOPIC):
			yield stomp
