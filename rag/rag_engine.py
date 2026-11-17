"""
Phase 6: RAG Engine using FAISS + Sentence Transformers + Gemini
Grounds explanations with legal knowledge base.
"""

import os
import pickle
import numpy as np
from pathlib import Path

# Lazy imports (heavy)
_faiss = None
_SentenceTransformer = None


def _get_faiss():
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


def _get_st():
    global _SentenceTransformer
    if _SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer
        _SentenceTransformer = SentenceTransformer
    return _SentenceTransformer


KB_PATH = Path(__file__).parent.parent / "knowledge_base" / "legal_knowledge.txt"
INDEX_CACHE = Path(__file__).parent.parent / "knowledge_base" / "faiss_index.pkl"


def _load_knowledge_base() -> list[str]:
    """Split knowledge base into chunks."""
    with open(KB_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    # Split on double newlines, keep sections together
    chunks = [c.strip() for c in text.split('\n\n') if len(c.strip()) > 60]
    return chunks


def build_index(chunks: list[str], model) -> tuple:
    """Build FAISS index from text chunks."""
    faiss = _get_faiss()
    embeddings = model.encode(chunks, show_progress_bar=False)
    embeddings = np.array(embeddings).astype('float32')
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, embeddings


class RAGEngine:
    def __init__(self):
        self.chunks = _load_knowledge_base()
        self.model = None
        self.index = None
        self._initialized = False

    def initialize(self):
        """Lazy-initialize embeddings and FAISS index."""
        if self._initialized:
            return
        ST = _get_st()
        self.model = ST('all-MiniLM-L6-v2')

        # Try loading cached index
        if INDEX_CACHE.exists():
            try:
                with open(INDEX_CACHE, 'rb') as f:
                    cached = pickle.load(f)
                    if cached.get('chunks') == self.chunks:
                        self.index = cached['index']
                        self._initialized = True
                        return
            except Exception:
                pass

        self.index, _ = build_index(self.chunks, self.model)
        try:
            with open(INDEX_CACHE, 'wb') as f:
                pickle.dump({'index': self.index, 'chunks': self.chunks}, f)
        except Exception:
            pass
        self._initialized = True

    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve top-k relevant chunks for a query."""
        self.initialize()
        faiss = _get_faiss()
        query_emb = self.model.encode([query]).astype('float32')
        top_k = max(1, min(int(top_k), len(self.chunks)))
        distances, indices = self.index.search(query_emb, top_k)
        retrieved = [self.chunks[i] for i in indices[0] if 0 <= i < len(self.chunks)]
        return "\n\n".join(retrieved)

    def answer_question(self, question: str, contract_text: str, gemini_client) -> str:
        """Answer a user question about the contract using RAG."""
        self.initialize()
        # Get legal knowledge context
        legal_context = self.get_relevant_context(question, top_k=3)
        # Truncate contract to avoid token limits
        contract_snippet = contract_text[:4000]

        prompt = f"""You are an expert legal document analyst. Answer the user's question about the uploaded contract.

RELEVANT LEGAL KNOWLEDGE:
{legal_context}

CONTRACT TEXT (excerpt):
{contract_snippet}

USER QUESTION: {question}

Provide a clear, accurate answer based on the contract content. If the contract does not contain information relevant to the question, say so clearly.
Always remind the user: This is informational analysis only, not professional legal advice.
"""
        try:
            response = gemini_client.chat.complete(
                model="gemini-3.5-flash-lite",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"


# Singleton
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
