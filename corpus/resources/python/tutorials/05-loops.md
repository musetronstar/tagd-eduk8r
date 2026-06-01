# Python Tutorial

## Loops

Loops contain a conditional statement and a block of code which will be
executed as long as the conditional statement is true.  They are useful in
situations where you want to repeat a block of code more than one time.

### `for` loop
The block of code in a `for` loop is executed (or iterated) over a sequence.

#### `range()` sequence
The `range(start, end, [step])` returns a sequence of integers
given range parameter start, end, and step
```python
# print integers in the range [0, 3): 0 inclusive to 3 exclusive.
# `i` is the name of the variable holding the value at that step in the loop
for i in range(0, 3):
	print(i)
#> 0
#> 1
#> 2


# print odd integers in the range [1, 10):
# from 1 inclusive to 10 exclusive, step (increment) by 2
for i in range(1, 10, 2):
	print(i)
#> 1
#> 3
#> 5
#> 7
#> 9
```

#### Lists & Tuples
Iterate over the items in a list. The same syntax is used for tuples.

```python
primes = [2, 3, 5, 7, 11, 13, 17]
for i in primes:
    print(i)
#> 2
#> 3
#> 5
#> 7
#> 11
#> 13
#> 17
```
##### Enumerate a list

To access the index of each item in a list, use the `enumerate()` function.
```python
# indexes:  0  1  2  3  4   5   6
primes =   [2, 3, 5, 7, 11, 13, 17]
for e in enumerate(primes):
    print(e)
#> (0, 2)
#> (1, 3)
#> (2, 5)
#> (3, 7)
#> (4, 11)
#> (5, 13)
#> (6, 17)

```

#### Dictionaries
Iterate over the keys, values, or items in a dictionary.

```python
fruit_basket = {
    'apples': 5,
    'oranges': 3,
    'bananas': 1
}

# Keys: for each key in the dictionary
for k in fruit_basket:
    print(k)
#> apples
#> oranges
#> bananas

# same as previous statement but using the `.keys()` method
# dict.keys() returns an iterable list of keys
for k in fruit_basket.keys():
    print(k)
#> apples
#> oranges
#> bananas

# Values: for each value in the dictionary
# dict.values() returns an iterable list of values
for v in fruit_basket.values():
    print(v)
#> 5
#> 3
#> 1

# Items: for each item in the dictionary. An item is a tuple with a key and value pair
# dict.items() returns a list of tuples containing the dictionary's key/value pairs
for e in fruit_basket.items():
    print(e)
#> ('apples', 5)
#> ('oranges', 3)
#> ('bananas', 1)
```

### `while` loop

The block of code in a `while` loop is executed as long as its conditional statement is true. (Both `if` statements and `while` loops use conditional statements to control flow).
```python
val = ""
# continue to ask a user for input until provided
while len(val) == 0:
    val = input("Enter a value: ")
print("You entered: ", val)
```


###### Additional Study
[Python for Beginners - Loops Tutorial](https://www.youtube.com/watch?v=6iF8Xb7Z3wQ&list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7&index=7)
