# Python Tutorial

## Integers and Floating Point numbers

```python
## ints and floats are stored in memory differently
# int (no decimal place)
i = 7
j = 22
# float (has decimal place)
f = 7.0

## remember python prints strings literally
print("i + f")
#> i + f

## notice the answer is a float - Python converts `i` to a float
print(i + f)
#> 14.0

## addition
print(i + j)
#> 29

## subtraction
print(j - i)
#> 15
print(i - j)
#> -15

## multiplication
print(i * j)
#> 154

## exponents
print(i ** 2)  # 7 to the power of 2
#> 49

## division
print(j / i)
#> 3.142857142857143

## floor division (integer division)
print(j // i)
#> 3.0

## modulo gives the remainder of a division operation
print(j % i)
#> 1

print("{} ÷ {} = {} R {}".format(j, i, (j//i), (j%i)))
#> 22 ÷ 7 = 3 R 1

## printing numbers as strings
# print("i = " + i)
# TypeError: must be str, not int

# we have to convert i to a string first!
print("i = " + str(i) + ", j = " + str(j) + ", f = " + str(f))
#> i = 7, j = 22, f = 7.0

# let Python convert for us
print("i = {}, j = {}, f = {}".format(i, j, f))
#> i = 7, j = 22, f = 7.0

# old school `printf` style
print("i = %s, j = %s, f = %s" % (i, j, f))
#> i = 7, j = 22, f = 7.0

# `printf` with padding and precision (for f)
print("i = %s, j = %s, f = %6.2f" % (i, j, f))
#> i = 7, j = 22, f =   7.00

# f-string (formatted string literals)
print(f"i = {i}, j = {j}, f = {f:6.2f}")
#> i = 7, j = 22, f =   7.00
```

## Further Study
* [Operator precedence](https://docs.python.org/3.3/reference/expressions.html#operator-precedence)
* [f-string formatted string literals](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals)

