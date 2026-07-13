/**
 * TwinFi AI — Frontend API Client
 * ===============================
 * Handles all backend API connections for the TwinFi AI prototype.
 * Uses fetchWithRetry for stability. Falls back to DEMO_MODE if backend is down.
 */

// Hackathon Demo Mode Flag
const DEMO_MODE = true;

const API_BASE = 'https://twinfi-ai-backend.onrender.com/api/v1';

// Token storage key
const TOKEN_KEY = 'twinfi_access_token';
const REFRESH_KEY = 'twinfi_refresh_token';
const USER_KEY = 'twinfi_user_profile';

class TwinFiAPIClient {
  constructor() {
    this.useMock = DEMO_MODE;
    this.checkBackendConnection();
  }

  async checkBackendConnection() {
    if (DEMO_MODE) {
      this.useMock = true;
      return;
    }
    try {
      const res = await fetch('https://twinfi-ai-backend.onrender.com/health', { method: 'GET', mode: 'cors' });
      if (res.ok) {
        this.useMock = false;
      } else {
        throw new Error('Backend not healthy');
      }
    } catch (e) {
      console.warn('⚠️ TwinFi Backend unreachable. Falling back to frontend mock mode.');
      this.useMock = true;
    }
  }

  // Headers helper
  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  // Resilient fetch with retry
  async fetchWithRetry(url, options = {}, retries = 2) {
    if (this.useMock) return null;
    
    for (let i = 0; i <= retries; i++) {
      try {
        const res = await fetch(url, options);
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `HTTP Error ${res.status}`);
        }
        return res;
      } catch (err) {
        if (i === retries) {
          console.warn(`Failed to fetch ${url} after ${retries} retries.`, err);
          throw err;
        }
        // Wait before retrying (exponential backoff)
        await new Promise(r => setTimeout(r, 500 * (i + 1)));
      }
    }
  }

  // Auth Operations
  async login(email, password) {
    if (this.useMock) {
      await new Promise(r => setTimeout(r, 800));
      if (email && password) {
        localStorage.setItem(TOKEN_KEY, 'mock-jwt-token-xyz');
        localStorage.setItem(USER_KEY, JSON.stringify({ email, first_name: 'Arjun', last_name: 'Sharma', role: 'customer' }));
        return { success: true, user: { email, first_name: 'Arjun' } };
      }
      throw new Error('Invalid credentials');
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      }, 1);
      const data = await res.json();
      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(REFRESH_KEY, data.refresh_token);
      return { success: true };
    } catch (e) {
      console.warn('Login API failed, falling back to local demo mode.', e);
      this.useMock = true;
      return this.login(email, password);
    }
  }

  async signup(profileData) {
    if (this.useMock) {
      await new Promise(r => setTimeout(r, 1200));
      localStorage.setItem(TOKEN_KEY, 'mock-jwt-token-xyz');
      localStorage.setItem(USER_KEY, JSON.stringify({
        email: profileData.email,
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        role: 'customer'
      }));
      return { success: true };
    }

    try {
      await this.fetchWithRetry(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      }, 1);
      return { success: true };
    } catch (e) {
      console.warn('Signup API failed, falling back to local demo mode.', e);
      this.useMock = true;
      return this.signup(profileData);
    }
  }

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = 'login.html';
  }

  // Financial DNA
  async getDNA() {
    // Check local cache
    const cached = localStorage.getItem('twinfi_dna_cache');
    if (cached) return JSON.parse(cached);

    if (this.useMock) {
      const demoData = {
        overall_score: 84,
        scores: {
          saving_dna: 92,
          investment_dna: 78,
          risk_dna: 55,
          lifestyle_dna: 63,
          impulse_index: 28,
          discipline_score: 88
        },
        personality_type: "The Strategic Planner",
        confidence: 0.93,
        version: 47
      };
      localStorage.setItem('twinfi_dna_cache', JSON.stringify(demoData));
      return demoData;
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/dna/`, { headers: this.getHeaders() });
      const body = await res.json();
      localStorage.setItem('twinfi_dna_cache', JSON.stringify(body.data));
      return body.data;
    } catch (e) {
      console.warn('DNA fetch failed, falling back to demo mode.');
      this.useMock = true;
      return this.getDNA();
    }
  }

  // Living Financial Twin State
  async getTwinState() {
    const cached = localStorage.getItem('twinfi_twin_cache');
    if (cached) return JSON.parse(cached);

    if (this.useMock) {
      const demoData = {
        health_score: 87,
        net_worth: 1627500,
        monthly_income: 120000,
        monthly_expenses: 64000,
        monthly_savings: 56000,
        savings_rate_pct: 46.7,
        debt_to_income_ratio: 0.20,
        emergency_fund_months: 4.8,
        predictions: {
          net_worth_12m: 2100000,
          net_worth_5y: 5800000,
          retirement_age_current_path: 58
        }
      };
      localStorage.setItem('twinfi_twin_cache', JSON.stringify(demoData));
      return demoData;
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/twin/`, { headers: this.getHeaders() });
      const body = await res.json();
      localStorage.setItem('twinfi_twin_cache', JSON.stringify(body.twin));
      return body.twin;
    } catch (e) {
      console.warn('Twin state fetch failed, falling back to demo mode.');
      this.useMock = true;
      return this.getTwinState();
    }
  }

  // AI Financial Coach Chat
  async sendCoachMessage(message, sessionId, history = []) {
    if (this.useMock) {
      await new Promise(r => setTimeout(r, 1000));
      return {
        reply: `Based on your pre-calculated financial health score of 87/100, you are doing great! I recommend increasing your monthly SIP by ₹5,000 to reach your ₹50 Lakh retirement goal 3 years earlier.`,
        powered_by: "Groq AI (Demo Mode)"
      };
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/coach/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          message,
          session_id: sessionId,
          conversation_history: history
        })
      }, 1);
      return await res.json();
    } catch (e) {
      console.warn('AI Coach unreachable, falling back to demo response.');
      return {
        reply: "AI service is temporarily unavailable. Using locally available financial analysis: Your financial health score is 87/100. Consider reviewing your recent OTT subscriptions for potential savings.",
        powered_by: "Local Fallback"
      };
    }
  }

  // Proactive Insights
  async getInsights() {
    if (this.useMock) {
      return [
        {
          id: "ins_001",
          type: "saving_opportunity",
          icon: "💡",
          priority: "high",
          title: "Subscription Consolidation Opportunity",
          message: "Your OTT subscriptions total ₹1,847/month. Consolidating them can save you ₹22,164 annually.",
          action_label: "View Leakage",
          action_url: "leakage.html",
          potential_saving: 22164
        },
        {
          id: "ins_002",
          type: "investment_alert",
          icon: "📈",
          priority: "medium",
          title: "SIP Increase Recommended",
          message: "Increasing your monthly SIP by ₹5,000 can bring your retirement forward by 3 years.",
          action_label: "Increase SIP",
          action_url: "investments.html"
        }
      ];
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/coach/insights`, { headers: this.getHeaders() });
      const body = await res.json();
      return body.insights;
    } catch (e) {
      console.warn('Failed to get insights, falling back to demo mode.');
      this.useMock = true;
      return this.getInsights();
    }
  }

  // Transactions
  async getTransactions(page = 1, pageSize = 20) {
    if (this.useMock) {
      return {
        items: [
          { reference_number: 'TXN827364812', amount: 1500, transaction_type: 'debit', merchant_name: 'Swiggy', category: 'Food & Dining', transacted_at: new Date().toISOString(), status: 'completed', fraud_score: 0.12 },
          { reference_number: 'TXN827364813', amount: 45000, transaction_type: 'credit', merchant_name: 'IDBI Payroll', category: 'Salary', transacted_at: new Date().toISOString(), status: 'completed', fraud_score: 0.01 },
          { reference_number: 'TXN827364814', amount: 1847, transaction_type: 'debit', merchant_name: 'Netflix India', category: 'Entertainment', transacted_at: new Date().toISOString(), status: 'completed', fraud_score: 0.05 },
          { reference_number: 'TXN827364815', amount: 350, transaction_type: 'debit', merchant_name: 'Starbucks', category: 'Food & Dining', transacted_at: new Date(Date.now() - 86400000).toISOString(), status: 'completed', fraud_score: 0.02 },
          { reference_number: 'TXN827364816', amount: 12000, transaction_type: 'debit', merchant_name: 'LIC Premium', category: 'Insurance', transacted_at: new Date(Date.now() - 172800000).toISOString(), status: 'completed', fraud_score: 0.00 }
        ]
      };
    }

    try {
      const res = await this.fetchWithRetry(`${API_BASE}/transactions/?page=${page}&page_size=${pageSize}`, { headers: this.getHeaders() });
      return await res.json();
    } catch (e) {
      console.warn('Failed to get transactions, falling back to demo mode.');
      this.useMock = true;
      return this.getTransactions();
    }
  }
}

// Global instance
window.twinfiAPI = new TwinFiAPIClient();
