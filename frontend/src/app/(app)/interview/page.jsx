"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import VoiceRecorder from "@/components/VoiceRecorder";
import QuestionPlayer from "@/components/QuestionPlayer";
import { receiveQuestion, getConfig } from "@/services/InterviewService";


export default function InterviewPage() {
  const router = useRouter();

  const [question, setQuestion] = useState(null);
  const [interviewId, setInterviewId] = useState(null);
  const [totalQuestions, setTotalQuestions] = useState(10);
  const [currentQuestionNum, setCurrentQuestionNum] = useState(1);
  const [status, setStatus] = useState("loading");
  const [scores, setScores] = useState([]);
  const [timeoutSeconds, setTimeoutSeconds] = useState(120);
  const [timeRemaining, setTimeRemaining] = useState(120);
  const timerRef = useRef(null);

  // Cargar configuración del backend
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await getConfig();
        setTimeoutSeconds(config.question_timeout_seconds || 120);
        setTimeRemaining(config.question_timeout_seconds || 120);
      } catch (error) {
        console.error("Error loading config:", error);
      }
    };
    loadConfig();
  }, []);

  // Cargar datos de la entrevista desde localStorage
  useEffect(() => {
    const storedInterviewId = localStorage.getItem("currentInterviewId");
    const storedQuestion = localStorage.getItem("currentQuestion");
    const storedTotal = localStorage.getItem("totalQuestions");

    if (storedInterviewId && storedQuestion) {
      setInterviewId(storedInterviewId);
      setQuestion(storedQuestion);
      setTotalQuestions(parseInt(storedTotal) || 10);
      setCurrentQuestionNum(1);
      setStatus("ready");
      console.log("Datos de entrevista cargados desde localStorage");
    } else {
      console.error("No se encontraron datos de entrevista en localStorage");
      setStatus("error");
    }
  }, []);

  // Timer countdown with persistence
  useEffect(() => {
    if (status !== "ready" || !question) {
      // Clear timer if not in ready state
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      return;
    }

    // Check if we have a stored start time for this question
    const timerKey = `timer_${interviewId}_q${currentQuestionNum}`;
    let startTime = localStorage.getItem(timerKey);

    if (!startTime) {
      // First time seeing this question, store start time
      startTime = Date.now();
      localStorage.setItem(timerKey, startTime.toString());
    } else {
      startTime = parseInt(startTime);
    }

    // Calculate elapsed time
    const calculateRemaining = () => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      const remaining = Math.max(0, timeoutSeconds - elapsed);
      return remaining;
    };

    // Set initial remaining time
    setTimeRemaining(calculateRemaining());

    // Start countdown
    timerRef.current = setInterval(() => {
      const remaining = calculateRemaining();
      setTimeRemaining(remaining);

      if (remaining <= 0) {
        clearInterval(timerRef.current);
        // Clear this question's timer
        localStorage.removeItem(timerKey);
        handleTimeout();
      }
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [question, status, timeoutSeconds, interviewId, currentQuestionNum]);

  const handleTimeout = () => {
    console.log("Tiempo agotado! Pasando a la siguiente pregunta...");

    // Submit empty answer or skip to next question
    const dummyResponse = {
      transcription: "(Sin respuesta - tiempo agotado)",
      score: 0,
      reasoning: "No se proporcionó respuesta dentro del tiempo límite.",
      completed: currentQuestionNum >= totalQuestions,
      next_question: null
    };

    handleAnswerSubmitted(dummyResponse);
  };


  const handleAnswerSubmitted = async (response) => {
    console.log("Respuesta procesada:", response);

    // Clear timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Store score
    setScores([...scores, {
      question: question,
      score: response.score,
      reasoning: response.reasoning
    }]);

    // Check if interview is complete
    if (response.completed) {
      console.log("Entrevista completada!");
      // Navigate to results page
      router.push(`/results?id=${interviewId}`);
      return;
    }

    // Load next question
    if (response.next_question) {
      setQuestion(response.next_question);
      setCurrentQuestionNum(currentQuestionNum + 1);
      setStatus("ready");
    } else {
      // Fetch next question from API
      setStatus("loading");
      try {
        const nextResponse = await receiveQuestion(interviewId);

        if (nextResponse.completed) {
          router.push(`/results?id=${interviewId}`);
        } else {
          setQuestion(nextResponse.question);
          setCurrentQuestionNum(nextResponse.question_number);
          setStatus("ready");
        }
      } catch (error) {
        console.error("Error al cargar siguiente pregunta:", error);
        setStatus("error");
      }
    }
  };


  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-10 col-lg-8">

          {/* Progress indicator */}
          <div className="mb-4">
            <div className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Pregunta {currentQuestionNum} de {totalQuestions}</h5>
              <div className="d-flex gap-3 align-items-center">
                <span className="badge bg-primary">
                  {Math.round((currentQuestionNum / totalQuestions) * 100)}% completado
                </span>
                {status === "ready" && (
                  <span className={`badge ${timeRemaining <= 30 ? 'bg-danger' : timeRemaining <= 60 ? 'bg-warning' : 'bg-success'} fs-6`}>
                    {Math.floor(timeRemaining / 60)}:{String(timeRemaining % 60).padStart(2, '0')}
                  </span>
                )}
              </div>
            </div>
            <div className="progress mt-2" style={{ height: "8px" }}>
              <div
                className="progress-bar"
                role="progressbar"
                style={{ width: `${(currentQuestionNum / totalQuestions) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="card shadow">
            <div className="card-body">
              <h1 className="text-center mb-4">Entrevista de AI</h1>

              {status === "loading" && (
                <div className="text-center text-muted">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando...</span>
                  </div>
                  <br />
                  Cargando pregunta...
                </div>
              )}

              {status === "ready" && question && (
                <>
                  <div className="alert alert-info mb-4">
                    <div className="d-flex justify-content-between align-items-start">
                      <h5 className="mb-0 flex-grow-1">{question}</h5>
                      {interviewId && (
                        <QuestionPlayer interviewId={interviewId} questionNum={currentQuestionNum} />
                      )}
                    </div>
                  </div>

                  <VoiceRecorder
                    interviewId={interviewId}
                    onAnswerSubmitted={handleAnswerSubmitted}
                  />
                </>
              )}

              {status === "error" && (
                <div className="alert alert-danger">
                  <p className="mb-0">Error cargando la entrevista. Por favor, regresa e intenta de nuevo.</p>
                  <button
                    className="btn btn-primary mt-3"
                    onClick={() => router.push("/")}
                  >
                    Volver al inicio
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Previous scores */}
          {scores.length > 0 && (
            <div className="mt-4 card shadow-sm">
              <div className="card-body">
                <h6 className="card-title">Puntuaciones anteriores:</h6>
                <div className="d-flex gap-2">
                  {scores.map((s, idx) => (
                    <span key={idx} className="badge bg-secondary">
                      P{idx + 1}: {s.score}/5
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
