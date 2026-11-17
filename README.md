# ⚖ LexAI — AI-Powered Legal Contract Analyzer

> **Final-Year GenAI Project** · Clause Extraction · Risk Scoring · RAG · Agentic Workflow · Google Gemini API

---

## 🚀 Quick Start

### 1. Clone / Copy the Project
```bash
cd legal_analyzer
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Your Google Gemini API Key
```bash
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```
Get your free API key at: https://aistudio.google.com/

### 5. Run the App
```bash
streamlit run app.py
```
Open http://localhost:8501

---

## 🗂 Project Structure

```
legal_analyzer/
├── app.py                      # Main Streamlit application (UI + orchestration)
│
├── core/
│   ├── extractor.py            # Phase 1–2: PDF/DOCX text extraction & clause splitting
│   ├── classifier.py           # Phase 3: Clause type classification
│   └── risk_analyzer.py        # Phase 4–5: Risk detection & scoring (0–100)
│
├── rag/
│   └── rag_engine.py           # Phase 6: FAISS + Sentence Transformers RAG engine
│
├── agents/
│   └── agents.py               # Phase 7: Three AI agents (Clause, Risk, Report)
│
├── reports/
│   └── report_generator.py     # Phase 8: ReportLab PDF report generator
│
├── knowledge_base/
│   └── legal_knowledge.txt     # Legal knowledge base (RAG source documents)
│
├── sample_contract.txt         # Test contract with intentional risk patterns
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📐 Architecture & Development Phases

```
Phase 1: Upload & Text Extraction
   PDF → PyMuPDF (fitz)  |  DOCX → python-docx
         ↓
Phase 2: Clause Splitting
   Regex-based section detection with paragraph fallback
         ↓
Phase 3: Clause Classification (Agent 1 — ClauseAnalysisAgent)
   Google Gemini API + keyword heuristic fallback
   Types: Termination, Payment, Confidentiality, Liability, Indemnity,
          Non-Compete, IP, Renewal, Dispute Resolution, Governing Law...
         ↓
Phase 4: Risk Detection
   Pattern matching for Critical/High/Medium/Low indicators
         ↓
Phase 5: Risk Scoring (Agent 2 — RiskAnalysisAgent)
   Google Gemini API + RAG context → Risk Level + Score (0–100) + Explanation
         ↓
Phase 6: RAG with Legal Knowledge Base
   FAISS index · Sentence Transformers (all-MiniLM-L6-v2)
   Retrieves relevant legal best-practices to ground AI explanations
         ↓
Phase 7: Contract Summary (Agent 3 — ReportAgent)
   Overall risk, key findings, recommendations
         ↓
Phase 8: Results UI + Risk Highlighting + Q&A + PDF Report
   Streamlit frontend with full color-coded clause cards
```

---

## 🤖 AI Agents

| Agent | Role | Model |
|-------|------|-------|
| **ClauseAnalysisAgent** | Classifies each clause into 15+ legal categories | gemini-3.5-flash-lite |
| **RiskAnalysisAgent** | Deep risk assessment with RAG-grounded explanations | gemini-3.5-flash-lite |
| **ReportAgent** | Generates executive summary & recommendations | gemini-3.5-flash-lite |

---

## 🎨 Features

- **Risk Score 0–100** with color-coded progress bars
- **4-tier risk system**: Critical (🔴) · High (🟠) · Medium (🟡) · Low (🟢)
- **RAG Q&A**: Ask anything about your contract in natural language
- **PDF Report**: Professional downloadable analysis report
- **Filter & Sort**: View clauses by risk level or score
- **Heuristic Fallback**: Works even if AI API is slow (keyword-based mode)

---

## 🧪 Testing

Use the included `sample_contract.txt` — it's designed with intentionally risky clauses:
- Unlimited liability cap ($1.00)
- Non-refundable, unilateral fee increases
- 5-year worldwide non-compete
- Perpetual confidentiality
- Immediate termination without notice

Convert it to PDF using any word processor, or test with any real contract PDF.

---

## 🔧 Debugging

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in the venv |
| PDF extraction empty | Ensure PDF is text-based (not scanned image) |
| Slow first run | sentence-transformers downloads model (~90MB) on first use |
| API rate limit | Enable "Heuristic mode" toggle in sidebar |
| No clauses detected | Contract may be <500 chars; try a longer document |
| FAISS error on Windows | Install `faiss-cpu` not `faiss` |

---

## ⚖ Disclaimer

This system provides **informational analysis only** and does not constitute professional legal advice.
Always consult a qualified attorney before making legal decisions based on this analysis.
