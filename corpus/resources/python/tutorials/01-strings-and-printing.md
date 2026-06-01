# Python Tutorial

## Strings and Printing
```python
# This is a comment
# Lines beginning with a '#' character are ignored by the python interpreter

# The print function has an argument containing a string enclosed in double quotes
## A string is one of the basic data types in Python
print("Hello World")
#> Hello World

# strings can be concatenated (combined together) using a '+' sign
print("Hello" + "World")
#> HelloWorld

# There is no space between the two words. Why? We need to tell python to print a space
print("Hello" + " " + "World")
#> Hello World

# We can print a number (e.g. an integer type) and python will convert it to string
print(2)
#> 2

# But what happens if we concatenate a string and a Number?
# print("2" + 2)
#> TypeError: must be str, not int

# Oops! We can't concatenate a string and a Number

## We have to convert the integer to a string
print("2" + str(2))
#> 22

## Thats the same as
print("2" + "2")
#> 22

## What about?
print("2+2")
#> 2+2

## Python prints exactly what you tell it to

# But concatenation is not numeric addition. What if we print numbers using a '+' sign?
print(2 + 2)
#> 4

# If we have a numeric string value, we can convert it to an integer to do addition
print(int("2") + 2)
#> 4
```
--------------------------------------------------------------------------

