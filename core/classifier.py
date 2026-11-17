"""
Phase 3: Clause Classification
Uses keyword heuristics as a fast pre-classifier,
then Gemini API for nuanced classification.
"""

import re

CLAUSE_TYPES = [
    "Termination",
    "Payment",
    "Confidentiality",
    "Liability",
    "Indemnity",
    "Non-Compete",
    "Intellectual Property",
    "Renewal",
    "Dispute Resolution",
    "Governing Law",
    "Force Majeure",
    "Warranty",
    "Assignment",
    "Amendment",
    "Definitions",
    "General / Other",
]

# Keyword-based pre-classifier for speed
KEYWORD_MAP = {
    "Termination": ["terminat", "cancel", "end of agreement", "expir", "notice of termination"],
    "Payment": ["payment", "invoice", "fee", "price", "compensation", "remunerat", "salary", "billing"],
    "Confidentiality": ["confidential", "non-disclosure", "nda", "proprietary", "secret", "trade secret"],
    "Liability": ["liabilit", "liable", "damages", "limitation of liability", "cap on liability"],
    "Indemnity": ["indemni", "hold harmless", "defend", "indemnification"],
    "Non-Compete": ["non-compete", "non compete", "restraint of trade", "not compete", "competing business"],
    "Intellectual Property": ["intellectual property", "copyright", "patent", "trademark", "ip rights", "ownership of work"],
    "Renewal": ["renew", "auto-renew", "extension", "rollover", "successive term"],
    "Dispute Resolution": ["arbitrat", "mediat", "dispute", "litigation", "jurisdiction"],
    "Governing Law": ["governing law", "applicable law", "jurisdiction", "venue", "choice of law"],
    "Force Majeure": ["force majeure", "act of god", "unforeseeable", "pandemic", "natural disaster"],
    "Warranty": ["warrant", "represent", "guarantee", "as-is", "fitness for purpose"],
    "Assignment": ["assign", "transfer", "delegate", "novation"],
    "Amendment": ["amend", "modif", "variation", "change to this agreement"],
    "Definitions": ["means", "defined as", "definition", "\"the company\"", "\"the client\""],
}


def classify_clause_heuristic(clause_text: str) -> str:
    """Fast keyword-based classification."""
    text_lower = clause_text.lower()
    scores = {}
    for ctype, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[ctype] = score
    if not scores:
        return "General / Other"
    return max(scores, key=scores.get)


def classify_clause_with_ai(clause_text: str, client) -> str:
    """Use Gemini API for accurate classification."""
    types_str = ", ".join(CLAUSE_TYPES)
    prompt = f"""You are a legal contract analyst. Classify the following contract clause into exactly ONE of these categories:
{types_str}

Respond with ONLY the category name, nothing else.

CLAUSE:
{clause_text[:1500]}
"""
    try:
        response = client.chat.complete(
            model="gemini-3.5-flash-lite",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()
        # Validate it's a known type
        for ct in CLAUSE_TYPES:
            if ct.lower() in result.lower():
                return ct
        return classify_clause_heuristic(clause_text)
    except Exception:
        return classify_clause_heuristic(clause_text)
