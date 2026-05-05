# 🧬 Metabolic Health Coach

An autonomous AI agent designed to bridge the gap between wearable biometric data (Fitbit) and actionable metabolic health insights. Built using LangGraph, the system provides stateful, personalized guidance based on real-time user data.

---

## 📌 Problem

Modern health tracking tools provide abundant data (steps, calories, heart rate), but lack meaningful interpretation.  

Most users experience **data fatigue** — they have access to metrics but lack guidance on how to act on them.  

This project addresses that gap by acting as an intelligent system that interprets biometric data and provides context-aware health recommendations.

---

## ⚙️ Approach

### 🧠 Model
- Google Gemini (via LangChain integration)
- Optimized for reasoning and tool-calling

### 🔄 System Design

- **Agent Framework:** LangGraph (stateful graph-based orchestration)
- **Pipeline:** Agentic RAG with tool-calling
- **Capabilities:**
  - Fetch real-time Fitbit data
  - Log user food intake
  - Query historical trends
  - Provide contextual health recommendations

---

## 🤔 Why This Approach?

Unlike linear chatbot systems, a graph-based architecture enables **cyclic reasoning**:

- The agent evaluates the user’s metabolic state  
- Identifies missing context (e.g., heart rate trends)  
- Calls appropriate tools  
- Re-evaluates before generating a response  

This results in more reliable and context-aware recommendations.

---

## 🏗️ Architecture

The system is designed for scalability, reliability, and persistent state management.

- **Orchestration:** LangGraph (state + decision flow)
- **Backend:** FastAPI with asynchronous execution
- **Database:** PostgreSQL (Neon)
  - Connection pooling via `psycopg_pool`
  - LangGraph checkpoints for persistent memory
- **Deployment:** Dockerized container for consistent environments
- **Interface:** Telegram bot for real-time interaction

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/de84511c-e70e-441b-ad64-8f94fe0c6d63" />

---

## 📊 Results

### Integration
- Successfully integrated Fitbit OAuth2.0 for real-time biometric data retrieval

### State Persistence
- Implemented PostgreSQL-based checkpointing
- Maintains conversational context across sessions (~99% reliability)

### System Reliability
- Migrated from blocking script → non-blocking FastAPI server
- Supports continuous (24/7) operation

---

## ⚖️ Tradeoffs

### Context vs Latency
- Prioritized persistent state (PostgreSQL checkpoints)
- Slight increase in latency
- Significant improvement in contextual continuity

### Data Integrity vs Flexibility
- Chose PostgreSQL over NoSQL
- Ensures strict schema enforcement for health metrics

---

## 🧪 Failures & Learnings

### 1. Runtime Compatibility Issues
- Attempted deployment on Python 3.14
- Faced binary incompatibility with `psycopg2`

**Fix**
- Standardized runtime to Python 3.12  
- Learned importance of stable production environments  

---

### 2. Database Transaction Conflicts
- Encountered `ActiveSqlTransaction` errors during index creation

**Fix**
- Implemented autocommit-based migration strategy  

---

### 3. Connection Instability
- Cloud database (Neon) closed idle SSL connections

**Fix**
- Added keep-alive checks in connection pooling logic  

---

## 🖥️ Demo

https://github.com/user-attachments/assets/ac735568-f229-4e5f-9258-6516b63720c2

- AI interpreting Fitbit metrics and suggesting actionable insights  
- Real-time food logging via Telegram interface  



---

## 🚀 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/ShivabasavaM/Metabolic-Health-Coach.git
cd Metabolic-Health-Coach
```

### 2. Environment Setup

Create a .env file:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=your_neon_url
GOOGLE_API_KEY=your_gemini_key
FITBIT_CLIENT_ID=your_id
FITBIT_CLIENT_SECRET=your_secret
```

### 3. Run with Docker (Recommended)
```
docker build -t metabolic-coach .
docker run -p 8080:8080 --env-file .env metabolic-coach
```

### 4. Local Setup (Alternative)
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 telegram_bot.py
```

## 🛠️ Tech Stack
- LLM & Agent Framework: Gemini, LangChain, LangGraph
- Backend: FastAPI, Python
- Database: PostgreSQL (Neon)
- Integration: Fitbit API, Telegram Bot
- Infra: Docker

## 📌 Future Improvements
- Add monitoring for agent decision flows
- Optimize latency in state retrieval
- Introduce personalized model fine-tuning
- Improve long-term health trend analysis
