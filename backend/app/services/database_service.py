"""
Database service layer for AI Interviewer
Handles all database operations using Supabase
"""
import os
from typing import Optional, Dict, List
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import bcrypt

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# CANDIDATE OPERATIONS
# ============================================================================

def create_or_get_candidate(email: str, first_name: str = None, last_name: str = None) -> Dict:
    """
    Create a new candidate or get existing one by email
    
    Args:
        email: Candidate email
        first_name: First name (optional)
        last_name: Last name (optional)
    
    Returns:
        Dict with candidate data including id
    """
    # Check if candidate already exists
    existing = supabase.table("candidates").select("*").eq("email", email).execute()
    
    if existing.data and len(existing.data) > 0:
        # Update names if provided
        if first_name or last_name:
            update_data = {}
            if first_name:
                update_data["first_name"] = first_name
            if last_name:
                update_data["last_name"] = last_name
            
            if update_data:
                updated = supabase.table("candidates").update(update_data).eq("email", email).execute()
                return updated.data[0]
        
        return existing.data[0]
    
    # Create new candidate
    candidate_data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name
    }
    
    result = supabase.table("candidates").insert(candidate_data).execute()
    return result.data[0]


def get_candidate_by_id(candidate_id: str) -> Optional[Dict]:
    """Get candidate by ID"""
    result = supabase.table("candidates").select("*").eq("id", candidate_id).execute()
    return result.data[0] if result.data else None


# ============================================================================
# INTERVIEW OPERATIONS
# ============================================================================

def create_interview(candidate_id: str, role: str) -> Dict:
    """
    Create a new interview session
    
    Args:
        candidate_id: UUID of the candidate
        role: Job role for the interview
    
    Returns:
        Dict with interview data including id
    """
    interview_data = {
        "candidate_id": candidate_id,
        "role_applied": role,
        "start_time": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("interviews").insert(interview_data).execute()
    return result.data[0]


def get_interview(interview_id: str) -> Optional[Dict]:
    """Get interview by ID with candidate data"""
    result = supabase.table("interviews").select(
        "*, candidates(*)"
    ).eq("id", interview_id).execute()
    
    return result.data[0] if result.data else None


def complete_interview(interview_id: str, final_score: float):
    """
    Mark interview as complete and update final score
    
    Args:
        interview_id: Interview UUID
        final_score: Total score from all answers
    """
    update_data = {
        "end_time": datetime.utcnow().isoformat(),
        "final_score": final_score
    }
    
    supabase.table("interviews").update(update_data).eq("id", interview_id).execute()


def get_all_interviews(limit: int = 50, offset: int = 0, filters: Dict = None) -> List[Dict]:
    """
    Get all interviews with pagination and filters
    
    Args:
        limit: Number of records to return
        offset: Number of records to skip
        filters: Optional filters (role, email, etc.)
    
    Returns:
        List of interview records with candidate data
    """
    query = supabase.table("interviews").select(
        "*, candidates(*)"
    ).order("created_at", desc=True)
    
    if filters:
        if "role" in filters and filters["role"]:
            query = query.eq("role_applied", filters["role"])
        if "email" in filters and filters["email"]:
            query = query.filter("candidates.email", "ilike", f"%{filters['email']}%")
    
    query = query.range(offset, offset + limit - 1)
    result = query.execute()
    
    return result.data


def get_interview_count(filters: Dict = None) -> int:
    """Get total count of interviews (for pagination)"""
    query = supabase.table("interviews").select("id", count="exact")
    
    if filters:
        if "role" in filters and filters["role"]:
            query = query.eq("role_applied", filters["role"])
    
    result = query.execute()
    return result.count


# ============================================================================
# QUESTION OPERATIONS
# ============================================================================

def save_questions(interview_id: str, role: str, questions: List[str]) -> List[Dict]:
    """
    Save multiple questions for an interview
    
    Args:
        interview_id: Interview UUID
        role: Job role
        questions: List of question strings
    
    Returns:
        List of created question records
    """
    questions_data = []
    for idx, question_text in enumerate(questions):
        questions_data.append({
            "interview_id": interview_id,
            "role": role,
            "content": question_text,
            "question_order": idx + 1
        })
    
    result = supabase.table("questions").insert(questions_data).execute()
    return result.data


def get_interview_questions(interview_id: str) -> List[Dict]:
    """Get all questions for an interview in order"""
    result = supabase.table("questions").select("*").eq(
        "interview_id", interview_id
    ).order("question_order").execute()
    
    return result.data


def get_question_by_id(question_id: str) -> Optional[Dict]:
    """Get a specific question by ID"""
    result = supabase.table("questions").select("*").eq("id", question_id).execute()
    return result.data[0] if result.data else None


# ============================================================================
# ANSWER OPERATIONS
# ============================================================================

def save_answer(
    interview_id: str,
    question_id: str,
    transcript: str,
    score: float,
    feedback: str
) -> Dict:
    """
    Save a candidate's answer with evaluation
    
    Args:
        interview_id: Interview UUID
        question_id: Question UUID
        transcript: Transcribed answer text
        score: Evaluation score (1-5)
        feedback: LLM evaluation feedback
    
    Returns:
        Created answer record
    """
    answer_data = {
        "interview_id": interview_id,
        "question_id": question_id,
        "transcript": transcript,
        "score": score,
        "feedback": feedback
    }
    
    result = supabase.table("answers").insert(answer_data).execute()
    return result.data[0]


def get_interview_answers(interview_id: str) -> List[Dict]:
    """Get all answers for an interview with question data"""
    result = supabase.table("answers").select(
        "*, questions(*)"
    ).eq("interview_id", interview_id).order("created_at").execute()
    
    return result.data


def get_answer_count(interview_id: str) -> int:
    """Get count of answers submitted for an interview"""
    result = supabase.table("answers").select("id", count="exact").eq(
        "interview_id", interview_id
    ).execute()
    
    return result.count or 0


# ============================================================================
# INTERVIEW RESULTS
# ============================================================================

def get_interview_results(interview_id: str) -> Optional[Dict]:
    """
    Get complete interview results with all data
    
    Returns:
        Dict with interview, candidate, questions, and answers
    """
    # Get interview with candidate
    interview = get_interview(interview_id)
    if not interview:
        return None
    
    # Get all questions
    questions = get_interview_questions(interview_id)
    
    # Get all answers
    answers = get_interview_answers(interview_id)
    
    # Calculate statistics
    total_questions = len(questions)
    answers_submitted = len(answers)
    total_score = sum(answer["score"] or 0 for answer in answers)
    max_possible_score = total_questions * 5
    average_score = total_score / total_questions if total_questions > 0 else 0
    
    return {
        "interview_id": interview_id,
        "candidate": interview.get("candidates"),
        "role": interview.get("role_applied"),
        "start_time": interview.get("start_time"),
        "end_time": interview.get("end_time"),
        "status": "completed" if interview.get("end_time") else "in_progress",
        "questions": questions,
        "answers": answers,
        "statistics": {
            "total_questions": total_questions,
            "answers_submitted": answers_submitted,
            "total_score": round(total_score, 2),
            "max_possible_score": max_possible_score,
            "average_score": round(average_score, 2),
            "completion_percentage": round((answers_submitted / total_questions * 100) if total_questions > 0 else 0, 2)
        }
    }


# ============================================================================
# ADMIN OPERATIONS
# ============================================================================

def authenticate_admin(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate admin user
    
    Args:
        email: Admin email
        password: Plain text password
    
    Returns:
        Admin user dict if authenticated, None otherwise
    """
    result = supabase.table("admins").select("*").eq("email", email).execute()
    
    if not result.data or len(result.data) == 0:
        return None
    
    admin = result.data[0]
    password_hash = admin.get("password_hash")
    
    # Verify password
    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        # Return admin data without password hash
        return {
            "id": admin["id"],
            "email": admin["email"],
            "created_at": admin.get("created_at")
        }
    
    return None


def create_admin(email: str, password: str) -> Dict:
    """
    Create a new admin user
    
    Args:
        email: Admin email
        password: Plain text password (will be hashed)
    
    Returns:
        Created admin record (without password hash)
    """
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    admin_data = {
        "email": email,
        "password_hash": password_hash.decode('utf-8')
    }
    
    result = supabase.table("admins").insert(admin_data).execute()
    
    # Return without password hash
    admin = result.data[0]
    return {
        "id": admin["id"],
        "email": admin["email"],
        "created_at": admin.get("created_at")
    }


def get_admin_by_email(email: str) -> Optional[Dict]:
    """Get admin by email (without password hash)"""
    result = supabase.table("admins").select("id, email, created_at").eq("email", email).execute()
    return result.data[0] if result.data else None
