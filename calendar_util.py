from . import autonumber
import calendar
import datetime
import ephem

class Month(autonumber.AutoNumber):
	# An explicit order is required for Python versions before 2.7.8.
	__order__ = """
		JANUARY
		FEBRUARY
		MARCH
		APRIL
		MAY
		JUNE
		JULY
		AUGUST
		SEPTEMBER
		OCTOBER
		NOVEMBER
		DECEMBER
	"""
	JANUARY = 1
	FEBRUARY = ()
	MARCH = ()
	APRIL = ()
	MAY = ()
	JUNE = ()
	JULY = ()
	AUGUST = ()
	SEPTEMBER = ()
	OCTOBER = ()
	NOVEMBER = ()
	DECEMBER = ()

class DayOfWeek(autonumber.AutoNumber):
	# An explicit order is required for Python versions before 2.7.8.
	__order__ = """
		MONDAY
		TUESDAY
		WEDNESDAY
		THURSDAY
		FRIDAY
		SATURDAY
		SUNDAY
	"""
	MONDAY = ()
	TUESDAY = ()
	WEDNESDAY = ()
	THURSDAY = ()
	FRIDAY = ()
	SATURDAY = ()
	SUNDAY = ()
assert DayOfWeek.MONDAY.value == 0
assert DayOfWeek.SUNDAY.value == 6

def get_new_years(year):
	return datetime.date(year, Month.JANUARY.value, 1)

def get_autumnal_equinox(year):
	return ephem.localtime(ephem.next_autumnal_equinox(datetime.date(year, Month.JANUARY.value, 1))).date()

def get_halloween(year):
	return datetime.date(year, Month.OCTOBER.value, 31)

def get_thanksgiving(year):
	thanksgiving_calendar = calendar.Calendar(DayOfWeek.THURSDAY.value)
	thanksgiving_month = thanksgiving_calendar.monthdatescalendar(year, Month.NOVEMBER.value)
	thanksgiving = thanksgiving_month[3][0]
	return thanksgiving
