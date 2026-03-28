import React from "react";
import "./Button.css";

function Button({ label, onClick, variant = "primary" }) {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {label}
    </button>
  );
}

export default Button;
