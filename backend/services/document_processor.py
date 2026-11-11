"""Extract text from uploaded documents (txt, pdf, docx)."""

from pathlib import Path
import io


def extract_text_from_file(file_path: str, content_type: str = None) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt" or (content_type and "text/plain" in content_type):
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf" or (content_type and "pdf" in content_type):
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    if suffix in (".docx", ".doc") or (content_type and "word" in content_type):
        try:
            from docx import Document
            doc = Document(str(path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            return f"[DOCX extraction error: {e}]"

    # Fallback: try as text
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "[Unsupported or unreadable file format]"


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    """Helper when we have bytes instead of a saved path."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return data.decode("utf-8", errors="ignore")

    # Write temp and reuse
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return extract_text_from_file(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
