"""
Financial Calculation Engine — Twin Engine
==========================================
ALL calculations are performed here. Groq is never called for numbers.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TwinEngine:

    async def calculate_health_score(self, twin_data: Dict[str, Any]) -> int:
        """
        Calculates 0–100 Financial Health Score.
        Formula:
          - Savings rate (30%): savings/income
          - Debt-to-income ratio (25%): lower is better
          - Emergency fund (20%): months covered
          - Investment ratio (15%): investments/net_worth
          - Expense discipline (10%): actual vs planned
        """
        income = twin_data.get("monthly_income", 120000)
        savings = twin_data.get("monthly_savings", 56000)
        expenses = twin_data.get("monthly_expenses", 64000)
        total_debt = twin_data.get("total_debt", 1850000)
        emergency_fund_months = twin_data.get("emergency_fund_months", 4.8)
        investments = twin_data.get("total_investments", 1326000)
        net_worth = twin_data.get("net_worth", 1627500)

        # Component 1: Savings rate (target ≥ 20%)
        savings_rate = savings / income if income > 0 else 0
        savings_score = min(savings_rate / 0.20, 1.0) * 30

        # Component 2: Debt-to-income (target < 0.36)
        dti = (total_debt / 12) / income if income > 0 else 0
        dti_score = max(0, (1 - dti / 0.36)) * 25

        # Component 3: Emergency fund (target ≥ 6 months)
        ef_score = min(emergency_fund_months / 6.0, 1.0) * 20

        # Component 4: Investment ratio (target ≥ 30% of net worth)
        inv_ratio = investments / net_worth if net_worth > 0 else 0
        inv_score = min(inv_ratio / 0.30, 1.0) * 15

        # Component 5: Expense discipline (target: expenses ≤ 60% of income)
        exp_ratio = expenses / income if income > 0 else 1
        exp_score = max(0, (1 - (exp_ratio - 0.60) / 0.40)) * 10

        total = savings_score + dti_score + ef_score + inv_score + exp_score
        return min(100, round(total))

    async def calculate_emi(
        self,
        principal: float,
        annual_rate_pct: float,
        tenure_months: int,
    ) -> Dict[str, Any]:
        """
        Standard EMI calculation using reducing balance formula.
        EMI = P × r × (1+r)^n / ((1+r)^n - 1)
        """
        if annual_rate_pct <= 0:
            return {"emi": principal / tenure_months, "total_interest": 0, "total_amount": principal}

        monthly_rate = annual_rate_pct / (12 * 100)
        n = tenure_months
        emi = principal * monthly_rate * (1 + monthly_rate) ** n / ((1 + monthly_rate) ** n - 1)
        total_amount = emi * n
        total_interest = total_amount - principal

        return {
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_amount": round(total_amount, 2),
            "principal": principal,
            "annual_rate_pct": annual_rate_pct,
            "tenure_months": tenure_months,
        }

    async def calculate_savings_projection(
        self,
        monthly_savings: float,
        annual_return_pct: float,
        years: int,
        existing_corpus: float = 0,
    ) -> Dict[str, Any]:
        """
        Compound savings projection (SIP + lump sum).
        Uses FV formula: FV = P*(1+r)^n + PMT*((1+r)^n - 1)/r
        """
        r = annual_return_pct / 100
        n = years
        monthly_r = r / 12
        months = years * 12

        # Future value of existing corpus
        fv_lump = existing_corpus * (1 + r) ** n

        # Future value of monthly SIP (annuity)
        if monthly_r > 0:
            fv_sip = monthly_savings * ((1 + monthly_r) ** months - 1) / monthly_r
        else:
            fv_sip = monthly_savings * months

        total_fv = fv_lump + fv_sip
        total_invested = existing_corpus + (monthly_savings * months)

        return {
            "future_value": round(total_fv),
            "total_invested": round(total_invested),
            "total_returns": round(total_fv - total_invested),
            "return_multiple": round(total_fv / total_invested, 2) if total_invested > 0 else 0,
            "years": years,
            "annual_return_pct": annual_return_pct,
        }

    async def calculate_risk_score(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates portfolio risk score 0–100.
        Based on: equity exposure, volatility, concentration, liquidity.
        """
        portfolio = customer_data.get("portfolio", {})
        total = sum(portfolio.values()) if portfolio else 1

        # Equity exposure (mutual funds + stocks = higher risk)
        equity = portfolio.get("mutual_funds", 0) + portfolio.get("stocks", 0)
        equity_pct = equity / total if total > 0 else 0

        # Base risk from equity exposure
        risk_score = equity_pct * 60  # Max 60 pts from equity

        # Emergency fund penalty (low EF = higher risk)
        ef_months = customer_data.get("emergency_fund_months", 3)
        if ef_months < 3:
            risk_score += 25
        elif ef_months < 6:
            risk_score += 10

        # Debt penalty
        dti = customer_data.get("debt_to_income", 0.20)
        risk_score += min(dti * 50, 20)

        risk_score = min(100, round(risk_score))
        risk_label = (
            "Low" if risk_score < 35
            else "Moderate" if risk_score < 65
            else "High"
        )

        return {
            "risk_score": risk_score,
            "risk_label": risk_label,
            "equity_exposure_pct": round(equity_pct * 100, 1),
            "components": {
                "equity_exposure": round(equity_pct * 60),
                "emergency_fund_gap": 10 if ef_months < 6 else 0,
                "debt_burden": min(round(dti * 50), 20),
            },
        }

    async def calculate_money_leakage(self, transactions: list) -> Dict[str, Any]:
        """
        Identifies money leakage from transaction patterns.
        Leakage = subscriptions + impulse + high-fee + duplicate charges.
        """
        leakage_categories = {}
        total_leakage = 0.0

        # Simulate leakage analysis (production: real transaction data)
        detected = [
            {"category": "OTT Subscriptions", "monthly": 1847, "items": ["Netflix", "Hotstar", "Prime"]},
            {"category": "Unused Gym", "monthly": 2000, "items": ["Gold's Gym membership"]},
            {"category": "Impulse Food Delivery", "monthly": 3200, "items": ["Swiggy", "Zomato excess"]},
            {"category": "Bank Charges", "monthly": 500, "items": ["Minimum balance fee", "ATM charges"]},
        ]

        for item in detected:
            leakage_categories[item["category"]] = item
            total_leakage += item["monthly"]

        return {
            "total_monthly_leakage": round(total_leakage),
            "total_annual_leakage": round(total_leakage * 12),
            "leakage_breakdown": detected,
            "leakage_pct_of_income": round((total_leakage / 120000) * 100, 1),
        }

    async def simulate_future(
        self,
        base_data: Dict[str, Any],
        scenario: str = "current",
        adjustments: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Parallel future simulation engine.
        scenario: 'current' | 'optimized' | 'stress_test' | 'custom'
        """
        adj = adjustments or {}

        income = base_data.get("monthly_income", 120000)
        expenses = base_data.get("monthly_expenses", 64000)
        savings = income - expenses
        net_worth = base_data.get("net_worth", 1627500)

        # Apply scenario adjustments
        if scenario == "optimized":
            savings += adj.get("extra_sip", 5000)
            expenses -= adj.get("expense_cut", 3000)
        elif scenario == "stress_test":
            income *= (1 - adj.get("income_drop_pct", 0.20))
            expenses += adj.get("expense_increase", 5000)
        elif scenario == "custom":
            income += adj.get("income_change", 0)
            expenses += adj.get("expense_change", 0)
            savings = income - expenses

        # Project 5 years
        projections = await self.calculate_savings_projection(
            monthly_savings=max(savings, 0),
            annual_return_pct=adj.get("return_pct", 12.0),
            years=5,
            existing_corpus=net_worth,
        )

        # Estimate retirement age
        target_corpus = 50_000_000  # ₹5 Cr target
        current_age = base_data.get("age", 28)
        annual_savings = max(savings, 0) * 12
        if annual_savings > 0:
            years_to_retire = (target_corpus / projections["future_value"]) * 5
            retirement_age = round(current_age + years_to_retire)
        else:
            retirement_age = 65

        return {
            "scenario": scenario,
            "monthly_savings": round(savings),
            "5yr_projection": projections,
            "estimated_retirement_age": min(retirement_age, 65),
            "goal_achievement_pct": min(round(projections["future_value"] / target_corpus * 100), 100),
        }

    async def get_twin_state(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve the current twin state (demo data for local dev)."""
        base_data = {
            "monthly_income": 120000,
            "monthly_expenses": 64000,
            "monthly_savings": 56000,
            "net_worth": 1627500,
            "total_debt": 1850000,
            "emergency_fund_months": 4.8,
            "total_investments": 1326000,
            "debt_to_income": 0.20,
        }
        health_score = await self.calculate_health_score(base_data)
        predictions = await self.generate_predictions(base_data)
        return {**base_data, "health_score": health_score, "predictions": predictions}

    async def generate_predictions(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 12m and 5y net worth predictions."""
        monthly_savings = twin_data.get("monthly_savings", 56000)
        net_worth = twin_data.get("net_worth", 1627500)

        proj_12m = await self.calculate_savings_projection(monthly_savings, 12.0, 1, net_worth)
        proj_5y = await self.calculate_savings_projection(monthly_savings, 12.0, 5, net_worth)

        return {
            "net_worth_12m": proj_12m["future_value"],
            "net_worth_5y": proj_5y["future_value"],
            "retirement_age_current_path": 58,
        }
