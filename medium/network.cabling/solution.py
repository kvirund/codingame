#!/usr/bin/python

# Author: Anton Gorev aka Veei
# Date: 2014-11-06

import sys

n = int(raw_input())
ys = []
sum = 0
first = True
minx = maxx = 0
miny = maxy = 0
for i in xrange(n):
    b = [int(a) for a in raw_input().split(" ")]
    ys += [b[1]]
    sum += b[1]
    if first or minx > b[0]:
        minx = b[0]
    if first or maxx < b[0]:
        maxx = b[0]
    if first or miny > b[1]:
        miny = b[1]
    if first or maxy < b[1]:
        maxy = b[1]
    first = False
    
def length(ys, y):
    return reduce(lambda a, b: a + abs(b - y), ys, 0)

result = y = miny
lmin = length(ys, miny)
lmax = length(ys, maxy)
while miny != maxy:
    print >> sys.stderr, miny, maxy
    if 1 == maxy - miny:
        if lmin < lmax:
            maxy = miny
        else:
            miny = maxy
        break
    
    midy = (maxy + miny)/2
    lmid = length(ys, midy)
    if lmid < lmin and lmid < lmax:
        nl = length(ys, midy + 1)
        if nl > lmid:
            maxy = midy
            lmax = lmid
        else:
            miny = midy
            lmin = lmid
    elif lmid < lmin and lmid >= lmax:
        miny = midy
        lmin = lmid
    elif lmid >= lmin and lmid < lmax:
        lmax = lmid
        maxy = midy
    else:
        print >> sys.stderr, "Broken logic", lmin, lmid, lmax, miny, midy, miny
        break

print >> sys.stderr, miny, length(ys, miny)
print length(ys, miny) + maxx - minx
