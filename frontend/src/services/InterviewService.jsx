export async function uploadAudio(formData) {
  const res = await fetch("https://", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Error subiendo audio");
  }

  return await res.json();
}


export async function auth(formData) {
  const res = await fetch("https://", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Error al autenticar");
  }

  return await res.json();
}