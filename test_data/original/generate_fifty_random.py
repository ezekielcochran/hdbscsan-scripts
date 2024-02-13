#!/usr/local/bin/python

import random

n = 50

print("{}".format(n))
for i in range(n):
	print("{} {}".format(random.randint(1, 100), random.randint(1, 100)))

