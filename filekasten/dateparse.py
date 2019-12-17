import subprocess

def parse_time(s):
    args = ['/usr/bin/date', '--date=%s' % s, '--', '+%s']
    t = subprocess.check_output(args)
    return int(t)
