import enum

class CommandClass(enum.Enum):
	"""Command Classes"""

	Alarm = 0x71
	ApplicationStatus = 0x22
	AssociationCommandConfiguration = 0x9b
	Association = 0x85
	Basic = 0x20
	BasicWindowCovering = 0x50
	Battery = 0x80
	CentralScene = 0x5B
	ClimateControlSchedule = 0x46
	Clock = 0x81
	Color = 0x33
	Configuration = 0x70
	ControllerReplication = 0x21
	CRC16Encap = 0x56
	DeviceResetLocally = 0x5a
	DoorLock = 0x62
	DoorLockLogging = 0x4c
	EnergyProduction = 0x90
	Hail = 0x82
	Indicator = 0x87
	Language = 0x89
	Lock = 0x76
	ManufacturerSpecific = 0x72
	Meter = 0x32
	MeterPulse = 0x35
	MultiCmd = 0x8f
	MultiInstanceAssociation = 0x8e
	MultiInstance = 0x60
	NodeNaming = 0x77
	NoOperation = 0x00
	Powerlevel = 0x73
	Proprietary = 0x88
	Protection = 0x75
	SceneActivation = 0x2B
	Security = 0x98
	SensorAlarm = 0x9c
	SensorBinary = 0x30
	SensorMultilevel = 0x31
	SwitchAll = 0x27
	SwitchBinary = 0x25
	SwitchMultilevel = 0x26
	SwitchToggleBinary = 0x28
	SwitchToggleMultilevel = 0x29
	ThermostatFanMode = 0x44
	ThermostatFanState = 0x45
	ThermostatMode = 0x40
	ThermostatOperatingState = 0x42
	ThermostatSetpoint = 0x43
	TimeParameters = 0x8B
	UserCode = 0x63
	Version = 0x86
	WakeUp = 0x84
	ZWavePlusInfo = 0x5E
