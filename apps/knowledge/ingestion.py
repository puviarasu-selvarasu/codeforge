import os
import json
import hashlib
from pathlib import Path
from django.conf import settings
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

_chunks = []
_vectorizer = None
_vectors = None
_index_path = settings.BASE_DIR / 'tfidf_index.json'

def load_index():
    global _chunks, _vectorizer, _vectors
    if _index_path.exists():
        try:
            with open(_index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _chunks = data.get('chunks', [])
            if _chunks:
                texts = [c['text'] for c in _chunks]
                _vectorizer = TfidfVectorizer(stop_words='english')
                _vectors = _vectorizer.fit_transform(texts)
            else:
                _vectorizer = None
                _vectors = None
            logger.info(f"Loaded {len(_chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            _chunks = []
            _vectorizer = None
            _vectors = None
    else:
        _chunks = []
        _vectorizer = None
        _vectors = None

def save_index():
    data = {'chunks': _chunks}
    with open(_index_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def rebuild_vectorizer():
    global _vectorizer, _vectors
    if not _chunks:
        _vectorizer = None
        _vectors = None
        return
    texts = [c['text'] for c in _chunks]
    _vectorizer = TfidfVectorizer(stop_words='english')
    _vectors = _vectorizer.fit_transform(texts)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.md', '.py', '.json']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == '.pdf':
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return ''.join([page.extract_text() or '' for page in reader.pages])
    elif ext == '.docx':
        import docx
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    return ''

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def index_file(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        return
    text = extract_text(file_path)
    if not text:
        return
    chunks = chunk_text(text)
    if not chunks:
        return
    source = str(file_path.relative_to(settings.KNOWLEDGE_ROOT))
    global _chunks
    _chunks = [c for c in _chunks if c['source'] != source]
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{source}_{i}".encode()).hexdigest()
        _chunks.append({'id': chunk_id, 'text': chunk, 'source': source})
    rebuild_vectorizer()
    save_index()
    logger.info(f"Indexed {len(chunks)} chunks from {source}")

def index_all_files():
    knowledge_root = settings.KNOWLEDGE_ROOT
    if not knowledge_root.exists():
        return
    global _chunks
    _chunks = []
    for root, dirs, files in os.walk(knowledge_root):
        for file in files:
            if file.startswith('.'):
                continue
            index_file(Path(root) / file)
    save_index()

load_index()