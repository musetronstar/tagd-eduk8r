## Project 2 - Adding JavaScript Functionality

This assignment will build upon the project "Our First Website" by adding interactivity and dynamic images using JavaScript.

You will change the files from the Mozilla tutorial you followed in the last project which should be in a directory called "test-site" and look exactly like this:  
http://mdn.github.io/beginner-html-site-styled/

Read and the following tutorial. Make sure you understand how JavaScript is being used to dynamically change the image.  
https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/JavaScript_basics

### What you will turn in
We will build on what we learned in the tutorial and some dynamic behavior to our *"About Me"* webpage:  
**Add a script that changes the image when you click on a list item of your personal interests.**

For example, if one of your personal interests is basketball, clicking on that list item will change the image to something related to basketball.

#### Requirements
* You should have at least 3 list items and three images corresponding to those interests
* The **images** should be all be displayed as the **same size height and width**. It is up to you what sizes you use, but they must be consistent. For example if the image of you is 800x600px, the other images must be the same height and width. You might have to edit photos and crop their sizes.
* **Clicking** on a list item **changes** the **image** displayed. The image should correspond to the interest, but does not have to be your own image - you can reuse an image on the Internet.
* Clicking on the *"About Me"* `<h1>` tag changes the image back to its initial state (the picture of you).

When you are finished. Use FTP to **upload your changes to your eduk8.us website**. You will **overwrite** the existing "About Me" files with the new ones.

See the tutorial *[Query Selectors and Events](http://eduk8.us/resources/javascript/?md=tutorials:query-selectors-events)* for help with selecting all `<li>` elements and adding event handlers.

### Extra Credit
Any (or all) of the following:
* Change the mouse cursor, colors, border, etc. on mouseover event for list items
* Change the look of the selected item, so we can see visually what item is selected
* Wrap your `<img>` tag in a `<figure>` and change the `<caption>` corresponding to the selected item.
