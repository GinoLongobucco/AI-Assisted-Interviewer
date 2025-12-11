"use client";

import { useState, useRef } from "react";
import { sendAnswer } from "@/services/InterviewService";

export default function voiceRecorder() {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  // Iniciar grabación
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream);

      audioChunks.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);

        // Enviar al backend
        const formData = new FormData();
        formData.append("file", audioBlob, "grabacion.webm");

        formData.forEach((value, key) => {
          console.log(key, value);
        });

        const file = formData.get("file");
        const url = URL.createObjectURL(file);

        new Audio(url).play();

        const respuesta = await sendAnswer(formData);
        console.log("Respuesta backend", respuesta);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (error) {
      console.error("Error al iniciar grabación", error);
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
        <div className="mt-5">
          <p>Reproducción:</p>
          <audio controls src={audioUrl}></audio>
        </div>
      )}
    </div>
  );
}
