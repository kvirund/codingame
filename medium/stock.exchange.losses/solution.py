#!/usr/bin/python

# Author: Anton Gorev aka Veei
# Date: 2014-11-06

c = int(raw_input())
data = [int(a) for a in raw_input().split(" ")]

min = 0
for i in xrange(len(data)):
        if data[min] >= data[i]:
                min = i

max = min
for i in xrange(min):
        if data[max] < data[i]:
                max = i

print data[min] - data[max]
