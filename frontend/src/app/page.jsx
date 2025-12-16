"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { startInterview, receiveQuestion } from "@/services/InterviewService";

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

  const [selectedRole, setSelectedRole] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState(null);
  const [interviewId, setInterviewId] = useState(null);

  // Limpiar localStorage cuando se carga la página principal
  useEffect(() => {
    localStorage.removeItem("currentInterviewId");
    localStorage.removeItem("currentQuestion");
  }, []);

  const handleRol = async () => {
    if (!selectedRole) return;
    setLoading(true);

    try {
      const response = await startInterview(selectedRole);
      console.log("Entrevista iniciada:", response);

      // Save interview data
      setInterviewId(response.interview_id);
      setQuestion(response.first_question);

      // Store in localStorage for interview page
      localStorage.setItem("currentInterviewId", response.interview_id);
      localStorage.setItem("currentQuestion", response.first_question);
      localStorage.setItem("totalQuestions", response.total_questions);

      // Navigate to interview page
      setTimeout(() => {
        router.push("/interview");
      }, 1000);
    }
    catch (error) {
      console.error("Error iniciando entrevista:", error.message);
      setLoading(false);
    }
  };


  // Cuando se obtiene la pregunta, navega a la página de entrevista
  useEffect(() => {
    if (question && interviewId) {
      router.push("/interview");
    }
  }, [question, interviewId, router]);


  return (
    <div className="container py-5">
      <div className="row justify-content-center mb-4">
        <div className="col-md-8 col-lg-6 text-center">
          <h1 className="mb-3">Selecciona el rol para ser entrevistado</h1>
        </div>
      </div>

      <div className="row justify-content-center g-3">
        {roles.map((role) => (
          <div key={role} className="col-6 col-md-4 col-lg-3">
            <div
              className={`card shadow-sm text-center p-3 selectable-card ${selectedRole === role ? "selected" : ""
                }`}
              style={{ cursor: "pointer" }}
              onClick={() => !loading && setSelectedRole(role)} // bloquear si loading
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
              onClick={handleRol}
              disabled={loading}
            >
              {loading ? "Procesando..." : "Continuar"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
