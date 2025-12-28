"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { startInterview } from "@/services/InterviewService";

export default function HomePage() {
  const router = useRouter();

  const roles = [
    "Software Developer",
    "Project Leader",
    "Data Analyst",
    "UX Designer",
    "QA Engineer",
    "Product Manager",
  ];

  // Step 1: Email collection, Step 2: Role selection
  const [step, setStep] = useState(1);

  // Email form
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [emailError, setEmailError] = useState("");

  // Role selection
  const [selectedRole, setSelectedRole] = useState(null);
  const [loading, setLoading] = useState(false);

  // Clear localStorage on mount
  useEffect(() => {
    localStorage.removeItem("currentInterviewId");
    localStorage.removeItem("currentQuestion");
    localStorage.removeItem("candidateEmail");
  }, []);

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleEmailSubmit = (e) => {
    e.preventDefault();

    if (!email) {
      setEmailError("Email is required");
      return;
    }

    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address");
      return;
    }

    setEmailError("");
    localStorage.setItem("candidateEmail", email);
    localStorage.setItem("candidateFirstName", firstName);
    localStorage.setItem("candidateLastName", lastName);
    setStep(2);
  };

  const handleStartInterview = async () => {
    if (!selectedRole) return;
    setLoading(true);

    try {
      const response = await startInterview({
        email: email,
        role: selectedRole,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
      });

      console.log("Interview started:", response);

      // Store interview data
      localStorage.setItem("currentInterviewId", response.interview_id);
      localStorage.setItem("currentQuestion", response.first_question);
      localStorage.setItem("totalQuestions", response.total_questions);

      // Navigate to interview page
      setTimeout(() => {
        router.push("/interview");
      }, 500);
    } catch (error) {
      console.error("Error starting interview:", error.message);
      setEmailError("Failed to start interview. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      {step === 1 ? (
        // Step 1: Email Collection
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="card shadow">
              <div className="card-body p-4">
                <h1 className="text-center mb-4">Welcome to AI Interview</h1>
                <p className="text-center text-muted mb-4">
                  Please enter your email to begin
                </p>

                <form onSubmit={handleEmailSubmit}>
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                      Email Address <span className="text-danger">*</span>
                    </label>
                    <input
                      type="email"
                      className={`form-control ${emailError ? "is-invalid" : ""}`}
                      id="email"
                      placeholder="your.email@example.com"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        setEmailError("");
                      }}
                      required
                    />
                    {emailError && (
                      <div className="invalid-feedback">{emailError}</div>
                    )}
                  </div>

                  <div className="mb-3">
                    <label htmlFor="firstName" className="form-label">
                      First Name <span className="text-muted">(optional)</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="firstName"
                      placeholder="John"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="lastName" className="form-label">
                      Last Name <span className="text-muted">(optional)</span>
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="lastName"
                      placeholder="Doe"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary w-100"
                  >
                    Continue to Role Selection
                  </button>
                </form>

                <div className="mt-4 text-center">
                  <a href="/admin/login" className="text-muted small">
                    Admin Login
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Step 2: Role Selection
        <>
          <div className="row justify-content-center mb-4">
            <div className="col-md-8 col-lg-6 text-center">
              <h1 className="mb-2">Select Role for Interview</h1>
              <p className="text-muted">
                Welcome, {firstName || email}! Choose the role you're applying for.
              </p>
              <button
                className="btn btn-sm btn-outline-secondary mt-2"
                onClick={() => setStep(1)}
                disabled={loading}
              >
                ← Change Email
              </button>
            </div>
          </div>

          <div className="row justify-content-center g-3">
            {roles.map((role) => (
              <div key={role} className="col-6 col-md-4 col-lg-3">
                <div
                  className={`card shadow-sm text-center p-3 selectable-card ${selectedRole === role ? "selected" : ""
                    }`}
                  style={{ cursor: "pointer" }}
                  onClick={() => !loading && setSelectedRole(role)}
                >
                  <h6 className="mt-2">{role}</h6>
                </div>
              </div>
            ))}
          </div>

          {selectedRole && (
            <div className="row justify-content-center mt-4">
              <div className="col-md-8 col-lg-6 text-center">
                <button
                  className="btn btn-primary px-4"
                  onClick={handleStartInterview}
                  disabled={loading}
                >
                  {loading ? "Starting Interview..." : "Start Interview"}
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
