// src/pages/Auth.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE, setToken } from "../utils/auth";

export default function Auth() {
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const endpoint = mode === "signup" ? "/signup" : "/login";
      const body = mode === "signup" ? { email, password, name } : { email, password };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || JSON.stringify(data));

      // backend returns { access: "<token>" }
      if (data.access) {
        setToken(data.access);
        navigate("/settings");
      } else {
        // fallback for different response shapes
        setError("No token returned from server.");
      }
    } catch (err) {
      setError(err.message || "Unknown error");
    }
  }

  return (
    <div style={{ padding: 16, maxWidth: 420, margin: "0 auto" }}>
      <h2>{mode === "signin" ? "Sign In" : "Create Account"}</h2>
      <form onSubmit={submit}>
        {mode === "signup" && (
          <div>
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
        )}
        <div>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <div style={{ marginTop: 12 }}>
          <button type="submit">{mode === "signin" ? "Sign In" : "Sign Up"}</button>
        </div>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <hr />
      <button onClick={() => setMode(mode === "signin" ? "signup" : "signin")}>
        {mode === "signin" ? "Switch to Sign Up" : "Switch to Sign In"}
      </button>
    </div>
  );
}
