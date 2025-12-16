const API_URL = "http://localhost:8000";

export async function getConfig() {
  const res = await fetch(`${API_URL}/`);

  if (!res.ok) {
    throw new Error("Error al obtener configuración");
  }

  return await res.json();
}

export async function startInterview(role) {
  const res = await fetch(`${API_URL}/ai/start-interview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ role }),
  });

  if (!res.ok) {
    throw new Error("Error iniciando entrevista");
  }

  return await res.json();
}


export async function receiveQuestion(interviewId) {
  const res = await fetch(
    `${API_URL}/ai/next-question/${interviewId}`,
    {
      method: "GET",
    }
  );

  if (!res.ok) {
    throw new Error("Error al recibir la pregunta");
  }

  return await res.json();
}


export async function submitAnswer(interviewId, audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "answer.webm");

  const res = await fetch(`${API_URL}/ai/submit-answer/${interviewId}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Error al enviar la respuesta");
  }

  return await res.json();
}


export async function getInterviewResults(interviewId) {
  const res = await fetch(`${API_URL}/ai/interview-results/${interviewId}`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Error al obtener resultados");
  }

  return await res.json();
}


export async function getQuestionAudio(interviewId) {
  return `${API_URL}/ai/question-audio/${interviewId}`;
}
