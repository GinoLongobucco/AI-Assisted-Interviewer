
export async function auth(formData) {
  const res = await fetch("http://", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Error al autenticar");
  }

  return await res.json();
}


export async function chooseRole(rol) {
  const res = await fetch("http://", {
    method: "POST",
    body: rol,
  });

  if (!res.ok) {
    throw new Error("Error al elegir un rol");
  }

  return await res.json();
}


export async function receiveQuestion() {
  const res = await fetch("http://", {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Error al recibir la pregunta");
  }

  return await res.json();
}


export async function sendAnswer(formData) {
  const res = await fetch("http://", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Error al enviar la respuesta");
  }

  return await res.json();
}