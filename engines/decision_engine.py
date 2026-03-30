from __future__ import annotations


class DecisionEngine:
    SCENARIO_FACTORS = {
        "alone": {"income_multiplier": 1.0, "fixed_cost_multiplier": 1.0, "risk_bonus": 0.12},
        "roommates": {"income_multiplier": 1.0, "fixed_cost_multiplier": 0.8, "risk_bonus": -0.1},
        "family": {"income_multiplier": 1.25, "fixed_cost_multiplier": 1.35, "risk_bonus": 0.24},
    }

    def evaluate(
        self,
        salary: float,
        rent: float,
        scenario: str,
        debt_payment: float = 0.0,
        effective_tax: float | None = None,
        city_costs: dict | None = None,
    ) -> dict:
        factors = self.SCENARIO_FACTORS.get(scenario, self.SCENARIO_FACTORS["alone"])
        city_costs = city_costs or {}
        if effective_tax is None:
            effective_tax = city_costs.get("tax_model", {}).get("effective_income_tax_rate", 0.24)

        monthly_net = ((salary * factors["income_multiplier"]) / 12.0) * (1 - effective_tax)
        baseline_cost = (
            city_costs.get("groceries", 450)
            + city_costs.get("utilities", 220)
            + city_costs.get("transport", 350)
            + city_costs.get("insurance", 170)
            + city_costs.get("healthcare_baseline", 330)
        )
        fixed_cost = baseline_cost * factors["fixed_cost_multiplier"]
        residual = monthly_net - rent - fixed_cost - debt_payment
        rent_ratio = rent / max(monthly_net, 1)
        survivability_months = max(0.0, residual / max(rent * 0.35, 1))
        risk_score = min(1.0, max(0.0, rent_ratio * 0.75 + (debt_payment / max(monthly_net, 1)) * 0.4 + factors["risk_bonus"]))
        stability = "stable" if risk_score < 0.35 and residual > 600 else "fragile" if risk_score < 0.65 and residual >= 0 else "unstable"
        affordability = "affordable" if rent_ratio < 0.33 and residual > 300 else "stretched" if residual >= 0 else "not_affordable"
        return {
            "monthly_net": round(monthly_net, 2),
            "post_rent_cash": round(residual, 2),
            "rent_ratio": round(rent_ratio, 3),
            "survivability_months": round(survivability_months, 2),
            "risk_score": round(risk_score, 3),
            "stability": stability,
            "affordability": affordability,
            "scenario": scenario,
            "debt_payment": round(debt_payment, 2),
            "effective_tax": round(effective_tax, 3),
            "baseline_cost": round(fixed_cost, 2),
        }
