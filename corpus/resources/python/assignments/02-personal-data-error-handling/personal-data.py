# ICT 2019 - Isaac N Colley
# The purpose of this program is to ask the user to input a persons name,
# gender and age, then output whether they are a man, boy, woman or girl.

# returns an English article string "a" or "an"
# given a numeric input string
def number_article(num):
    # if the number begins with "8" or is equal to "11" or "18"
    if num[0] == "8" or num in ("11", "18"):
        return "an"
    else:
        return "a"

print("Please enter the following personal data:")
name = input("Name: ")
gender = input("Gender (M/F): ")
age = input("Age: ")
title = ""  # holds man, boy, woman, girl

if gender == "M":
    if int(age) >= 18:
        title = "man"
    else:
        title = "boy"
elif gender == "F":
    if int(age) >= 18:
        title = "woman"
    else:
        title = "girl"

print("{} is {} {} year old {}.".format(
    name, number_article(age), age, title)
)
