"""
Phase 2 — Legal RAG + Urdu Challan Generator
Standalone deployable Flask service (Render / Railway) replacing the
Colab + ngrok bridge (notebook Cell 13).

Exposes the exact two routes ragConnector.js (Phase 3 Node backend) expects:
  POST /retrieve        {violation_type} -> {law_section, fine_amount, law_description}
  POST /generate-urdu   {violation_type, law_section, fine_amount, law_description} -> {urdu_text}
  GET  /health          -> {status: ok}

NOTE ON THE FINE-TUNED MODEL:
Your notebook's Qwen2 + QLoRA fine-tuned model (Cell 6/7) needs a GPU and
several GB of RAM, which Render/Railway free/hobby tiers don't provide.
Your own notebook already has a clean fallback for exactly this case
(USE_FINETUNED = False -> Groq). This deployment uses that Groq path only,
so it runs fine on a small, cheap web instance.
"""

import os
import re
from datetime import datetime

from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

from traffic_laws import TRAFFIC_LAWS

# ── Config (from environment, NEVER hardcoded) ───────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY environment variable is not set. "
        "Set it in your Render/Railway dashboard (see README)."
    )

VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "./vectordb")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

app = Flask(__name__)

# ── Load embedding model + vector DB (once, at startup) ──────────────
print("Loading multilingual embedding model...")
embedder = SentenceTransformer("intfloat/multilingual-e5-small")
print("Embedder loaded.")

chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
collection = chroma_client.get_or_create_collection(
    name="pakistan_traffic_laws",
    metadata={"hnsw:space": "cosine"},
)

groq_client = Groq(api_key=GROQ_API_KEY)


def _law_to_chunks(law: dict) -> list:
    base_id = law["violation"].replace(" ", "_").lower()
    return [
        {
            "id": f"{base_id}_main",
            "text": f"{law['section']}. Violation: {law['violation']}. {law['description']}",
            "metadata": {
                "violation": law["violation"],
                "section": law["section"],
                "fine_pkr": law["fine_pkr"],
                "fine_usd": law["fine_usd"],
                "points": law["points"],
                "authority": law["authority"],
                "urdu_violation": law["urdu_violation"],
                "urdu_law": law["urdu_law"],
                "repeat_offence": law["repeat_offence"],
                "chunk_type": "main",
            },
        },
        {
            "id": f"{base_id}_urdu",
            "text": f"خلاف ورزی: {law['urdu_violation']}. {law['urdu_law']}. جرمانہ: {law['fine_pkr']} روپے",
            "metadata": {
                "violation": law["violation"],
                "section": law["section"],
                "fine_pkr": law["fine_pkr"],
                "fine_usd": law["fine_usd"],
                "points": law["points"],
                "authority": law["authority"],
                "urdu_violation": law["urdu_violation"],
                "urdu_law": law["urdu_law"],
                "repeat_offence": law["repeat_offence"],
                "chunk_type": "urdu",
            },
        },
        {
            "id": f"{base_id}_fine",
            "text": f"Fine for {law['violation']}: PKR {law['fine_pkr']}. Demerit points: {law['points']}. Repeat: {law['repeat_offence']}",
            "metadata": {
                "violation": law["violation"],
                "section": law["section"],
                "fine_pkr": law["fine_pkr"],
                "fine_usd": law["fine_usd"],
                "points": law["points"],
                "authority": law["authority"],
                "urdu_violation": law["urdu_violation"],
                "urdu_law": law["urdu_law"],
                "repeat_offence": law["repeat_offence"],
                "chunk_type": "fine",
            },
        },
    ]


def ensure_vector_db_seeded():
    """Populate ChromaDB from TRAFFIC_LAWS on first boot only."""
    if collection.count() > 0:
        print(f"Vector DB already seeded ({collection.count()} chunks).")
        return

    print("Vector DB empty — seeding Pakistani traffic laws...")
    all_ids, all_texts, all_meta = [], [], []
    for law in TRAFFIC_LAWS:
        for chunk in _law_to_chunks(law):
            all_ids.append(chunk["id"])
            all_texts.append(chunk["text"])
            all_meta.append(chunk["metadata"])

    embeddings = embedder.encode(all_texts, show_progress_bar=False).tolist()
    collection.upsert(ids=all_ids, documents=all_texts, embeddings=embeddings, metadatas=all_meta)
    print(f"Vector DB ready ({collection.count()} chunks).")


ensure_vector_db_seeded()


# ── RAG retrieval ──────────────────────────────────────────────────
def retrieve_law(violation_type: str, top_k: int = 3) -> list:
    query = f"traffic violation {violation_type} fine penalty law Pakistan"
    query_emb = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=top_k, where={"chunk_type": "main"})
    laws = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        laws.append({"text": doc, "metadata": meta})
    return laws


# ── Urdu report generation (Groq only — see module docstring) ───────
def _has_digits(text: str) -> bool:
    return bool(re.search(r"[0-9\u06F0-\u06F9]", text))


def _is_clean_urdu(text: str) -> bool:
    """Reject the narrative if ANY character falls outside Urdu script,
    whitespace, or basic punctuation. A ratio-based check would only
    compare Urdu vs Latin letter counts, silently letting other scripts
    (e.g. the model leaking a Chinese translation of its own instructions)
    slip through undetected. This checks the whole string, not just a ratio."""
    if not text:
        return False
    stripped = re.sub(
        r'[\u0600-\u06FF\u0750-\u077F\s\u060C\u061B\u061F\u06D4.,:;!?"\'()\-]',
        "",
        text,
    )
    return len(stripped) == 0


def _default_narrative(urdu_violation: str, violation: str, urdu_law: str) -> str:
    return (
        urdu_law
        or f"یہ خلاف ورزی ({urdu_violation or violation}) پاکستانی ٹریفک قوانین کے تحت قابل جرمانہ ہے "
        f"اور ڈرائیور کی حفاظت کے لیے اس قانون کی پاسداری لازمی ہے۔"
    )


def _get_model_narrative(violation: str, urdu_violation: str) -> str:
    urdu_prompt = f"""آپ ایک سرکاری پاکستانی ٹریفک ای چالان سسٹم ہیں۔

خلاف ورزی: {urdu_violation or violation}

صرف ایک مختصر، رسمی اردو جملہ لکھیں جو بتائے کہ یہ خلاف ورزی کیوں قابلِ جرمانہ ہے۔

اہم ہدایات:
- صرف اردو رسم الخط استعمال کریں، کوئی انگریزی لفظ نہ ہو۔
- جواب میں کوئی ہندسہ (نمبر)، گاڑی نمبر، تاریخ، یا دفعہ نمبر شامل نہ کریں — صرف وضاحتی جملہ۔
- کوئی اضافی وضاحت یا سرخی شامل نہ کریں، صرف وہ ایک جملہ دیں۔"""
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": urdu_prompt}],
            temperature=0.3,
            max_tokens=120,
        )
        narrative = response.choices[0].message.content.strip()
    except Exception:
        narrative = ""

    if not narrative or not _is_clean_urdu(narrative) or _has_digits(narrative):
        return ""
    return narrative


def generate_urdu_challan_report(
    violation: str,
    plate: str,
    section: str,
    fine_pkr,
    location: str = "N/A",
    urdu_violation: str = "",
    urdu_law: str = "",
) -> str:
    """Critical fields (plate, fine, date, section, location) are always
    injected from arguments into a fixed template — the model only supplies
    a short, validated, number-free narrative sentence."""
    today_human = datetime.now().strftime("%d %B %Y")
    clean_location = (location or "N/A").replace(",", "").strip()

    narrative = _get_model_narrative(violation, urdu_violation)
    if not narrative:
        narrative = _default_narrative(urdu_violation, violation, urdu_law)

    return f"""ای چالان رپورٹ
تاریخ: {today_human}
مقام: {clean_location}

گاڑی نمبر: {plate}
خلاف ورزی: {urdu_violation or violation}
قانونی دفعہ: {section}
جرمانہ: {fine_pkr} روپے

{narrative}

جرمانہ فوری ادا کریں۔
ٹریفک آفیسر"""


# ── Routes (contract expected by ragConnector.js — unchanged) ────────
@app.route("/retrieve", methods=["POST"])
def retrieve():
    data = request.get_json(force=True)
    violation_type = data.get("violation_type", "")

    laws = retrieve_law(violation_type)
    if not laws:
        return jsonify(
            {
                "law_section": "Unknown",
                "fine_amount": 0,
                "law_description": "No matching law found — manual review required.",
            }
        )

    primary = laws[0]
    meta = primary["metadata"]
    return jsonify(
        {
            "law_section": meta.get("section", "Unknown"),
            "fine_amount": meta.get("fine_pkr", 0),
            "law_description": primary.get("text", ""),
        }
    )


@app.route("/generate-urdu", methods=["POST"])
def generate_urdu():
    data = request.get_json(force=True)
    violation_type = data.get("violation_type", "")
    law_section = data.get("law_section", "Unknown")
    fine_amount = data.get("fine_amount", 0)
    # ragConnector.js does not send plate_number/location (see notebook Cell 12
    # note) — Phase 3 stores those separately in MongoDB.
    urdu_report = generate_urdu_challan_report(
        violation=violation_type,
        plate="N/A",
        section=law_section,
        fine_pkr=fine_amount,
        location="N/A",
    )
    return jsonify({"urdu_text": urdu_report})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "chunks_in_db": collection.count()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
