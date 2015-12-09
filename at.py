import subprocess

try:
    from shlex import quote as quote_arg
except ImportError:
    from pipes import quote as quote_arg

_AT_CMD = ['/usr/bin/at', '-M']
_SLEEP_CMD = ['/bin/sleep']

def quote_command(args):
	return ' '.join(quote_arg(arg) for arg in args)

def schedule(when, cmd):
	at = subprocess.Popen(
			AT_CMD + [when.strftime('%H:%M %d.%m.%Y')],
			stdin=subprocess.PIPE,
			stderr=subprocess.PIPE)
	delayed = quote_command(SLEEP_CMD + [when.strftime('%S.%f')]) + '; ' + quote_command(cmd)
	at.communicate(delayed)
