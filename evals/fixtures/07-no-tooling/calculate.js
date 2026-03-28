/**
 * Basic arithmetic utility.
 *
 * BUG: divide() does not check for a zero divisor. Calling divide(x, 0)
 * returns Infinity (or NaN for 0/0), which silently corrupts downstream
 * calculations instead of throwing an error.
 */

function add(a, b) {
  return a + b;
}

function subtract(a, b) {
  return a - b;
}

function multiply(a, b) {
  return a * b;
}

function divide(a, b) {
  return a / b;
}

function percentage(value, total) {
  return divide(value, total) * 100;
}
