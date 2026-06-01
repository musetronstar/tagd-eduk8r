## Query Selectors and Event Handlers
### How to select HTML elements and add event handlers.

The web browser tracks events that take place, for example, a mouse click or hovering over an element.  
Using JavaScript, we can tell the browser to call a function when a specific event takes place.  
This is type of **callback function** called an **event handler**.

Use your **JavaScript console** to test the following code examples.  You can enable the console by pressing `F12` on your keyboard.

### 1. Use JavaScript to Select Elements

Given the following HTML `<h4>` heading element and the unorder list `<li>` elements.

------------------------------------------------------------

#### Personal Interests
* Music
* Sports
* Cooking

------------------------------------------------------------

##### Select the `<h4>` element ("Personal Interests") and set an event handler

```javascript
// select the first <h4> element in the page and return the `Element` object
let elem = document.querySelector('h4');

// set an event such that when we mouse over the element,
// it appends a dash ('-') to the element's inner text
elem.onmouseover = function(ev) {
	let elem = ev.target;  // the element that caused this event
	elem.textContent += '-';
};
```

Let's generalize the text appending for several events.

```javascript
// append a string to an element's textContent property
function appendText(elem, str) {
	elem.textContent += str;
}

// set events for the given element
function setEvents(elem) {
	elem.onmouseover = function(ev) {
		appendText(ev.target, "-");
	};

	elem.onclick = function(ev) {
		appendText(ev.target, "+");
	};
}

setEvents(document.querySelector('h4'));

// what will this do?
setEvents(document.querySelector('li'));
```

You can see that `document.querySelector('li')` only selected the first element, through we have three.

Let's select all three `<li>` elements using `querySelectorAll("li")` and set their events.

```javascript
/*\
|*| Iterate through all selected <li> elements
|*| using either of the two approaches below.
\*/

// array of `li` elements
let elems = document.querySelectorAll("li");

// 1. Iterate using a `for` loop
for (let i=0; i<elems.length; i++) {
	setEvents(elems[i]);
}

// 2. Use the `Array.forEach()` method to execute a callback function
//    for each element, passing that element as an argument.
elems.forEach(function(e) {
	setEvents(e);
});
```

### Further study
##### [Arrays](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
##### [Array.forEach()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)
