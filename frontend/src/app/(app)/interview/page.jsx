"use client";
import { useState, useEffect } from "react";
import VoiceRecorder from "@/components/VoiceRecorder";
import { receiveQuestion } from "@/services/InterviewService";

export default function HomePage() {

  const [question, setQuestion] = useState(null);

  useEffect(() => {
    handleQuestion();
  }, []);

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

  return (

    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow">
            <div className="card-body">
              <h1 className="text-center mb-3">Página de entrevista</h1>
              {question && (
                <div>
                  <h5>{question}</h5>
                  <VoiceRecorder />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
