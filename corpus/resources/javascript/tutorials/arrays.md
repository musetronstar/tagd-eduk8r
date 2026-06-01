## Array Tutorial

Arrays contain a list of values which can be indexed with and integer.

Here is an array of prime numbers.
```javascript
// prime numbers
// index:     0  1  2  3  4
let primes = [2, 3, 5, 7, 11];

// the length property - an empty array will have a length == 0
console.log(primes.length);
//> 5

// access the first element using subscript notation (aka brackets [index])
console.log(primes[0]);
//> 2

// the last element
console.log(primes[primes.length-1]);
//> 11

// out of range - some languages throw an error - JavaScript returns `undefined`
console.log(primes[5]);
//> undefined

// looping through arrays
// 1. `for` loop
for (let i=0; i<primes.length; i++) {
	console.log(i, primes[i]);
}
/*
0 2
1 3
2 5
3 7
4 11
*/

// 2. use `forEach()` to call a function callback for each element
//    the parameters to the callback are:
//    * the current element
//    * the current index (optional)
//    * the array operated on (optional)
primes.forEach(function(e, i, arr) {
	if (e !== arr[i]) console.error("impossible!");
	console.log(i, e);
});
/*
0 2
1 3
2 5
3 7
4 11
*/

// push a value (add to the end of the array) and returns the new length
var len = primes.push(13);
console.log(primes);
//> [2, 3, 5, 7, 11, 13]
console.log(len);
//> 6

// pop a value (remove from the end of the array)
let val = primes.pop();
console.log(primes);
//> [2, 3, 5, 7, 11]
console.log(val);
//> 13

// shift a value (remove from the beginning of the array)
val = primes.shift();
console.log(primes);
//> [3, 5, 7, 11]
console.log(val);
//> 2

// unshift a value (add to the begginning or the array) and returns the new length
len = primes.unshift(2);
console.log(primes);
//> [2, 3, 5, 7, 11]
console.log(len);
//> 5
```

### Additional resources
* [MDN - Arrays](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
