# TwinFi AI

TwinFi AI is the world's first **Living Financial Twin**. It is an enterprise-grade AI banking platform that creates a dynamic, learning digital replica of a user's financial life.

## Problem Statement

Traditional banking apps provide static, backward-looking financial data. Users see what they *have spent*, but rarely understand what they *should do*. Managing finances across accounts, understanding complex loan impacts, planning for goals, and predicting future financial health is overwhelming and fragmented.

## Solution

TwinFi AI solves this by ingesting real-time financial data to build a "Living Financial Twin". This AI twin learns your financial behavior, models your financial DNA, simulates potential futures, and proactively recommends the next best actions. It transforms banking from a passive dashboard into an active, predictive financial coach.

## Key Features

- **Living Financial Twin**: A real-time, holographic digital replica representing your overall financial health, net worth, and risk.
- **Financial DNA**: Deep behavioral profiling (Spender vs Saver, Risk Tolerance, Emotional Spending) derived from transaction history.
- **AI Financial Coach**: Powered by Groq, an ultra-low latency AI coach that acts as a personalized fiduciary advisor.
- **Future Simulator**: Time-travel with your finances. Move sliders to see how today's decisions impact your net worth 10 years from now.
- **Economy Simulator**: Test your twin's resilience against macroeconomic shocks like RBI repo rate hikes, inflation spikes, or market crashes.
- **Fraud Intelligence**: Real-time anomaly detection and location-based fraud mapping using ensemble AI models.
- **AI Insights**: Actionable, proactive alerts (e.g., "Plug ₹22K leakage in unused subscriptions", "Refinance loan now to save ₹1.2L").
- **Relationship Manager Dashboard**: A premium desktop view for wealth managers to monitor their clients' twins in real-time.

## Tech Stack

### Frontend
- **HTML5 / CSS3 / Vanilla JS**: High-performance, lightweight UI with a bespoke premium dark-glassmorphism design system.
- **Chart.js**: Dynamic charting for cash flow, future simulations, and portfolio tracking.

### Backend
- **Python / FastAPI**: High-performance asynchronous REST API.
- **SQLAlchemy**: ORM for database interactions.

### Database
- **SQLite**: Local, lightweight relational database (for prototype portability).

### AI & LLM
- **Groq API**: Lightning-fast inference for the AI Financial Coach.
- **Scikit-Learn (Concepts)**: Transaction categorization and anomaly detection logic.

## Architecture Overview

TwinFi AI uses a decoupled architecture:
1. **Frontend**: Pure static HTML/JS files served by any static web server. It uses `api-client.js` to communicate with the backend.
2. **Backend**: A FastAPI application that provides REST endpoints for DNA, Twin State, Goals, Insights, and AI Coaching.
3. **Demo Mode**: The application includes a self-contained `DEMO_MODE` that injects realistic mock data into the UI, ensuring seamless hackathon presentations even without live database connections.

## Project Folder Structure

```
TwinFi_AI/
│
├── backend/                  # FastAPI Application
│   ├── app/                  # Application Logic (API, Services, Models)
│   ├── tests/                # Pytest Suite
│   ├── .env.example          # Environment Variables Template
│   └── requirements.txt      # Python Dependencies
│
├── mobile/                   # Mobile-first Web App Interfaces
├── desktop/                  # Premium Desktop Dashboard Interfaces
├── assets/                   # Shared CSS and JS (api-client.js)
├── screenshots/              # Project Screenshots
└── README.md                 # Project Documentation
```

## Installation Guide

### Prerequisites
- Python 3.9+
- Groq API Key (for AI Coach)

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the example environment file and add your Groq API Key:
```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### 3. Start Backend Server
```bash
uvicorn app.main:app --reload
# Backend will be available at http://localhost:8000
```

### 4. Start Frontend
Open a new terminal window in the root directory (`TwinFi_AI`):
```bash
python -m http.server 3000
```
Navigate to `http://localhost:3000/mobile/splash.html` in your browser.

## Screenshots

*(Add screenshots here)*
See the `/screenshots` folder for UI examples.

## Future Roadmap

- **OpenBanking API Integration**: Connect live bank accounts via Account Aggregators (AA).
- **Advanced Predictive ML**: Implement deep learning models for precise transaction categorization.
- **Multi-Agent Architecture**: Deploy specialized AI agents for Tax, Real Estate, and Equity advice.
- **Push Notifications**: Proactive mobile alerts for fraud and budget thresholds.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributors

Built with ❤️ for the AI Hackathon.
