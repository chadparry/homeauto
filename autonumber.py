import enum
from enum import unique

# This can't be a member because members in an enum are treated magically.
_AutoNumber_last = {}
class AutoNumber(enum.Enum):
	"""Automatically numbers enum values sequentially

	This code is based on the recipe at
	https://docs.python.org/3/library/enum.html#autonumber.
	It requires either Python 3.4 or the enum34 package."""
	def __new__(cls, *args):
		if args == ():
			if cls in _AutoNumber_last:
				value = _AutoNumber_last[cls] + 1
			else:
				value = 0
		elif len(args) == 1:
			value = args[0]
		else:
			value = args
		obj = object.__new__(cls)
		obj._value_ = value
		if isinstance(value, int):
			_AutoNumber_last[cls] = value
		return obj
