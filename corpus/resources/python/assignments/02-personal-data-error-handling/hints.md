## Hints for Assignment 2

First, insert the error function at the top of the program, under your program description comment.

```python
import sys

# prints error string and quits the program with an exit code
def error(str):
    print(str, file=sys.stderr)
    sys.exit(1)
```

You will need to check string lengths and do splicing.

```python
name = "Johnny"
print(len(name))
#> 6

# truncate name to length 4
print(name[0:4])
#> John
```

You will need to define functions - some that return values,
some that do not return values.

```python
# accepts a number and *returns* a string whether its big or small
def num_big_small(n):
    if n >= 100:
        return "big"
    else:
        return "small"

# prints whether a number is big or small - *does not return* a value
def print_big_small(n):
    print("{} is a {} number".format(n, num_big_small(n)))

# call the function, passing it a value
print_big_small(13)
#> 13 is a small number
```

Read the [strings tutorial](/resources/python/tutorials/?md=02-string-variables) for more information about string manipulation.
