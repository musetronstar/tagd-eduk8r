## Assignment 2 - Personal Data with Error Handling

Modify your personal data program in the last assignment to:
* use functions for reusable code
* perform error checking

When an error occurs, print an error message and exit. For printing errors, place this function at the top of your file:

```python
import sys

# prints error string and quits the program with an exit code
def error(str):
    print(str, file=sys.stderr)
    sys.exit(1)
```

Check the following conditions:
* Name cannot be empty
* If the name is greater than 18 characters, truncate it to 18 characters
* Age must be a number greater than 0 and less than 180
* Gender can be any of {M, F, male, female} in any combination of upper or lower case.

At a minimum these function must be define:
* Define a function that accepts a number parameter and returns the proper English article for the number ('a' or 'an').
* Define a function `gender_title(gender, age)` that returns a string (man, boy, woman, girl) given the gender.
* Define a function `print_personal_data(name, age, gender)` that prints the final results. The name is printed in title case.

Read the following [hints](http://eduk8.us/resources/python/assignments/?md=02-personal-data-error-handling:hints) for this assignments if needed.

Remember to **update** your program description comments!

Upload your completed assignment to your network share directory in a sub-directory named "assignment-2"
