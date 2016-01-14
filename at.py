import dateutil.tz
from six.moves import shlex_quote
import subprocess

_AT_CMD = ['/usr/bin/at', '-M']
_SLEEP_CMD = ['/bin/sleep']

def quote_command(args):
	return ' '.join(shlex_quote(arg) for arg in args)

def schedule(when, cmd):
	local_tzinfo = dateutil.tz.tzlocal()
	local_when = (when.replace(tzinfo=local_tzinfo) if when.tzinfo is None
			else when.astimezone(local_tzinfo))
	at = subprocess.Popen(
			_AT_CMD + [local_when.strftime('%H:%M %d.%m.%Y')],
			stdin=subprocess.PIPE,
			stderr=subprocess.PIPE)
	delayed_cmd = '; '.join(quote_command(cmd2) for cmd2 in (
			_SLEEP_CMD + [local_when.strftime('%S.%f')],
			cmd))
	at.communicate(delayed_cmd)
