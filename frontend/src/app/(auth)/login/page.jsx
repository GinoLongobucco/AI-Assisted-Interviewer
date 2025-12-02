"use client";

import { useState } from "react";
import { auth  } from "@/services/InterviewService";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await auth({ email, password });
      console.log("Entra al login:", response);
    } catch (error) {
      console.error("Error en login:", error.message);
    }
  };

  return (
    <main className="d-flex align-items-center justify-content-center min-vh-100 bg-light">
      <div
        className="card shadow-lg p-4"
        style={{ maxWidth: "420px", width: "100%" }}
      >
        <h1 className="text-center mb-4">Login</h1>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button className="btn btn-primary w-100 mt-3" type="submit">
            Login
          </button>
        </form>
      </div>
    </main>
  );
}
