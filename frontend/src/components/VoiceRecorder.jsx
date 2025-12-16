"use client";

import { useState, useRef } from "react";
import { submitAnswer } from "@/services/InterviewService";


export default function VoiceRecorder({ interviewId, onAnswerSubmitted }) {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);
  const audioBlobRef = useRef(null);


  // Iniciar grabación
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, {
          type: "audio/webm",
        });

        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);

        audioBlobRef.current = audioBlob;
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (error) {
      console.error("Error al iniciar grabación", error);
    }
  };


  const sendRecording = async () => {
    if (!audioBlobRef.current || !interviewId) return;

    setLoading(true);

    try {
      const response = await submitAnswer(interviewId, audioBlobRef.current);
      console.log("Respuesta backend:", response);

      // Store result to display
      setResult(response);

      // Clear audio
      setAudioUrl(null);
      audioBlobRef.current = null;

    } catch (error) {
      console.error("Error enviando grabación", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    // Notify parent component to load next question
    onAnswerSubmitted(result);
    setResult(null);
  };


  // Detener grabación
  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };


  return (
    <div className="mt-5">
      {!recording ? (
        <button onClick={startRecording} className="btn btn-primary">
          Iniciar respuesta
        </button>
      ) : (
        <button onClick={stopRecording} className="btn btn-danger">
          Detener
        </button>
      )}

      {audioUrl && !result && (
        <>
          <div className="mt-4">
            <p>Reproducción:</p>
            <audio controls src={audioUrl}></audio>
          </div>

          <div className="row justify-content-center mt-4">
            <div className="col-md-8 col-lg-6 text-center">
              <button
                className="btn btn-primary px-4"
                onClick={sendRecording}
                disabled={loading}
              >
                {loading ? "Procesando..." : "Enviar respuesta"}
              </button>
            </div>
          </div>
        </>
      )}

      {result && (
        <div className="mt-4 card shadow-sm">
          <div className="card-body">
            <h5 className="card-title">Resultado de tu respuesta</h5>

            <div className="mb-3">
              <strong>Transcripción:</strong>
              <p className="text-muted">{result.transcription}</p>
            </div>

            <div className="mb-3">
              <strong>Puntuación:</strong>
              <h3 className="text-primary">{result.score} / 5</h3>
            </div>

            <div className="mb-3">
              <strong>Evaluación:</strong>
              <p className="text-muted">{result.reasoning}</p>
            </div>

            <div className="text-center mt-4">
              <button
                className="btn btn-success btn-lg px-5"
                onClick={handleNextQuestion}
              >
                {result.completed ? "Ver Resultados Finales" : "Siguiente Pregunta →"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
