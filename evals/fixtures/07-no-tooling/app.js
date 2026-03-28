/**
 * UI logic for the calculator page.
 * Uses the global functions defined in calculate.js.
 */

function compute() {
  var a = parseFloat(document.getElementById("a").value);
  var b = parseFloat(document.getElementById("b").value);
  var op = document.getElementById("op").value;
  var resultEl = document.getElementById("result");

  var answer;

  switch (op) {
    case "add":
      answer = add(a, b);
      break;
    case "subtract":
      answer = subtract(a, b);
      break;
    case "multiply":
      answer = multiply(a, b);
      break;
    case "divide":
      answer = divide(a, b);
      break;
    case "percentage":
      answer = percentage(a, b);
      break;
    default:
      answer = "Unknown operation";
  }

  resultEl.textContent = "Result: " + answer;
}
