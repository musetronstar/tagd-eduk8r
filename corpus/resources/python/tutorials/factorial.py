#!/usr/bin/python3

import sys

def r_factorial(n):
    if n == 0:
        return 1
    if n < 0:
        return None
    return n * r_factorial(n-1)


def factorial(n):
    f = 1
    for i in range(1 ,n+1):
        f *= i
    return f

num = int(sys.argv[1])
print(r_factorial(num))
