from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text(
    file_path: str,
    content_type: str,
) -> str:

    if content_type == "application/pdf":
        return extract_pdf_text(file_path)

    if content_type == "text/plain":
        return extract_txt_text(file_path)

    if content_type == (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ):
        return extract_docx_text(file_path)

    raise ValueError(
        f"Unsupported document type: {content_type}"
    )


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_txt_text(file_path: str) -> str:
    return Path(file_path).read_text(
        encoding="utf-8"
    )


def extract_docx_text(file_path: str) -> str:
    document = DocxDocument(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)