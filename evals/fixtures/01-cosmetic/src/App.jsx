import React from "react";
import Button from "./Button";

function App() {
  return (
    <div className="app">
      <h1>Welcome</h1>
      <Button label="Get Started" onClick={() => alert("Clicked!")} />
      <Button label="Learn More" variant="secondary" onClick={() => {}} />
    </div>
  );
}

export default App;
