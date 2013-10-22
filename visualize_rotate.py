# CC0 Licensed. http://creativecommons.org/publicdomain/zero/1.0/legalcode

from pylab import *
from rotate import to_delete
from time import sleep

now = datetime.datetime(2013, 1, 1, 1, 1, 1)
initial = now
current_set = set([])
s_last = []

while now <= datetime.datetime(2013, 4, 1, 1, 1, 1):
    current_set.add(now)
    current_set = current_set.difference(to_delete(current_set, now))
    s = [i.days for i in [(now - i) for i in sorted(current_set)]]
    if s != s_last:
        raw_input("press enter...")
        clf()
        scatter(s, [1] * len(s))
        axis([-1, 40, 0, 2])
        axvline(x=1, ymin=0, ymax=1)
        axvline(x=7, ymin=0, ymax=1)
        axvline(x=28, ymin=0, ymax=1)
        draw()
    s_last = s
    now += datetime.timedelta(hours=1)
