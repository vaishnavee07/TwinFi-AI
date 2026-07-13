# 🚀 TwinFi AI

> **An AI-Powered Living Financial Twin for Personalized Financial Intelligence**

TwinFi AI is an intelligent financial wellness platform that creates a **Living Financial Twin**—a dynamic digital representation of a user's financial health. By combining AI-driven insights, financial behavior analysis, and future simulations, TwinFi AI helps users make smarter financial decisions through personalized recommendations and predictive analytics.

---

## 📌 Problem Statement

Traditional banking applications mainly provide transaction history and account balances. They rarely help users understand:

- How financially healthy they are.
- How current spending affects future goals.
- Where money is leaking unnecessarily.
- How economic changes impact their finances.
- What actions they should take to improve their financial future.

As a result, users receive information but very little intelligent financial guidance.

---

# 💡 Solution

TwinFi AI transforms traditional banking into an intelligent financial assistant by creating a **Living Financial Twin**.

The platform continuously analyzes a user's financial profile to:

- Evaluate financial health
- Understand spending behavior
- Simulate future financial outcomes
- Detect financial risks
- Recommend personalized improvements
- Explain insights through an AI Financial Coach

Instead of simply displaying financial data, TwinFi AI helps users understand and improve their financial future.

---

# ✨ Key Features

## 🧬 Living Financial Twin
Creates a dynamic digital representation of the user's complete financial profile, including net worth, savings, financial health, and future projections.

---

## 🧠 Financial DNA

Analyzes behavioral financial patterns such as:

- Spending habits
- Saving behavior
- Risk tolerance
- Investment preference
- Financial discipline

to generate a personalized Financial DNA profile.

---

## 🤖 AI Financial Coach

Powered by the **Groq API**, the AI Coach explains financial metrics, answers user questions, and provides personalized recommendations based on backend-calculated financial insights.

---

## 📈 Future Financial Simulator

Allows users to simulate different financial scenarios and visualize how changes in income, savings, expenses, or investments influence long-term financial outcomes.

---

## 🌍 Economy Simulator

Models the effect of macroeconomic events such as:

- Inflation
- Interest rate changes
- Market volatility

to demonstrate their impact on the user's financial position.

---

## 🛡 Fraud Intelligence

Monitors transaction patterns to identify suspicious financial activities and highlight potential fraud risks.

---

## 💡 AI Insights

Generates proactive financial recommendations such as:

- Reduce unnecessary subscriptions
- Improve savings rate
- Optimize investments
- Increase emergency funds
- Improve Financial Health Score

---

## 👨‍💼 Relationship Manager Dashboard

Provides financial advisors with a centralized dashboard to monitor customer financial health, identify risks, and deliver personalized recommendations.

---

# 🏗 System Architecture

```
                 ┌───────────────────────────┐
                 │       Mobile App          │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │      FastAPI Backend      │
                 └─────────────┬─────────────┘
                               │
        ┌───────────────┬───────────────┐
        │               │               │
   SQLite DB      AI Engines      Groq API
        │               │               │
        └───────────────┴───────────────┘
                     Financial Insights
```

---

# 🛠 Tech Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Chart.js

---

## Backend

- Python
- FastAPI
- SQLAlchemy

---

## Database

- SQLite

---

## Artificial Intelligence

- Groq API
- Financial Analysis Engine
- Rule-Based Recommendation Engine
- Financial DNA Engine

---

# 📂 Project Structure

```
TwinFi_AI
│
├── assets/
│   ├── css/
│   └── js/
│
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── mobile/
├── desktop/
├── rm/
│
├── screenshots/
│
├── README.md
└── LICENSE
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/vaishnavee07/TwinFi-AI.git

cd TwinFi-AI
```

---

## Backend Setup

```bash
cd backend

python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Copy

```
.env.example
```

to

```
.env
```

and configure:

```
GROQ_API_KEY=
SECRET_KEY=
```

---

## Run Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```
http://localhost:8000
```

Swagger API:

```
http://localhost:8000/docs
```

---

## Run Frontend

From the project root:

```bash
python -m http.server 3000
```

Open:

```
http://localhost:3000/mobile/splash.html
```

---

# 📷 Screenshots

Add screenshots of:

- Mobile Dashboard
- Financial DNA
- Living Financial Twin
- Future Simulator
- AI Coach
- Desktop Dashboard
- RM Dashboard

inside the `screenshots/` folder.

---

# 🗺 Future Enhancements

- Open Banking Integration
- Account Aggregator Support
- Multi-language AI Coach
- Voice Assistant
- Investment Portfolio Optimization
- Credit Score Prediction
- Tax Planning Assistant
- Insurance Recommendation Engine

---

# 📄 License

Licensed under the MIT License.
