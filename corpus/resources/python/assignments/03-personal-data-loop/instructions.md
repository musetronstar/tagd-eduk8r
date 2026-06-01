## Assignment 3 - Personal Data Input Loop

We will modify our last assignment to
* allow input of data for more than one person
  * prompt for input until the user quits
* print all personal data, *after* prompting for input
* print the average of all ages entered

Changes that *must* be made:
* Add a function `input_personal_data()` that returns a dictionary with keys `name`, `age`, `gender`
* Modify print_personal_data(data) that prints personal data as before.  The `data` parameter will be a dictionary containing `name`, `age`, `gender`.
* Add a function called `warn(msg)` that prints to `stderr` like `error()` but does not exit.
  * Modify so that invalid input does not cause the program to exit, just prompt for a new person.
* Add a loop that prompts for user input until a user enters
  * 'y' or 'yes' (upper or lowercase) to continue
  * 'q', 'quit', 'n', or 'no' (upper or lowercase) to exit the prompt
* After exiting the prompt for user input
  * print all personal data in same format as before
  * print `Average age: ##.##` where age is formatted as a float type with a precision of two decimal places.
    see [printing float precision](http://eduk8.us/resources/python/tutorials/?md=03-integers-and-floats)

Upload your completed assignment to your network share directory in a sub-directory named "assignment-3"
