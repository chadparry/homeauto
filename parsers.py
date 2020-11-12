def get_enum_parser(type):
	def interpreted_value(x):
		if hasattr(type, x):
			return type[x].value
		return long(x, 0)
	return interpreted_value

def interpreted_int(x):
	return int(x, 0)

def interpreted_bool(x):
	values = {
		'off': False,
		'on': True,
		'0': False,
		'1': True,
	}
	return values[x]

def comma_delimited(x):
	return x.split(',')
