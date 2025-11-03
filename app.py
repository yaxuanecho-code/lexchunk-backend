
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
from textacy.extract import token_matches

# ensure model availability
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

app = FastAPI(title="Lexical Chunk Backend", version="1.0.0")

# CORS: allow all origins by default (you can tighten this later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Inp(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chunks")
def extract_chunks(inp: Inp):
    doc = nlp(inp.text)
    results = []

    # 1) noun chunks (spaCy built-in)
    for np in doc.noun_chunks:
        results.append({
            "type": "noun_chunk",
            "phrase": np.text,
            "start": np.start_char,
            "end": np.end_char,
            "sentence": np.sent.text,
        })

    # 2) verb/multiword expressions (Textacy token_matches)
    patterns = [
        # phrasal verbs: VERB + PART/ADV (e.g., give up, take off)
        [{"POS": "VERB"}, {"POS": {"IN": ["PART", "ADV"]}}],
        # classic multiword expressions / idioms (examples)
        [{"LOWER": "take"}, {"LOWER": "care"}, {"LOWER": "of"}],
        [{"LOWER": "as"}, {"LOWER": "a"}, {"LOWER": "matter"}, {"LOWER": "of"}, {"LOWER": "fact"}],
        [{"LOWER": "on"}, {"LOWER": "the"}, {"LOWER": "other"}, {"LOWER": "hand"}],
        [{"LOWER": "as"}, {"LOWER": "a"}, {"LOWER": "result"}, {"LOWER": "of"}],
    ]
    for span in token_matches(doc, patterns=patterns):
        results.append({
            "type": "verb_chunk",
            "phrase": span.text,
            "start": span.start_char,
            "end": span.end_char,
            "sentence": span.sent.text,
        })

    return {"collocations": results}
