import os
import uuid
import json
import requests
import aiofiles
from datetime import datetime
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, Form, Body, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict

from app.services.database_service import (
    create_or_get_candidate,
    create_interview,
    complete_interview,
    save_questions,
    get_interview_questions,
    save_answer,
    get_interview,
    get_interview_results,
    get_all_interviews,
    get_interview_count,
    authenticate_admin,
    get_answer_count
)
from app.services.auth_service import create_access_token, verify_access_token
from app.services.config_service import read_env_config, update_env_config, validate_config_update

from app.model.interviewer import (
    generate_all_questions,
    transcribe_audio,
    evaluate_answer
)
from dotenv import load_dotenv

# ============================================================================
# CARGAR VARIABLES DE ENTORNO (.env) DESDE /backend
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

# ============================================================================
# LEER VARIABLES
# ============================================================================
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "10"))
QUESTION_TIMEOUT_SECONDS = int(os.getenv("QUESTION_TIMEOUT_SECONDS", "120"))

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
class StartInterviewRequest(BaseModel):
    email: EmailStr
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ConfigUpdateRequest(BaseModel):
    MAX_QUESTIONS: Optional[int] = None
    QUESTION_TIMEOUT_SECONDS: Optional[int] = None


# ============================================================================
# DEPENDENCY: AUTH
# ============================================================================
def get_current_admin(authorization: Optional[str] = Header(None)):
    """Dependency to get current admin from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    return {
        "message": "AI Interview Backend API",
        "max_questions": MAX_QUESTIONS,
        "question_timeout_seconds": QUESTION_TIMEOUT_SECONDS,
        "llm_provider": os.getenv("LLM_PROVIDER", "gemini")
    }


@app.post("/ai/start-interview")
async def start_interview(data: StartInterviewRequest):
    """
    Start a new interview: create candidate, generate questions, save to DB
    """
    try:
        print(f"Starting interview for role: {data.role}, email: {data.email}")
        
        # Create or get candidate
        candidate = create_or_get_candidate(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name
        )
        print(f"Candidate created/retrieved: {candidate['id']}")
        
        # Generate all questions at once
        questions = generate_all_questions(data.role, MAX_QUESTIONS)
        print(f"Generated {len(questions)} questions")
        
        # Create interview in database
        interview = create_interview(candidate["id"], data.role)
        interview_id = interview["id"]
        print(f"Created interview with ID: {interview_id}")
        
        # Save questions to database
        saved_questions = save_questions(interview_id, data.role, questions)
        print(f"Saved {len(saved_questions)} questions to database")
        
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
    if interview.get("end_time"):
        return {
            "question": None,
            "completed": True,
            "message": "Interview completed"
        }
    
    # Get all questions for this interview
    questions = get_interview_questions(interview_id)
    
    # Get count of submitted answers
    answer_count = get_answer_count(interview_id)
    
    # Check if all questions answered
    if answer_count >= len(questions):
        return {
            "question": None,
            "completed": True,
            "message": "All questions answered"
        }
    
    # Get next question (index = answer_count)
    if answer_count < len(questions):
        next_q = questions[answer_count]
        return {
            "question": next_q["content"],
            "question_number": answer_count + 1,
            "total_questions": len(questions),
            "completed": False
        }
    
    return {
        "question": None,
        "completed": True,
        "message": "No more questions"
    }


@app.post("/ai/submit-answer/{interview_id}")
async def submit_interview_answer(interview_id: str, file: UploadFile = File(...)):
    """
    Submit an answer: transcribe audio, evaluate, save to DB
    """
    interview = get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    if interview.get("end_time"):
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    try:
        # Get all questions
        questions = get_interview_questions(interview_id)
        
        # Get current question index
        answer_count = get_answer_count(interview_id)
        
        if answer_count >= len(questions):
            raise HTTPException(status_code=400, detail="All questions already answered")
        
        current_question_obj = questions[answer_count]
        current_question_text = current_question_obj["content"]
        current_question_id = current_question_obj["id"]
        
        # Read audio file
        audio_bytes = await file.read()
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "answer.webm"
        
        # Transcribe audio using Whisper
        transcription = transcribe_audio(audio_file)
        
        # Evaluate answer using LLM
        evaluation = evaluate_answer(current_question_text, transcription)
        
        # Save answer to database
        saved_answer = save_answer(
            interview_id=interview_id,
            question_id=current_question_id,
            transcript=transcription,
            score=evaluation["score"],
            feedback=evaluation["reasoning"]
        )
        
        # Check if this was the last question
        new_answer_count = answer_count + 1
        interview_complete = new_answer_count >= len(questions)
        
        # If complete, update interview
        if interview_complete:
            # Calculate total score
            from app.services.database_service import get_interview_answers
            all_answers = get_interview_answers(interview_id)
            total_score = sum(ans["score"] or 0 for ans in all_answers)
            complete_interview(interview_id, total_score)
        
        # Get next question if available
        next_q = None
        if new_answer_count < len(questions):
            next_q = questions[new_answer_count]["content"]
        
        return {
            "transcription": transcription,
            "score": evaluation["score"],
            "reasoning": evaluation["reasoning"],
            "next_question": next_q,
            "completed": interview_complete
        }
        
    except Exception as e:
        print(f"Error processing answer: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")


@app.get("/ai/interview-results/{interview_id}")
def get_results(interview_id: str):
    """
    Get complete interview results from database
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
    
    # Get current question
    questions = get_interview_questions(interview_id)
    answer_count = get_answer_count(interview_id)
    
    if answer_count >= len(questions):
        raise HTTPException(status_code=400, detail="No current question")
    
    current_question = questions[answer_count]["content"]
    
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


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/admin/login")
async def admin_login(data: AdminLoginRequest):
    """
    Admin login endpoint - returns JWT token
    """
    try:
        admin = authenticate_admin(data.email, data.password)
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token_data = {
            "id": str(admin["id"]),
            "email": admin["email"]
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": admin
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/api/admin/interviews")
async def list_interviews(
    page: int = 1,
    limit: int = 20,
    role: Optional[str] = None,
    email: Optional[str] = None,
    admin=Depends(get_current_admin)
):
    """
    Get all interviews with pagination and filters (admin only)
    """
    try:
        offset = (page - 1) * limit
        
        filters = {}
        if role:
            filters["role"] = role
        if email:
            filters["email"] = email
        
        interviews = get_all_interviews(limit=limit, offset=offset, filters=filters)
        total_count = get_interview_count(filters=filters)
        
        return {
            "interviews": interviews,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
    except Exception as e:
        print(f"Error fetching interviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching interviews")


@app.get("/api/admin/interviews/{interview_id}")
async def get_interview_detail(
    interview_id: str,
    admin=Depends(get_current_admin)
):
    """
    Get detailed interview data (admin only)
    """
    results = get_interview_results(interview_id)
    if not results:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return results


@app.get("/api/admin/config")
async def get_config(admin=Depends(get_current_admin)):
    """
    Get current configuration (admin only)
    """
    try:
        config = read_env_config()
        
        return {
            "MAX_QUESTIONS": config.get("MAX_QUESTIONS", "10"),
            "QUESTION_TIMEOUT_SECONDS": config.get("QUESTION_TIMEOUT_SECONDS", "120")
        }
    except Exception as e:
        print(f"Error reading config: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading configuration")


@app.put("/api/admin/config")
async def update_config(
    data: ConfigUpdateRequest,
    admin=Depends(get_current_admin)
):
    """
    Update configuration (admin only)
    """
    try:
        updates = {}
        
        if data.MAX_QUESTIONS is not None:
            updates["MAX_QUESTIONS"] = str(data.MAX_QUESTIONS)
        
        if data.QUESTION_TIMEOUT_SECONDS is not None:
            updates["QUESTION_TIMEOUT_SECONDS"] = str(data.QUESTION_TIMEOUT_SECONDS)
        
        # Validate updates
        is_valid, error_msg = validate_config_update(updates)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Apply updates
        success = update_env_config(updates)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update configuration")
        
        # Reload environment variables (for current process)
        global MAX_QUESTIONS, QUESTION_TIMEOUT_SECONDS
        if "MAX_QUESTIONS" in updates:
            MAX_QUESTIONS = int(updates["MAX_QUESTIONS"])
        if "QUESTION_TIMEOUT_SECONDS" in updates:
            QUESTION_TIMEOUT_SECONDS = int(updates["QUESTION_TIMEOUT_SECONDS"])
        
        return {
            "message": "Configuration updated successfully",
            "config": updates
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating configuration")
