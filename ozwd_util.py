import contextlib
import OpenZWave.RemoteManager
import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport

OZWD_HOST = 'homeauto.spicerack.parry.org'
OZWD_PORT = 9090

@contextlib.contextmanager
def get_client():
	socket = thrift.transport.TSocket.TSocket(OZWD_HOST, OZWD_PORT)
	transport = thrift.transport.TTransport.TBufferedTransport(socket)
	protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(transport)
	client = OpenZWave.RemoteManager.Client(protocol)

	transport.open()
	try:
		yield client
	finally:
		transport.close()
