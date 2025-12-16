import uuid
import os
from typing import Dict, Optional

# In-memory storage for interviews
_interviews = {}

# Get configurable max questions from environment
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "10"))


def create_interview(role: str, questions: list) -> str:
    """
    Create a new interview with pre-generated questions
    
    Args:
        role: The job role
        questions: List of pre-generated questions
    
    Returns:
        str: Interview ID
    """
    interview_id = str(uuid.uuid4())
    
    _interviews[interview_id] = {
        "role": role,
        "questions": questions,
        "current_question_index": 0,
        "answers": [],
        "total_score": 0,
        "max_questions": len(questions),
        "status": "in_progress"
    }
    
    return interview_id


def get_interview(interview_id: str) -> Optional[Dict]:
    """Get interview by ID"""
    return _interviews.get(interview_id)


def get_current_question(interview_id: str) -> Optional[str]:
    """
    Get the current question for an interview
    
    Returns:
        str or None: Current question or None if interview is complete
    """
    interview = _interviews.get(interview_id)
    if not interview:
        return None
    
    index = interview["current_question_index"]
    if index >= len(interview["questions"]):
        return None
    
    return interview["questions"][index]


def submit_answer(interview_id: str, transcription: str, score: int, reasoning: str) -> bool:
    """
    Submit an answer for the current question
    
    Args:
        interview_id: Interview ID
        transcription: Transcribed answer text
        score: Score (1-5)
        reasoning: Evaluation reasoning
    
    Returns:
        bool: True if successful, False otherwise
    """
    interview = _interviews.get(interview_id)
    if not interview:
        return False
    
    current_q_index = interview["current_question_index"]
    if current_q_index >= len(interview["questions"]):
        return False
    
    # Store the answer
    interview["answers"].append({
        "question": interview["questions"][current_q_index],
        "transcription": transcription,
        "score": score,
        "reasoning": reasoning
    })
    
    # Update total score
    interview["total_score"] += score
    
    # Move to next question
    interview["current_question_index"] += 1
    
    # Check if interview is complete
    if interview["current_question_index"] >= interview["max_questions"]:
        interview["status"] = "completed"
    
    return True


def is_interview_complete(interview_id: str) -> bool:
    """Check if interview is complete"""
    interview = _interviews.get(interview_id)
    if not interview:
        return False
    
    return interview["status"] == "completed"


def get_interview_results(interview_id: str) -> Optional[Dict]:
    """
    Get complete interview results
    
    Returns:
        Dict with questions, answers, scores, and statistics
    """
    interview = _interviews.get(interview_id)
    if not interview:
        return None
    
    max_possible_score = interview["max_questions"] * 5
    average_score = interview["total_score"] / interview["max_questions"] if interview["max_questions"] > 0 else 0
    
    return {
        "role": interview["role"],
        "status": interview["status"],
        "questions": interview["questions"],
        "answers": interview["answers"],
        "total_score": interview["total_score"],
        "max_possible_score": max_possible_score,
        "average_score": round(average_score, 2),
        "questions_answered": len(interview["answers"]),
        "total_questions": interview["max_questions"]
    }
