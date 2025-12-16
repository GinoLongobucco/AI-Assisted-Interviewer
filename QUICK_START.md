# 🚀 Quick Start Guide - AI Interview System

## ⚠️ IMPORTANT: Configuration Required

Before running the system, you need to configure your API keys.

### Step 1: Configure Backend Environment

1. Navigate to the `backend/` directory
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** and add your API keys:

```bash
# Choose your LLM provider
LLM_PROVIDER=gemini  # or "openai"

# REQUIRED: Add your API key
GEMINI_API_KEY=your_actual_gemini_api_key_here
# OR
OPENAI_API_KEY=your_actual_openai_api_key_here

# ALSO REQUIRED: OpenAI key for Whisper (even if using Gemini)
OPENAI_API_KEY=your_actual_openai_api_key_here

# Interview configuration
MAX_QUESTIONS=10

# Supabase (optional for now)
SUPABASE_URL=
SUPABASE_KEY=
```

### Step 2: Get Your API Keys

#### For Google Gemini (Free Tier Available)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste it as `GEMINI_API_KEY` in your `.env`
5. Set `LLM_PROVIDER=gemini`

#### For OpenAI (Required for Whisper)
1. Go to: https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
4. Paste it as `OPENAI_API_KEY` in your `.env`

> **Note:** Even if you use Gemini for questions/scoring, you still need an OpenAI key for Whisper audio transcription.

### Step 3: Restart Backend

After configuring `.env`:

**If using Docker:**
```bash
cd backend
docker compose down
docker compose up --build
```

**If running manually:**
```bash
cd backend
uvicorn app.main:app --reload
```

### Step 4: Start Frontend

```bash
cd frontend
npm run dev
```

### Step 5: Test the System

1. Open browser to `http://localhost:3000`
2. Select a role (e.g., "Software Developer")
3. Click "Continuar"
4. Answer questions by recording audio
5. View your scores and results

---

## 🎛️ Customization

### Change Number of Questions

Edit `backend/.env`:
```bash
MAX_QUESTIONS=5   # Shorter interview
MAX_QUESTIONS=20  # Longer interview
```

Then restart the backend.

### Switch LLM Provider

Edit `backend/.env`:
```bash
# Use Google Gemini (free tier)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key

# OR use OpenAI GPT-4
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
```

Then restart the backend.

---

## 📝 System Features

✅ **LLM Question Generation** - AI generates role-specific questions  
✅ **Audio Recording** - Browser-based voice recording  
✅ **Whisper Transcription** - High-accuracy speech-to-text  
✅ **AI Evaluation** - 1-5 scoring with detailed reasoning  
✅ **Progress Tracking** - Real-time interview progress  
✅ **Results Dashboard** - Complete score breakdown  
✅ **Configurable** - Easily change question count  
✅ **Flexible LLM** - Choose Gemini or GPT  

---

## 🆘 Troubleshooting

### "API key not found" error
- Make sure you created `.env` from `.env.example`
- Verify API keys are correctly pasted (no extra spaces)
- Restart the backend after adding keys

### Docker container fails to start
- Run `docker compose down`
- Run `docker compose up --build` to rebuild
- Check logs: `docker compose logs backend`

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check: `http://localhost:8000` should show API info

### Audio recording not working
- Make sure you're using HTTPS or localhost
- Grant microphone permissions in browser

---

## 📚 Documentation

- [CONFIG.md](file:///c:/Users/jeana/Documents/GitHub/AI-Assisted-Interviewer/backend/CONFIG.md) - Detailed configuration guide
- [walkthrough.md](file:///C:/Users/jeana/.gemini/antigravity/brain/29d563a6-2421-44ec-add1-ce09cc7e23bf/walkthrough.md) - Complete implementation details

---

## 🔄 Current Status

✅ Backend implemented with LLM integration  
✅ Frontend with audio recording and results  
✅ Docker configuration ready  
⚠️ **Requires API key configuration before use**  
🔜 Database integration (prepared for future)
