# AI Playground - Setup Instructions

Multi-modal AI application with Image Analysis, Document Summarization, and Conversation Analysis capabilities.

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (3.12 or higher)
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Blink29/Plivo_multi_tasks_ai_bot.git
cd Plivo_multi_tasks_ai_bot
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
```

**Edit `.env` file and add your API key:**
```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Start backend server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

**Open new terminal:**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000

## Login Credentials

- **Admin**: `admin@plivo.com` / `admin123`
- **User**: `user@plivo.com` / `user123`
- **Test**: `test@test.com` / `test123`

## Deployment

### Backend (Render)
1. Connect your GitHub repo to Render
2. Select the `backend` folder as root directory
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Environment**: Add `GEMINI_API_KEY` environment variable

### Frontend (Vercel)
1. Connect your GitHub repo to Vercel
2. Select the `frontend` folder as root directory
3. Add environment variable:
   - **VITE_API_BASE_URL**: Your Render backend URL (e.g., `https://your-app.onrender.com`)
4. Update `backend/app/config.py` PROD_CORS_ORIGINS with your Vercel URL
