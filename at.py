from six.moves import shlex_quote
import subprocess
import tzlocal

_AT_CMD = ['/usr/bin/at', '-M']
_SLEEP_CMD = ['/bin/sleep']

def quote_command(args):
	return ' '.join(shlex_quote(arg) for arg in args)

def schedule(when, cmd):
	local_tzinfo = tzlocal.get_localzone()
	local_when = (local_tzinfo.localize(when) if when.tzinfo is None
			else when.astimezone(local_tzinfo))
	if local_when.second > 0 or local_when.microsecond > 0:
		delayed_cmd = '; '.join(quote_command(args) for args in (
				_SLEEP_CMD + [local_when.strftime('%S.%f')],
				cmd))
	else:
		delayed_cmd = quote_command(cmd)
	at = subprocess.Popen(
			_AT_CMD + [local_when.strftime('%H:%M %d.%m.%Y')],
			stdin=subprocess.PIPE,
			stderr=subprocess.PIPE)
	at.communicate(delayed_cmd)
