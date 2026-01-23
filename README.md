# 🏦 BFSI AI Platform - WhatsApp & Voice AI Demo

## 🎯 Overview

Production-grade AI platform for BFSI companies (Banking, Insurance, NBFCs, Mutual Funds) featuring:

- **WhatsApp AI Assistant** - Automated customer support via Twilio
- **Outbound Voice AI** - Multilingual voice calls via Sarvam AI
- **RAG-Powered Intelligence** - Context-aware responses using ChromaDB
- **Regulatory Compliance** - GDPR, RBI, IRDAI aligned

## 🧠 Technology Stack

### AI & ML
- **LLM**: Groq (LLaMA 3.1 / Mixtral)
- **Vector DB**: ChromaDB
- **Embeddings**: BGE-Base-EN-v1.5
- **Voice AI**: Sarvam AI (TTS + STT)
- **WhatsApp**: Twilio Business API

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Queue**: Celery + Redis
- **Auth**: JWT
- **Database**: SQLite (dev) / PostgreSQL (prod)

### Frontend
- **Framework**: React.js 18
- **Styling**: Vanilla CSS
- **Build**: Vite

### DevOps
- **Containerization**: Docker + Docker Compose
- **Deployment**: Docker-ready

## 🎨 Brand Colors

```css
Primary: #000000 (Black)
Secondary: #e7000b (Red)
Text: #ffffff (White)
```

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── whatsapp.py      # Twilio WhatsApp webhook
│   │   │   ├── voice.py         # Sarvam voice calls
│   │   │   ├── rag.py           # RAG query endpoint
│   │   │   └── documents.py     # Document ingestion
│   │   ├── core/
│   │   │   ├── config.py        # Configuration
│   │   │   ├── security.py      # Auth & compliance
│   │   │   └── logging.py       # Audit logging
│   │   ├── services/
│   │   │   ├── groq_service.py  # Groq LLM integration
│   │   │   ├── rag_service.py   # ChromaDB RAG
│   │   │   ├── twilio_service.py # WhatsApp integration
│   │   │   ├── sarvam_service.py # Voice AI
│   │   │   └── compliance.py    # PII masking, consent
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys:
  - Groq API Key
  - Twilio Account SID & Auth Token
  - Sarvam API Key

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# Or on Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env

# Run development server
npm run dev

# Or build for production
npm run build
npm run preview
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Seed Sample Data

Visit http://localhost:3000 and click "Seed Sample Data" button to populate the knowledge base with BFSI demo data.

## 📱 Features

### 1️⃣ WhatsApp AI Assistant

- Auto-reply to customer messages
- RAG-powered FAQ responses
- Policy/loan document queries
- Payment link sharing
- Session memory per user
- Human escalation

### 2️⃣ Outbound Voice AI

- AI-initiated calls
- Multilingual (English + Hindi, Tamil, etc.)
- Use cases:
  - EMI reminders
  - Policy renewals
  - Loan offers
  - Claim updates
- Intent capture (Interested/Pay Now/Call Later/DND)

### 3️⃣ RAG Decision Engine

- Groq LLM for NLU
- ChromaDB vector search
- BFSI-safe responses
- Zero hallucination policy
- Structured JSON output

## 🔐 Security & Compliance

- ✅ PII masking before embedding
- ✅ WhatsApp opt-in tracking
- ✅ Call consent & recording disclosure
- ✅ GDPR / RBI / IRDAI alignment
- ✅ Audit-ready logging
- ✅ JWT authentication

## 📊 Demo Scenarios

1. **Insurance Policy Renewal** (RAG-based WhatsApp)
2. **Loan EMI Reminder** (Voice → WhatsApp)
3. **Credit Card Upgrade** (Outbound call)
4. **Claim Status Follow-up** (Document upload)

## 🧪 API Endpoints

```
POST /api/whatsapp/webhook       # Twilio WhatsApp incoming
POST /api/voice/outbound         # Initiate voice call
POST /api/rag/query              # RAG query
POST /api/documents/ingest       # Upload documents
POST /api/payments/link          # Generate payment link
GET  /api/analytics/calls        # Call analytics
```

## 📚 Documentation

- [Architecture Details](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Compliance Guide](./docs/COMPLIANCE.md)

## 🎯 Roadmap

- [ ] Multi-language support (10+ Indian languages)
- [ ] Advanced analytics dashboard
- [ ] CRM integration (Salesforce, Zoho)
- [ ] Voice biometrics
- [ ] Sentiment analysis

## 📄 License

Proprietary - BFSI Enterprise Demo

## 🤝 Support

For enterprise inquiries: contact@example.com
