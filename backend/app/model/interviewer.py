import os
from typing import List, Dict
from openai import OpenAI
from app.model.llm_client import call_llm

# Initialize Groq client for Whisper (audio transcription)
# Groq provides free Whisper large v3
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment. Audio transcription will fail.")
    print("Please add GROQ_API_KEY to your .env file.")
    groq_client = None
else:
    groq_client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

# Interview prompts
INTERVIEWER_SYSTEM_PROMPT = (
    "You are an expert AI interviewer that is interacting with a user "
    "that is applying for the role of {role}. Your task is to ask questions "
    "to know if the person being interviewed is suitable for the job. "
    "If there is no prior context, start with an initial question."
)

EVALUATOR_SYSTEM_PROMPT = """You are an Expert Technical Interviewer and Evaluator.

Your task is to evaluate a candidate's answer based on a specific question. You must analyze the quality, depth, and precision of the response using the strict scoring rubric defined below.

### Scoring Rubric (1-5 Scale)

* **1 - Incorrect:** Totally irrelevant, wrong, nonsensical, or vague. The answer does not address the question at all.
* **2 - Partial:** Mentions something related to the topic but lacks clarity, depth, or misses key points.
* **3 - Acceptable:** Correct but basic, generic, or shallow. It lacks concrete examples or demonstrates only surface-level knowledge.
* **4 - Good:** Clear, relevant, detailed, and professional. The candidate shows reasoning or method behind the answer.
* **5 - Excellent:** Very complete, thoughtful, structured, and insightful. The answer provides concrete examples, shows deep understanding, and is perfectly articulated.

### Output Requirement
You must output the evaluation in a strict format to allow for automated processing and variable storage. Do not add introductory text.

Format strictly as follows:
SCORE: <Integer 1-5>
REASONING: <Brief explanation of why this score was given>"""


def generate_all_questions(role: str, num_questions: int) -> List[str]:
    """
    Generate all interview questions at once using LLM
    
    Args:
        role: The job role being interviewed for
        num_questions: Number of questions to generate
    
    Returns:
        List of question strings
    """
    messages = [
        {
            "role": "system",
            "content": INTERVIEWER_SYSTEM_PROMPT.format(role=role)
        },
        {
            "role": "user",
            "content": f"Generate exactly {num_questions} interview questions for the {role} position. "
                      f"These questions should progressively assess technical skills, problem-solving abilities, "
                      f"and professional experience. Return ONLY the questions, one per line, numbered 1-{num_questions}."
        }
    ]
    
    response = call_llm(messages, temperature=0.8)
    
    # Parse the response to extract questions
    lines = response.strip().split('\n')
    questions = []
    
    for line in lines:
        # Remove numbering (handles "1.", "1)", "1 -", etc.)
        line = line.strip()
        if line:
            # Remove common numbering patterns
            import re
            clean_line = re.sub(r'^\d+[\.\)\-\:]\s*', '', line)
            if clean_line:
                questions.append(clean_line)
    
    # Ensure we have exactly num_questions
    if len(questions) < num_questions:
        # If we got fewer, pad with generic questions
        for i in range(len(questions), num_questions):
            questions.append(f"Tell me about your experience relevant to this {role} position.")
    
    return questions[:num_questions]


def transcribe_audio(audio_file) -> str:
    """
    Transcribe audio to text using Groq Whisper Large v3 (free)
    
    Args:
        audio_file: Audio file object
    
    Returns:
        str: Transcribed text
    """
    if not groq_client:
        raise ValueError(
            "GROQ_API_KEY not configured. Please add GROQ_API_KEY to your .env file. "
            "Get your free API key at: https://console.groq.com/keys"
        )
    
    transcript = groq_client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=audio_file
    )
    return transcript.text


def evaluate_answer(question: str, answer: str) -> Dict[str, any]:
    """
    Evaluate an answer using LLM with scoring rubric
    
    Args:
        question: The interview question
        answer: The candidate's answer
    
    Returns:
        Dict with 'score' (int) and 'reasoning' (str)
    """
    messages = [
        {
            "role": "system",
            "content": EVALUATOR_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"**Question:** {question}\n**Candidate Answer:** {answer}"
        }
    ]
    
    response = call_llm(messages, temperature=0.3)
    
    # Parse the response to extract score and reasoning
    score = None
    reasoning = ""
    
    lines = response.strip().split('\n')
    for line in lines:
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except:
                score = 3  # Default to acceptable if parsing fails
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()
    
    # Default values if parsing failed
    if score is None:
        score = 3
    if not reasoning:
        reasoning = "Unable to parse evaluation response properly."
    
    return {
        "score": score,
        "reasoning": reasoning
    }
