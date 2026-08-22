from typing import Literal


def calculator_tool(
    calculation_type: Literal["cancellation_fee", "service_credit_amount", "sla_breach_window", "credit_eligibility"],
    input_data: dict,
    applicable_agreement: str | None = None,
) -> dict:
    if calculation_type == "cancellation_fee":
        if applicable_agreement == "northstar":
            amount = 0.0
            formula = "Northstar Agreement section 4.2 waiver"
            source = "05_Northstar_Logistics_Enterprise_Agreement.pdf"
        else:
            amount = round(float(input_data["subtotal"]) * 0.25, 2)
            formula = "subtotal * 25% inside 60 minute window"
            source = "03_Cancellation_and_Service_Credit_SOP_v4.pdf"
        return {"eligible": amount == 0, "amount": amount, "formula_used": formula, "source_document": source, "confidence": "certain"}

    if calculation_type == "credit_eligibility":
        eligible = input_data.get("carrier_fault") and float(input_data.get("pickup_delay_hours", 0)) >= 2
        return {
            "eligible": bool(eligible),
            "formula_used": "carrier_fault and pickup_delay_hours >= 2",
            "source_document": "05_Northstar_Logistics_Enterprise_Agreement.pdf" if applicable_agreement == "northstar" else "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
            "confidence": "certain",
        }

    if calculation_type == "service_credit_amount":
        rate = 0.15 if applicable_agreement == "northstar" else 0.10
        amount = round(float(input_data["subtotal"]) * rate, 2)
        return {
            "amount": amount,
            "rate": rate,
            "formula_used": f"subtotal * {int(rate * 100)}%",
            "source_document": "05_Northstar_Logistics_Enterprise_Agreement.pdf" if applicable_agreement == "northstar" else "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
            "confidence": "certain",
        }

    if calculation_type == "sla_breach_window":
        remaining = max(float(input_data["sla_hours"]) - float(input_data["created_hours_ago"]), 0)
        return {"remaining_hours": remaining, "formula_used": "sla_hours - created_hours_ago", "source_document": "ticket snapshot", "confidence": "certain"}

    raise ValueError("unsupported calculation")
