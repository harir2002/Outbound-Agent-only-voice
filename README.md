# 🏦 BFSI Outbound AI Voice Agent

An enterprise-grade, lightweight outbound voice campaign manager designed for BFSI (Banking, Financial Services, and Insurance). This agent automates high-quality, multilingual voice calls for SIP reminders, KYC updates, and payment notifications using Sarvam AI and Twilio.

## 🚀 Features

- **High-Fidelity AI Voice**: Uses Sarvam AI (Bulbul:v2) for natural-sounding Indian voices in multiple languages (English, Hindi, Tamil, etc.).
- **Automated Campaigns**: 
  - **SIP Debit Reminders**: Notify investors of upcoming SIP deductions.
  - **KYC Update Alerts**: Streamline compliance with automated update reminders.
  - **SIP Failure Notifications**: Promptly inform users about transaction failures.
- **Lightweight Architecture**: Optimized for fast deployment on Hugging Face Spaces (Docker) and Vercel.
- **Zero Database Dependency**: Uses session-based handling for high performance and privacy.

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React (Vite)
- **Voice AI**: Sarvam AI
- **LLM**: Groq (Mixtral)
- **Communication**: Twilio Voice

## 📂 Project Structure

```text
├── backend/            # FastAPI Application
│   ├── app/            # Core logic & API routes
│   ├── Dockerfile      # Production build configuration
│   └── requirements.txt # Minimal dependencies
├── frontend/           # React Application
│   ├── src/            # UI Components & Pages
│   └── vercel.json     # Vercel deployment config
```

## ⚙️ Setup & Deployment

### Environment Variables (.env)

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq Cloud API Key |
| `SARVAM_API_KEY` | Sarvam AI API Key |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio outbound number |

### Local Development

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🌐 Deployment Instructions

### Backend (Hugging Face)
1. Create a new **Space** on Hugging Face.
2. Select **Docker** as the SDK.
3. Push the `backend/` code or point the Space to the GitHub repository.
4. Add the required `.env` variables in the Space settings.

### Frontend (Vercel)
1. Import the repository into Vercel.
2. Set the `frontend` folder as the **Root Directory**.
3. Add `VITE_API_URL` as an environment variable pointing to your backend URL.
4. Deploy!

---
Developed for **Sales Demo** efficiency. 🚀
