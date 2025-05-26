import sys

def convert(s):
    s = s.replace('(s ', 'S(')
    s = s.replace('(p ', 'P(')
    s = s.replace('(r)', '1')
    s = s.replace(' ', ',')

    return s

for line in sys.stdin:
    print(convert(line.strip()))
