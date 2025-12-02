import os
import uuid
import json
import requests
import aiofiles
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client

from dotenv import load_dotenv

# ============================================================================
# CARGAR VARIABLES DE ENTORNO (.env) DESDE /backend SIN IMPORTAR DESDE DÓNDE
# SE EJECUTE UVICORN
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

# ============================================================================
# LEER VARIABLES
# ============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("ERROR: No se pudo cargar SUPABASE_URL o SUPABASE_KEY desde .env")

# Conexión Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================================
# CONFIG FASTAPI
# ============================================================================
app = FastAPI(title="AI Interview Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELOS
# ============================================================================
class RegisterCandidateModel(BaseModel):
    email: str
    first_name: str
    last_name: str

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/")
def home():
    return {"message": "Backend funcionando correctamente"}

# ============================================================================
# REGISTRO DE CANDIDATO
# ============================================================================
@app.post("/register_candidate")
def register_candidate(data: RegisterCandidateModel):

    existing = supabase.table("candidates").select("*").eq("email", data.email).execute().data
    if existing:
        return {"message": "El candidato ya existe", "id": existing[0]["id"]}

    result = supabase.table("candidates").insert({
        "email": data.email,
        "first_name": data.first_name,
        "last_name": data.last_name
    }).execute()

    return {"message": "Candidato registrado", "id": result.data[0]["id"]}

# ============================================================================
# INICIAR ENTREVISTA
# ============================================================================
@app.post("/start_interview/{candidate_id}")
def start_interview(candidate_id: str, role: str = Body(..., embed=True)):

    interview = supabase.table("interviews").insert({
        "candidate_id": candidate_id,
        "role_applied": role
    }).execute()

    return {
        "message": "Entrevista iniciada",
        "interview_id": interview.data[0]["id"]
    }

# ============================================================================
# GENERAR PREGUNTAS CON IA
# ============================================================================
@app.post("/generate_questions_for_role")
def generate_questions_for_role(role: str = Body(..., embed=True)):

    existing_q = supabase.table("questions").select("*").eq("role", role).execute().data

    if len(existing_q) >= 5:
        return {"message": "Preguntas encontradas", "questions": existing_q}

    prompt = f"""
    Genera 5 preguntas técnicas para una entrevista del rol: {role}.
    Devuelve formato JSON:
    {{
      "questions": [
        "Pregunta 1...",
        "Pregunta 2...",
        "Pregunta 3...",
        "Pregunta 4...",
        "Pregunta 5..."
      ]
    }}
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        json=payload
    )

    generated = json.loads(response.json()["choices"][0]["message"]["content"])
    questions_list = generated["questions"]

    inserted = []
    for q in questions_list:
        res = supabase.table("questions").insert({
            "role": role,
            "content": q
        }).execute()
        inserted.append(res.data[0])

    return {"message": "Preguntas generadas", "questions": inserted}

# ============================================================================
# SIGUIENTE PREGUNTA
# ============================================================================
@app.get("/next_question/{interview_id}")
def next_question(interview_id: str):

    interview = supabase.table("interviews").select("*").eq("id", interview_id).execute().data[0]
    role = interview["role_applied"]

    all_questions = supabase.table("questions").select("*").eq("role", role).execute().data
    answered = supabase.table("answers").select("question_id").eq("interview_id", interview_id).execute().data
    answered_ids = {q["question_id"] for q in answered}

    for q in all_questions:
        if q["id"] not in answered_ids:
            return q

    return {"message": "No hay más preguntas"}

# ============================================================================
# SUBIR AUDIO → WHISPER → TEXTO
# ============================================================================
@app.post("/submit_answer")
async def submit_answer(
    interview_id: str = Form(...),
    question_id: str = Form(...),
    audio: UploadFile = File(...)
):

    temp_filename = f"tmp_{uuid.uuid4()}.wav"

    async with aiofiles.open(temp_filename, 'wb') as f:
        await f.write(await audio.read())

    whisper_url = "https://api.openai.com/v1/audio/transcriptions"

    with open(temp_filename, "rb") as f:
        response = requests.post(
            whisper_url,
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            files={"file": f},
            data={"model": "whisper-1"}
        )

    os.remove(temp_filename)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error en transcripción")

    transcript = response.json()["text"]

    supabase.table("answers").insert({
        "interview_id": interview_id,
        "question_id": question_id,
        "transcript": transcript
    }).execute()

    return {"transcript": transcript}

# ============================================================================
# EVALUAR RESPUESTA CON IA
# ============================================================================
@app.post("/evaluate_answer")
def evaluate_answer(answer_id: str = Body(..., embed=True)):

    answer = supabase.table("answers").select("*").eq("id", answer_id).execute().data[0]
    question = supabase.table("questions").select("*").eq("id", answer["question_id"]).execute().data[0]

    prompt = f"""
    Evalúa esta respuesta:
    Pregunta: {question['content']}
    Respuesta: {answer['transcript']}
    Devuelve JSON:
    {{
      "score": X,
      "feedback": "texto"
    }}
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        json=payload
    )

    result_json = json.loads(response.json()["choices"][0]["message"]["content"])

    supabase.table("answer_scores").insert({
        "answer_id": answer_id,
        "score": result_json["score"],
        "feedback": result_json["feedback"]
    }).execute()

    return result_json

# ============================================================================
# FINALIZAR ENTREVISTA
# ============================================================================
@app.post("/finish_interview/{interview_id}")
def finish_interview(interview_id: str):

    # Obtener solo los scores de esta entrevista usando JOIN
    scores_response = (
        supabase.table("answer_scores")
        .select("score, answers!inner(interview_id)")
        .eq("answers.interview_id", interview_id)
        .execute()
    )

    scores = scores_response.data

    if not scores:
        return {"message": "No hay respuestas evaluadas"}

    avg = sum([s["score"] for s in scores]) / len(scores)

    supabase.table("interviews").update({
        "final_score": avg,
        "end_time": datetime.utcnow()
    }).eq("id", interview_id).execute()

    return {"message": "Entrevista finalizada", "final_score": avg}

