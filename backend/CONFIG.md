# AI-Assisted Interviewer - Configuration Guide

## Environment Variables

### Required Configuration

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Supabase (optional for now, prepared for future)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# LLM Configuration
# Choose either "gemini" or "openai"
LLM_PROVIDER=gemini

# API Keys - provide the one matching your LLM_PROVIDER
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Groq API Key (for free Whisper large v3 transcription)
GROQ_API_KEY=your_groq_api_key_here

# Interview Configuration
# Easily change the number of questions per interview
MAX_QUESTIONS=10
```

## LLM Provider Setup

### Option 1: Google Gemini (Recommended)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Set `LLM_PROVIDER=gemini` in your `.env`
4. Add your key to `GEMINI_API_KEY`

### Option 2: OpenAI GPT
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key
3. Set `LLM_PROVIDER=openai` in your `.env`
4. Add your key to `OPENAI_API_KEY`

### Audio Transcription - Groq (Required, Free)
1. Go to [Groq Console](https://console.groq.com/keys)
2. Create an API key
3. Add it to `GROQ_API_KEY` in your `.env`

**Note:** Groq provides FREE access to Whisper Large v3 for audio transcription - much faster than OpenAI!

## Features

### Question Generation
- LLM generates all interview questions at the start based on the selected role
- Configurable via `MAX_QUESTIONS` environment variable
- Default: 10 questions

### Audio Transcription
- Uses OpenAI Whisper API to convert audio to text
- High accuracy for multiple languages

### Answer Evaluation
- Uses LLM with a 1-5 scoring rubric:
  - 1 - Incorrect
  - 2 - Partial
  - 3 - Acceptable
  - 4 - Good
  - 5 - Excellent
- Provides detailed reasoning for each score

### Text-to-Speech (Optional)
- Edge TTS for question audio
- Endpoint: `/ai/question-audio/{interview_id}`

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Running the Application

### Using Docker (Backend)
```bash
cd backend
docker compose up --build
```

### Manual (Backend)
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## Changing Number of Questions

Simply update the `MAX_QUESTIONS` value in your `.env` file:

```bash
# For 5 questions
MAX_QUESTIONS=5

# For 20 questions
MAX_QUESTIONS=20
```

Restart the backend server after changing.

## API Endpoints

- `POST /ai/start-interview` - Start interview and generate questions
- `GET /ai/next-question/{interview_id}` - Get next question
- `POST /ai/submit-answer/{interview_id}` - Submit audio answer
- `GET /ai/interview-results/{interview_id}` - Get complete results
- `GET /ai/question-audio/{interview_id}` - Get TTS audio (optional)

## Future Database Integration

The system is prepared for Supabase integration. Schema design is documented in the codebase for future implementation.
