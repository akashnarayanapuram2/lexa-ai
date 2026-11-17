"""
Phase 7: Agentic Workflow
Three agents using Gemini API:
1. ClauseAnalysisAgent — classifies and structures clauses
2. RiskAnalysisAgent  — deep risk assessment per clause
3. ReportAgent        — generates executive contract summary
"""

from core.classifier import classify_clause_with_ai, classify_clause_heuristic
from core.risk_analyzer import assess_risk_with_ai, detect_risk_heuristic
from rag.rag_engine import get_rag_engine


class ClauseAnalysisAgent:
    """
    Agent 1: Analyzes and classifies each clause.
    Uses AI classification with heuristic fallback.
    """

    def __init__(self, gemini_client):
        self.client = gemini_client
        self.name = "Clause Analysis Agent"

    def run(self, clauses: list[dict], use_ai: bool = True) -> list[dict]:
        """Classify all clauses and return enriched list."""
        enriched = []
        for clause in clauses:
            if use_ai and len(clause["text"]) > 100:
                clause_type = classify_clause_with_ai(clause["text"], self.client)
            else:
                clause_type = classify_clause_heuristic(clause["text"])

            enriched.append({
                **clause,
                "type": clause_type,
                "agent": self.name,
            })
        return enriched


class RiskAnalysisAgent:
    """
    Agent 2: Performs deep risk assessment for each clause.
    Uses RAG context + Gemini for grounded explanations.
    """

    def __init__(self, gemini_client):
        self.client = gemini_client
        self.rag = get_rag_engine()
        self.name = "Risk Analysis Agent"

    def run(self, clauses: list[dict], use_ai: bool = True) -> list[dict]:
        """Assess risk for all clauses and return enriched list."""
        assessed = []
        for clause in clauses:
            clause_type = clause.get("type", "General / Other")

            if use_ai and len(clause["text"]) > 80:
                # Get RAG context for this clause type
                rag_query = f"{clause_type} clause risks legal contract"
                rag_context = self.rag.get_relevant_context(rag_query, top_k=2)
                risk_data = assess_risk_with_ai(
                    clause["text"], clause_type, rag_context, self.client
                )
            else:
                h = detect_risk_heuristic(clause["text"])
                risk_data = {
                    "level": h["level"],
                    "score": h["score"],
                    "explanation": "Heuristic analysis applied.",
                    "review_points": ["Review with a legal professional."],
                }

            assessed.append({
                **clause,
                "risk_level": risk_data["level"],
                "risk_score": risk_data["score"],
                "explanation": risk_data["explanation"],
                "review_points": risk_data["review_points"],
                "risk_agent": self.name,
            })
        return assessed


class ReportAgent:
    """
    Agent 3: Generates executive summary and contract overview.
    """

    def __init__(self, gemini_client):
        self.client = gemini_client
        self.name = "Report Agent"

    def generate_summary(self, contract_text: str, analyzed_clauses: list[dict]) -> dict:
        """Generate structured contract summary."""
        # Build risk stats
        risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for c in analyzed_clauses:
            level = c.get("risk_level", "Low")
            if level in risk_counts:
                risk_counts[level] += 1

        avg_score = (
            sum(c.get("risk_score", 0) for c in analyzed_clauses) / len(analyzed_clauses)
            if analyzed_clauses else 0
        )

        clause_types = list({c.get("type", "General") for c in analyzed_clauses})

        prompt = f"""You are a senior legal analyst. Generate a concise executive summary of this contract.

CONTRACT TEXT (excerpt):
{contract_text[:3000]}

ANALYSIS STATS:
- Total clauses: {len(analyzed_clauses)}
- Critical risks: {risk_counts['Critical']}
- High risks: {risk_counts['High']}
- Medium risks: {risk_counts['Medium']}
- Low risks: {risk_counts['Low']}
- Average risk score: {avg_score:.1f}/100
- Clause types found: {', '.join(clause_types)}

Write the summary in this EXACT format:

CONTRACT_TYPE: [type of contract, e.g., Software License Agreement]
PARTIES: [parties involved if determinable, else "Not specified"]
OVERALL_RISK: [Low/Medium/High/Critical]
KEY_FINDINGS:
- [finding 1]
- [finding 2]
- [finding 3]
RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]
- [recommendation 3]
DISCLAIMER: This analysis is for informational purposes only and does not constitute professional legal advice.
"""
        try:
            response = self.client.chat.complete(
                model="gemini-3.5-flash-lite",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            return _parse_summary(content, risk_counts, avg_score)
        except Exception as e:
            return {
                "contract_type": "Unknown",
                "parties": "Not specified",
                "overall_risk": "Unknown",
                "key_findings": ["Analysis incomplete due to API error."],
                "recommendations": ["Retry analysis or consult a legal professional."],
                "risk_counts": risk_counts,
                "avg_score": avg_score,
            }


def _parse_summary(text: str, risk_counts: dict, avg_score: float) -> dict:
    result = {
        "contract_type": "Legal Agreement",
        "parties": "Not specified",
        "overall_risk": "Medium",
        "key_findings": [],
        "recommendations": [],
        "risk_counts": risk_counts,
        "avg_score": avg_score,
    }
    lines = text.split('\n')
    mode = None
    for line in lines:
        line = line.strip()
        if line.startswith("CONTRACT_TYPE:"):
            result["contract_type"] = line.split(":", 1)[1].strip()
        elif line.startswith("PARTIES:"):
            result["parties"] = line.split(":", 1)[1].strip()
        elif line.startswith("OVERALL_RISK:"):
            val = line.split(":", 1)[1].strip()
            for lvl in ["Critical", "High", "Medium", "Low"]:
                if lvl.lower() in val.lower():
                    result["overall_risk"] = lvl
                    break
        elif line.startswith("KEY_FINDINGS:"):
            mode = "findings"
        elif line.startswith("RECOMMENDATIONS:"):
            mode = "recs"
        elif line.startswith("DISCLAIMER"):
            mode = None
        elif line.startswith("-") and mode == "findings":
            result["key_findings"].append(line.lstrip("- ").strip())
        elif line.startswith("-") and mode == "recs":
            result["recommendations"].append(line.lstrip("- ").strip())
    return result
