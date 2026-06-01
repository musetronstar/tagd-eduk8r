## Query Selectors and Event Handlers
### How to select HTML elements and add event handlers.
#### Use data attibutes to store user-defined data.

Read this [article](https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes) about HTML5 data attributes.

In this tutorial, we will access the `data-*` attribute of an element that was clicked on.

Use your **JavaScript console** to test the following code examples.  You can enable the console by pressing `F12` on your keyboard.

### 1. Use JavaScript to set `onclick event handlers` for HTML elements we are interested in.

Given the following HTML `<h1>` heading element and the unorder list `<li>` elements.

```html
<h1 data-imgsrc="images/default.jpg">Interests</h1>
<ul>
  <li data-imgsrc="images/music.jpg">Music</li>
  <li data-imgsrc="images/sports.jpg">Sports</li>
  <li data-imgsrc="images/cooking.jpg">Cooking</li>
</ul>
```
------------------------------------------------------------

<h1 data-imgsrc="images/default.jpg">Interests</h1>
<ul>
  <li data-imgsrc="images/music.jpg">Music</li>
  <li data-imgsrc="images/sports.jpg">Sports</li>
  <li data-imgsrc="images/cooking.jpg">Cooking</li>
</ul>

------------------------------------------------------------

Notice the `data-imgsrc` attribute which holds user defined data - in our case, images src URLs that correspond to each element.
We can extract that data in the `onclick event handler`.

```javascript
// function that set an <img> src attribute
function setImgSrc(src) {
	// this is for demonstration
	console.log("src: " + src);
}

// set event handler for <h1> element
document.querySelector("h1").onclick = function(e) {
	setImgSrc(e.dataset.imgSrc);
};

// set event handlers for <li> elements
document.querySelectorAll("li").forEach(function(e) {
	setImgSrc(e.dataset.imgSrc);
});
```
