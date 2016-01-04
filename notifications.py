import autonumber
import contextlib
import stompy.simple

@contextlib.contextmanager
def connection(client, username=None, password=None, clientid=None):
	try:
		yield client.connect(username, password, clientid)
	finally:
		client.disconnect()

@contextlib.contextmanager
def subscription(client, destination, ack='auto', conf=None):
	try:
		yield client.subscribe(destination, ack, conf)
	finally:
		client.unsubscribe(destination, conf)

@autonumber.unique
class NotificationType(autonumber.AutoNumber):
	"""Notification types

	Notifications of various Z-Wave events sent to the watchers
	registered with the Manager::AddWatcher method.

	Copied from http://www.openzwave.com/dev/classOpenZWave_1_1Notification.html#a5fa14ba721a25a4c84e0fbbedd767d54."""

	ValueAdded = 0  # A new node value has been added to OpenZWave's list. These notifications occur after a node has been discovered, and details of its command classes have been received.  Each command class may generate one or more values depending on the complexity of the item being represented.
	ValueRemoved = ()  # A node value has been removed from OpenZWave's list.  This only occurs when a node is removed.
	ValueChanged = ()  # A node value has been updated from the Z-Wave network and it is different from the previous value.
	ValueRefreshed = ()  # A node value has been updated from the Z-Wave network.
	Group = ()  # The associations for the node have changed. The application should rebuild any group information it holds about the node.
	NodeNew = ()  # A new node has been found (not already stored in zwcfg*.xml file)
	NodeAdded = ()  # A new node has been added to OpenZWave's list.  This may be due to a device being added to the Z-Wave network, or because the application is initializing itself.
	NodeRemoved = ()  # A node has been removed from OpenZWave's list.  This may be due to a device being removed from the Z-Wave network, or because the application is closing.
	NodeProtocolInfo = ()  # Basic node information has been receievd, such as whether the node is a listening device, a routing device and its baud rate and basic, generic and specific types. It is after this notification that you can call Manager::GetNodeType to obtain a label containing the device description.
	NodeNaming = ()  # One of the node names has changed (name, manufacturer, product).
	NodeEvent = ()  # A node has triggered an event.  This is commonly caused when a node sends a Basic_Set command to the controller.  The event value is stored in the notification.
	PollingDisabled = ()  # Polling of a node has been successfully turned off by a call to Manager::DisablePoll
	PollingEnabled = ()  # Polling of a node has been successfully turned on by a call to Manager::EnablePoll
	SceneEvent = ()  # Scene Activation Set received
	CreateButton = ()  # Handheld controller button event created
	DeleteButton = ()  # Handheld controller button event deleted
	ButtonOn = ()  # Handheld controller button on pressed event
	ButtonOff = ()  # Handheld controller button off pressed event
	DriverReady = ()  # A driver for a PC Z-Wave controller has been added and is ready to use.  The notification will contain the controller's Home ID, which is needed to call most of the Manager methods.
	DriverFailed = ()  # Driver failed to load
	DriverReset = ()  # All nodes and values for this driver have been removed.  This is sent instead of potentially hundreds of individual node and value notifications.
	EssentialNodeQueriesComplete = ()  # The queries on a node that are essential to its operation have been completed. The node can now handle incoming messages.
	NodeQueriesComplete = ()  # All the initialisation queries on a node have been completed.
	AwakeNodesQueried = ()  # All awake nodes have been queried, so client application can expected complete data for these nodes.
	AllNodesQueriedSomeDead = ()  # All nodes have been queried but some dead nodes found.
	AllNodesQueried = ()  # All nodes have been queried, so client application can expected complete data.
	Notification = ()  # An error has occured that we need to report.
	DriverRemoved = ()  # The Driver is being removed. (either due to Error or by request) Do Not Call Any Driver Related Methods after recieving this call
	ControllerCommand = ()  # When Controller Commands are executed, Notifications of Success/Failure etc are communicated via this Notification
	  # Notification::GetEvent returns Driver::ControllerCommand and Notification::GetNotification returns Driver::ControllerState
	NodeReset = ()  # The Device has been reset and thus removed from the NodeList in OZW

@autonumber.unique
class NotificationCode(autonumber.AutoNumber):
	"""Notification codes

	Notifications of the type Type_Notification convey some
	extra information defined here.

	Copied from http://www.openzwave.com/dev/classOpenZWave_1_1Notification.html#ae1a158109af2e17f8a83101a50809ca3."""

	MsgComplete = 0  # Completed messages
	Timeout = ()  # Messages that timeout will send a Notification with this code.
	NoOperation = ()  # Report on NoOperation message sent completion
	Awake = ()  # Report when a sleeping node wakes up
	Sleep = ()  # Report when a node goes to sleep
	Dead = ()  # Report when a node is presumed dead
	Alive = ()  # Report when a node is revived
