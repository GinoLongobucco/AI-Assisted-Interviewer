"use client";
import { useState, useEffect } from "react";
import VoiceRecorder from "@/components/VoiceRecorder";
import { receiveQuestion } from "@/services/InterviewService";


export default function HomePage() {
  const MAX_QUESTIONS = 5;
  const [question, setQuestion] = useState(null);
  const [step, setStep] = useState(0);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    handleQuestion();
  }, [step]);


  const handleQuestion = async () => {
    setStatus("loading");
    //simulacion
    await new Promise(resolve => setTimeout(resolve, 1000));
    setQuestion(`Pregunta simulada ${step + 1}`);
    setStatus("ready");

    //servicio
    // if (!selectedRole) return;
    //setStatus("ready");
    // try {
    //   const response = await receiveQuestion();
    //   setQuestion(response.question);
    //   console.log("Recibe la pregunta desde el modelo:", response);
    // }
    // catch (error) {
    //   console.error("Error el recibir la pregunta:", error.message);
    // }
  };


  const handleAnswerSent = async () => {
    if (step + 1 >= MAX_QUESTIONS) {
      console.log("Entrevista finalizada");
      setStatus("finish");
      return;
    }

    setStatus("waiting");
    setQuestion(null);

    console.log("Esperando 3 segundos...");
    await new Promise(resolve => setTimeout(resolve, 3000));
    setStep(prev => prev + 1);
  };


  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow">
            <div className="card-body">
              {status === "finish" ? (
                <div className="text-center py-5">
                  <h4 className="text-success">Entrevista finalizada</h4>
                  <p>Gracias por completar la entrevista.</p>
                </div>
              ) : (
                <div>
                  <h1 className="text-center mb-3">Página de entrevista</h1>

                  {(status === "waiting" || status === "loading") && (
                    <p className="text-center text-muted">
                      Cargando pregunta...
                    </p>
                  )}

                  {status === "ready" && question && (
                    <>
                      <h5>{question}</h5>
                      <VoiceRecorder onAnswerSent={handleAnswerSent} />
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
