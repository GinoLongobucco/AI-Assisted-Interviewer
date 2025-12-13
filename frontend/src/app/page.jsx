"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { chooseRole, receiveQuestion } from "@/services/InterviewService";

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
  const [roleSent, setRoleSent] = useState(false);

  const handleRol = async () => {
    if (!selectedRole) return;
    setLoading(true);
    setRoleSent(true);

    try {
      const response = await chooseRole(selectedRole);
      console.log("Envia el rol:", response);
      // setRoleSent(true);
    }
    catch (error) {
      console.error("Error enviando rol:", error.message);
    }
  };


  const handleQuestion = async () => {
    setQuestion('Pregunta simulada 1');

    // if (!selectedRole) return;
    // setLoading(true);
    try {
      const response = await receiveQuestion();
      setQuestion(response.question);
      console.log("Recibe la pregunta desde el modelo:", response);
    }
    catch (error) {
      console.error("Error el recibir la pregunta:", error.message);
    }
  };


  //espera 3 seg y se mueve de ruta
  useEffect(() => {
    console.log('setRoleSent(true); ', roleSent)
    if (!roleSent) return;

    const timer = setTimeout(async () => {
      await handleQuestion();
      console.log('questionnn ', question)

      if (question) {
        router.push("/interview");
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, [roleSent, question]);


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
