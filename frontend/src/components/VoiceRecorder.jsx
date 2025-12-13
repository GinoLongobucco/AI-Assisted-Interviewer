"use client";

import { useState, useRef } from "react";
import { sendAnswer } from "@/services/InterviewService";


export default function voiceRecorder({ onAnswerSent }) {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);

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
    //temporarl
    onAnswerSent();

    if (!audioBlobRef.current) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("file", audioBlobRef.current, "grabacion.webm");

    try {
      // const respuesta = await sendAnswer(formData);
      // console.log("Respuesta backend", respuesta);

      // limpiar estado para la siguiente pregunta
      setAudioUrl(null);
      audioBlobRef.current = null;

      // onAnswerSent();
    } catch (error) {
      console.error("Error enviando grabación", error);
    } finally {
      setLoading(false);
    }
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

      {audioUrl && (
        <>
          <div className="mt-5">
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
                {loading ? "Procesando..." : "Continuar"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
