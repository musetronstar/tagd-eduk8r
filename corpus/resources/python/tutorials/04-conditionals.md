# Python Tutorial

## Booleans and Conditionals

### Boolean values
Booleans can have a value of either `True` or `False`
A boolean expression also evaluates to `True` or `False`.

All values are considered `True` unless they are:
* constants defined to be false: `None` and `False`.
* zero of any numeric type: `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)`
* empty sequences and collections: `''`, `()`, `[]`, `{}`, `set()`, `range(0)`

[Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)

#### `bool()` function
The `bool()` function tells whether a value evaluates to `True` or `False`.  For example

```python
bool(0)
#> False

bool(0.0)
#> False

bool(0.00001)
#> True

bool("Hello")
#> True

bool("")
#> False
```

### Conditionals

Conditionals evaluate boolean expressions, usually as a way of comparing values.
* Notice the indentation of statements within a conditional block must line up.
* The indented code following the `:` is known as a "block"
* Blocks of code have the same indentation level

```python
if True:            # conditional
    print("A")   # block of code (indented)
else:
    print("B")
#> A

if False:
    print("A")
else:
    print("B")
#> B

# a boolean value can be negated using a `not` operator
if not False:
    print("A")
else:
    print("B")
#> A

# there are also `elif` "shortened from else if" conditional statements 
if not True:
    print("A")
elif True:
    print("B")
else:
   print("C")
#> B
```

### Comparison
Logical operators compare a sequence of values and evaluate to `True` or `False`

| Logical operators | Refered to in English                          |
| -----------------:|:---------------------------------------------- |
| `==`              | equal to                                       |
| `!=`              | not equal to                                   |
| `<`               | less than                                      |
| `<=`              | less than or equal to                          |
| `>`               | greater than                                   |
| `>=`              | greater than or equal to                       |
| `is`              | is the same identity as                        |
| `in`              | equal to value a in a sequence                 |
| `and`             | expression to the left and the right are true  |
| `or`              | expression to the left or to the right is true |

```python
a = 1
b = 1
if a == b:
    print("a is equal to b")
else:
    print("a is not equal to b")
#> a is equal to b

a = 1
b = 2
if a == b:
    print("a is equal to b")
else:
    print("a is not equal to b")
#> a is not equal to b

if a > b:
    print("a is greater than b")
else:
    print("a is not greater than b")
#> a is not greater than b

if not a > b:
    print("negate a is greater than b")
else:
    print("a is greater than b")
#> negate a is greater than b



## arithmetic comparison operators
```

## Further Study
[Operator precedence](https://docs.python.org/3.3/reference/expressions.html#operator-precedence)

--------------------------------------------------------------------------
