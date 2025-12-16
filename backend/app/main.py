import os
import uuid
import json
import requests
import aiofiles
from datetime import datetime
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import create_client
from app.state.interviews import (
    create_interview, 
    get_interview, 
    get_current_question,
    submit_answer,
    is_interview_complete,
    get_interview_results,
    MAX_QUESTIONS
)
from app.model.interviewer import (
    generate_all_questions,
    transcribe_audio,
    evaluate_answer
)
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

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("WARNING: Supabase not configured")

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
# MODELS
# ============================================================================
class RoleRequest(BaseModel):
    role: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    return {
        "message": "AI Interview Backend API",
        "max_questions": MAX_QUESTIONS,
        "question_timeout_seconds": int(os.getenv("QUESTION_TIMEOUT_SECONDS", "120")),
        "llm_provider": os.getenv("LLM_PROVIDER", "gemini")
    }


@app.post("/ai/start-interview")
async def start_interview(data: RoleRequest):
    """
    Start a new interview: generate all questions using LLM
    """
    try:
        print(f"Starting interview for role: {data.role}")
        print(f"MAX_QUESTIONS: {MAX_QUESTIONS}")
        
        # Generate all questions at once
        print("Calling generate_all_questions...")
        questions = generate_all_questions(data.role, MAX_QUESTIONS)
        print(f"Generated {len(questions)} questions")
        
        # Create interview with questions
        interview_id = create_interview(data.role, questions)
        print(f"Created interview with ID: {interview_id}")
        
        # Return interview ID and first question
        return {
            "interview_id": interview_id,
            "first_question": questions[0],
            "total_questions": len(questions),
            "role": data.role
        }
    except Exception as e:
        print(f"ERROR in start_interview: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")


@app.get("/ai/next-question/{interview_id}")
def next_question(interview_id: str):
    """
    Get the next question in the interview
    """
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check if interview is complete
    if is_interview_complete(interview_id):
        return {
            "question": None,
            "completed": True,
            "message": "Interview completed"
        }
    
    # Get current question
    question = get_current_question(interview_id)
    if not question:
        return {
            "question": None,
            "completed": True,
            "message": "No more questions"
        }
    
    current_index = interview["current_question_index"]
    total = interview["max_questions"]
    
    return {
        "question": question,
        "question_number": current_index + 1,
        "total_questions": total,
        "completed": False
    }


@app.post("/ai/submit-answer/{interview_id}")
async def submit_interview_answer(interview_id: str, file: UploadFile = File(...)):
    """
    Submit an answer: transcribe audio, evaluate, and score
    """
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if is_interview_complete(interview_id):
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    try:
        # Get current question
        current_question = get_current_question(interview_id)
        if not current_question:
            raise HTTPException(status_code=400, detail="No current question")
        
        # Read audio file
        audio_bytes = await file.read()
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "answer.webm"
        
        # Transcribe audio using Whisper
        transcription = transcribe_audio(audio_file)
        
        # Evaluate answer using LLM
        evaluation = evaluate_answer(current_question, transcription)
        
        # Submit answer to interview state
        success = submit_answer(
            interview_id,
            transcription,
            evaluation["score"],
            evaluation["reasoning"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to submit answer")
        
        # Check if there's a next question
        next_q = get_current_question(interview_id)
        interview_complete = is_interview_complete(interview_id)
        
        return {
            "transcription": transcription,
            "score": evaluation["score"],
            "reasoning": evaluation["reasoning"],
            "next_question": next_q,
            "completed": interview_complete
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")


@app.get("/ai/interview-results/{interview_id}")
def get_results(interview_id: str):
    """
    Get complete interview results
    """
    results = get_interview_results(interview_id)
    if not results:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return results


@app.get("/ai/question-audio/{interview_id}")
async def get_question_audio(interview_id: str):
    """
    Get TTS audio for the current question using gTTS (Google Text-to-Speech)
    """
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    current_question = get_current_question(interview_id)
    if not current_question:
        raise HTTPException(status_code=400, detail="No current question")
    
    try:
        from gtts import gTTS
        import tempfile
        import hashlib
        
        # Create cache directory for TTS audio
        cache_dir = "/tmp/tts_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate a hash of the question for caching
        question_hash = hashlib.md5(current_question.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{question_hash}.mp3")
        
        # Check if audio is already cached
        if not os.path.exists(cache_file):
            # Generate TTS audio using gTTS with US English accent
            tts = gTTS(text=current_question, lang='en', tld='us', slow=False)
            tts.save(cache_file)
        
        # Read and return the audio file
        with open(cache_file, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        return StreamingResponse(
            BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": "inline"
            }
        )
        
    except Exception as e:
        import traceback
        print(f"Error generating TTS: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating TTS: {str(e)}")
