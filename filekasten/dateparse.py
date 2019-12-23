import subprocess

date_bin = subprocess.check_output(['which', 'date']).strip()
def parse_time(s):
    args = [date_bin, '--date=%s' % s, '--', '+%s']
    t = subprocess.check_output(args)
    return int(t)
