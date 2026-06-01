## Query Selectors and Event Handlers
### How to select HTML elements and add event handlers.
#### Use class attributes to select elements we are interested in.

In this tutorial, we will set onclick events to elements we select according to their class attributes.

Use your **JavaScript console** to test the following code examples.  You can enable the console by pressing `F12` on your keyboard.

### 1. Use JavaScript to set `onclick event handlers` for HTML elements we are interested in.

Given the following HTML `<h1>` heading element and the unorder list `<li>` elements.

```html
<h1 class="about-me">About Me</h1>
<ul>
  <li class="music">Music</li>
  <li class="sports">Sports</li>
  <li class="cooking">Cooking</li>
</ul>
```
------------------------------------------------------------

<h1 class="about-me">About Me</h1>
<ul>
  <li class="music">Music</li>
  <li class="sports">Sports</li>
  <li class="cooking">Cooking</li>
</ul>

------------------------------------------------------------

We can select individual elements using the class selectors.

```javascript
// function that set an <img> src attribute
function setImgSrc(src) {
	// this is for demonstration, your code will need to actually
	// set an img element's src property
	alert("src: " + src);
}

// set event handler for <h1> element
document.querySelector("h1.about-me").onclick = function(e) {
	setImgSrc("images/default.jpg");
};

// set event handlers for <li> elements
document.querySelector("li.music").onclick = function(e) {
	setImgSrc("images/music.jpg");
};

document.querySelector("li.sports").onclick = function(e) {
	setImgSrc("images/sports.jpg");
};

document.querySelector("li.cooking").onclick = function(e) {
	setImgSrc("images/cooking.jpg");
};
```
