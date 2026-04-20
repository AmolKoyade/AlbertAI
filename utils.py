import base64
import io
import streamlit as st
import docx
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader

# FIX: Reject files above this size before processing to prevent app freezes
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _check_file_size(uploaded_file) -> bool:
    """Returns True if file is within the allowed size limit."""
    uploaded_file.seek(0, 2)        # Seek to end to measure size
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)           # Reset back to start
    if file_size > MAX_FILE_SIZE_BYTES:
        st.warning(
            f"⚠️ File is too large ({file_size // (1024 * 1024)} MB). "
            f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )
        return False
    return True


def extract_text(uploaded_file) -> str:
    """Extract plain text from an uploaded PDF or DOCX file."""
    text = ""

    if not uploaded_file or not hasattr(uploaded_file, "type"):
        return text

    # FIX 1: Guard against oversized files before attempting to read
    if not _check_file_size(uploaded_file):
        return text

    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        elif "officedocument.wordprocessingml.document" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        # FIX 2: Surface file read errors instead of silently returning ""
        st.warning(f"⚠️ Could not read file: {e}")

    return text


def encode_image(uploaded_file):
    """Resize and base64-encode an uploaded image for API submission."""

    # FIX 3: Guard against oversized images
    if not _check_file_size(uploaded_file):
        return None

    try:
        img = Image.open(uploaded_file)
        img.thumbnail((1024, 1024))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        # FIX 4: Handle corrupted or unsupported image formats gracefully
        st.warning(f"⚠️ Could not process image: {e}")
        return None


def get_web_context(query: str) -> str:
    """Fetch a brief web summary for the query using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except Exception as e:
        # FIX 5: Was a bare `except: return ""` — now surfaces the actual error
        # so network issues, rate limits, and API changes are visible during debugging
        st.warning(f"⚠️ Web search unavailable: {e}")
        return ""