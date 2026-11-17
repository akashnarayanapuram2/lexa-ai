"""
Phase 4 & 5: Risk Detection and Scoring
Detects risky/unusual clauses and assigns:
- Risk Level: Low / Medium / High / Critical
- Risk Score: 0–100
"""

import re

# High-risk language patterns
RISK_PATTERNS = {
    "Critical": [
        r"unlimited liability",
        r"waive[s]? all rights",
        r"irrevocable",
        r"in perpetuity",
        r"sole discretion",
        r"without notice",
        r"immediately terminat",
        r"forfeit",
        r"personal guarantee",
        r"unlimited indemnif",
    ],
    "High": [
        r"unilateral(ly)?",
        r"at any time",
        r"without cause",
        r"automatic renewal",
        r"worldwide",
        r"exclusive rights",
        r"assign without consent",
        r"waive[s]? any claim",
        r"non-refundable",
        r"liquidated damages",
        r"penalty",
        r"punitive",
    ],
    "Medium": [
        r"reasonable efforts",
        r"best efforts",
        r"material breach",
        r"60 days? notice",
        r"30 days? notice",
        r"cure period",
        r"right to audit",
        r"most favored nation",
        r"non-solicit",
    ],
    "Low": [
        r"standard terms",
        r"mutual agreement",
        r"written consent",
        r"prior notice",
    ],
}

RISK_SCORES = {
    "Critical": (80, 100),
    "High": (55, 79),
    "Medium": (25, 54),
    "Low": (1, 24),
    "None": (0, 0),
}


def detect_risk_heuristic(clause_text: str) -> dict:
    """
    Heuristic risk detection using pattern matching.
    Returns {level, score, matched_patterns}
    """
    text_lower = clause_text.lower()
    matched = {}

    for level, patterns in RISK_PATTERNS.items():
        hits = [p for p in patterns if re.search(p, text_lower)]
        if hits:
            matched[level] = hits

    if "Critical" in matched:
        level = "Critical"
        base = 85
    elif "High" in matched:
        level = "High"
        base = 60
    elif "Medium" in matched:
        level = "Medium"
        base = 35
    elif "Low" in matched:
        level = "Low"
        base = 12
    else:
        level = "Low"
        base = 5

    # Bump score for multiple hits
    total_hits = sum(len(v) for v in matched.values())
    bonus = min(total_hits * 3, 15)
    score = min(base + bonus, 100)

    return {
        "level": level,
        "score": score,
        "matched_patterns": matched,
    }


def assess_risk_with_ai(clause_text: str, clause_type: str, rag_context: str, client) -> dict:
    """
    Full AI-powered risk assessment using Gemini API + RAG context.
    Returns {level, score, explanation, review_points}
    """
    prompt = f"""You are an expert legal risk analyst. Analyze this contract clause for potential risks.

CLAUSE TYPE: {clause_type}

RELEVANT LEGAL KNOWLEDGE:
{rag_context}

CONTRACT CLAUSE:
{clause_text[:2000]}

Respond in this EXACT format (fill in each field):
RISK_LEVEL: [Low|Medium|High|Critical]
RISK_SCORE: [0-100 integer]
EXPLANATION: [2-3 sentences explaining why this clause may be concerning]
REVIEW_POINTS:
- [specific thing to review 1]
- [specific thing to review 2]
- [specific thing to review 3]

Be precise. Consider one-sided terms, missing protections, unusual scope, and ambiguous language.
Note: This is informational analysis only, not professional legal advice.
"""
    try:
        response = client.chat.complete(
            model="gemini-3.5-flash-lite",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        return _parse_risk_response(content)
    except Exception as e:
        # Fallback to heuristic
        h = detect_risk_heuristic(clause_text)
        return {
            "level": h["level"],
            "score": h["score"],
            "explanation": "AI analysis unavailable; heuristic risk detection applied.",
            "review_points": ["Review this clause with a qualified legal professional."],
        }


def _parse_risk_response(text: str) -> dict:
    """Parse structured AI response."""
    result = {
        "level": "Low",
        "score": 10,
        "explanation": "",
        "review_points": [],
    }

    lines = text.split('\n')
    review_mode = False
    review_pts = []

    for line in lines:
        line = line.strip()
        if line.startswith("RISK_LEVEL:"):
            val = line.split(":", 1)[1].strip()
            for lvl in ["Critical", "High", "Medium", "Low"]:
                if lvl.lower() in val.lower():
                    result["level"] = lvl
                    break
        elif line.startswith("RISK_SCORE:"):
            try:
                score_str = line.split(":", 1)[1].strip()
                result["score"] = max(0, min(100, int(re.search(r'\d+', score_str).group())))
            except Exception:
                pass
        elif line.startswith("EXPLANATION:"):
            result["explanation"] = line.split(":", 1)[1].strip()
            review_mode = False
        elif line.startswith("REVIEW_POINTS:"):
            review_mode = True
        elif review_mode and line.startswith("-"):
            pt = line.lstrip("- ").strip()
            if pt:
                review_pts.append(pt)

    result["review_points"] = review_pts or ["Review with a qualified attorney."]
    return result
